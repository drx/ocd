from control_flow import control_flow_graph
from copy import copy, deepcopy
from itertools import count
import debug
import function_calls
import disassemblers.libdisassemble.opcode86 as opcode86
import re
import representation
import zlib

def is_constant(x):
    '''
    Test of the argument is a constant.
    '''
    return re.match("-?0x.*", x)

def is_register(x):
    '''
    Test if the argument is a register.
    '''
    registers = map(lambda x: x[0], opcode86.regs)
    return x in registers

def get_labels(functions):
    '''
    Find addresses that need to be labeled.
    '''
    labels = {}
    for function in functions:
        for ins in functions[function]:
            if ins['ins']['op'] == 'jump':
                addr = ins['loc']+ins['length']+ins['ins']['dest']['repr']
                labels[addr] = 'loc_{0:x}'.format(addr)

    return labels

def infer_signature(asm):
    '''
    Infer the signature of a function.
    '''
    return ('int', [])

def variable_inference(cfg):
    '''
    Infer the variables in code.

    Change all temporary variables (registers) into temp_0, temp_1, etc.
     and other variables into var_0, var_1, etc.
    '''
    def variable_inference_arg(arg):
        if 'op' in arg:
            variable_inference_ins(arg)
        elif arg['value'] in vars:
            arg.update(vars[arg['value']])
        else:
            if arg['w'] or arg['r']:
                if arg['r'] and is_constant(arg['value']):
                    type = 'const'
                    if arg['value'] == arg['repr']:
                        repr = int(arg['value'], 16)
                    else:
                        repr = arg['repr']
                elif is_register(arg['value']):
                    type = 'temp'
                    repr = temp_names.__next__()
                else:
                    type = 'var'
                    repr = var_names.__next__()
                info = {'type':type, 'repr':repr, 'value': arg['value']}
                vars[arg['value']] = info
                arg.update(info)

    def variable_inference_ins(ins):
        for k, arg in ins.items():
            if k == 'args':
                for a in arg:
                    variable_inference_arg(a)
            if k not in ('src', 'dest'):
                continue

            variable_inference_arg(ins[k])


    var_names = new_var_name()
    temp_names = new_temp_name()
    vars = {}

    for block, depth in cfg.iterblocks():
        for i, line in enumerate(block):
            variable_inference_ins(line['ins'])

    var_number_indicator =  var_names.__next__()
    m = re.match( "var_(.*)", var_number_indicator )
    return int(m.group(1))

def computation_collapse(cfg):
    '''
    Collapse the computation tree in the graph.

    For example, this code:

     a = 5
     b = a + 2
     c = b * 2

    would be converted to:

     c = (5+2)*2
    '''
    def is_writable(ins, k):
        '''
        Check if the argument is writable.
        '''
        return k in ins and 'w' in ins[k] and ins[k]['w']

    def is_temp_comp(ins, k):
        '''
        Check if the argument is a temporary.
        '''
        return k in ins and 'type' in ins[k] and ins[k]['type'] == 'temp'

    def lookup_vars(ins, mem):
        '''
        Lookup variables in memory.
        '''
        for k in ('src','dest'):
            if k in ins and 'op' in ins[k]:
                ins[k] = lookup_vars(ins[k], mem)
            elif k != 'dest' and k in ins and 'repr' in ins[k] and ins[k]['repr'] in mem:
                ins[k] = mem[ins[k]['repr']]
        if 'op' in ins and ins['op'] == 'apply':
            for i, arg in enumerate(ins['args']):
                ins['args'][i] = lookup_vars({'src': arg}, mem)['src']
        return ins

    def collapse_line(line, mem):
        '''
        Try to collapse a line.
        '''
        ins = line['ins']
        for k in ('dest',):
            if k in ins and is_writable(ins, k) and is_temp_comp(ins, k):
                key = ins[k]['repr']
                mem[key] = lookup_vars(deepcopy(ins), mem)
            line['ins'] = lookup_vars(ins, mem)
        
    def collapse_vertex(vertex, mem):
        '''
        Collapse a vertex of the cfg.
        '''
        t, v = vertex
        v_type, v_start = t

        if v_type == 'block':
            for line in v:
                collapse_line(line, mem)

        elif v_type == 'cons':
            for block in v:
                collapse_vertex(block, mem)

        elif v_type == 'if':
            cond, block = v
            collapse_vertex(block, deepcopy(mem))

        elif v_type == 'ifelse':
            cond, true, false = v
            for block in (true, false):
                collapse_vertex(block, deepcopy(mem))
        
        elif v_type == 'while':
            cond, pre, loop = v
            for block in (pre, loop):
                collapse_vertex(block, deepcopy(mem))

    for v in cfg.sortedvertices():
        collapse_vertex(v, {})

def cremate(cfg):
    '''
    Remove dead instructions.

    Specifically, traverse the code reverse inorder and:
     * record every read of a temporary variable
     * if you encounter a write to a temporary variable,
        erase it from the set
    
    This way record every necessary write to a temporary variable
     and remove the unnecessary ones.
    '''

    def get_read_arg(arg):
        if 'op' in arg:
            return get_read(arg)
        if arg['r'] and arg['type'] == 'temp':
            return {arg['repr']}

        return set()

    def get_read(ins):
        '''
        Get the set of variables read from in the instruction.
        '''
        r = set()
        if 'src' in ins:
            r |= get_read_arg(ins['src'])
        return r

    def get_written(ins):
        '''
        Get the set of variables written to in the instruction.
        '''
        w = set()
        if 'dest' in ins and ins['dest']['w'] and ins['dest']['type'] == 'temp':
            w |= {ins['dest']['repr']}
        return w

    def variable_declarations(cfg):
        '''
        Finds information about used variables and adds the declarations for them.
        '''

    def consume_block(block, reads_in):
        '''
        Try to consume lines in a block of code.
        '''
        reads = deepcopy(reads_in)
        t, v = block
        v_type, v_start = t

        if v_type == 'if':
            cond, true = v
            return consume_block(true, reads)

        if v_type == 'while':
            cond, pre, loop = v
            reads = consume_block(loop, reads)
            return consume_block(pre, reads)

        if v_type == 'cons':
            for b in reversed(v):
                reads = consume_block(b, reads)

            return reads

        if v_type == 'ifelse':
            cond, true, false = v
            reads_true = consume_block(true, reads)
            reads_false = consume_block(false, reads)
            return reads_true | reads_false

        for line in reversed(block[1]):
            w = get_written(line['ins'])
            r = get_read(line['ins'])
            if w <= reads:
                pass
            else:
                line['display'] = False
            reads -= w
            reads |= r

        return reads
        
    vars = set()
    for vertex in list(cfg.sortedvertices()):
         vars |= consume_block(vertex, set())
   
    return vars

def new_var_name():
    '''
    Generator of new variable names.
    '''
    for n in count(0):
        yield "var_{0}".format(n)

def new_temp_name():
    '''
    Generator of new temporary variable names.
    '''
    for n in count(0):
        yield "temp_{0}".format(n)

def add_declarations(cfg, var_number, temps_used):
    to_declare = temps_used
    for i in range(0, var_number):
        to_declare |= set(["var_{0}".format(i)])
    
    #print(to_declare)
    
def decompile_function(asm, labels, name, symbols):
    '''
    Decompile a function.
    '''
    signature = infer_signature(asm)
   
    cfg = control_flow_graph(asm, labels, name)
    symbols_rev = {symbols[s]['start']: s for s in symbols}
    function_calls.fold(cfg, symbols_rev)

    var_number = variable_inference(cfg)
    computation_collapse(cfg)
    temps_used = cremate(cfg)
    add_declarations(cfg, var_number, temps_used)

    return cfg, signature

def decompile_functions(functions, symbols):
    '''
    Decompile all functions.
    '''
    labels = get_labels(functions)

    decompiled_functions = {}

    for name, symbol in functions.items():
        decompiled_functions[name] = decompile_function(functions[name], labels, name, symbols)
    
    return decompiled_functions 
