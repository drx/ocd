from control_flow import control_flow_graph
from copy import copy, deepcopy
from representation import conditions, condition_negs, representation
from itertools import starmap, repeat, count
from postprocessor import postprocessor
import copy
import debug
import function_calls
import libdisassemble.opcode86 as opcode86
import re
import zlib

class Indent():
    def __init__(self, level=0):
        self.level = level

    def inc(self):
        new = copy.copy(self)
        new.level += 1
        return new

    def out(self):
        return '\t'*self.level

def condition(cond, var='cmp'):
    if cond[0] == '!':
        cond = condition_negs[cond[1:]]
    return conditions[cond].format(cond=var)

def decompile(cfg):
    return '\n'.join(map(decompile_vertex, cfg.itervertices()))

def decompile_vertex(vertex, indent=None):
    t, v = vertex
    block_type, block_start = t
    if indent is None:
        indent = Indent(1)
    if block_type == 'block':
        return '\n'.join(starmap(decompile_line, zip(v, repeat(indent))))

    elif block_type == 'if':
        cond, block = v
        return '\n{indent}if ({cond})\n{indent}{{\n{block}\n{indent}}}\n'.format(
            cond=condition(cond), block=decompile_vertex(block, indent.inc()), indent=indent.out())

    elif block_type == 'ifelse':
        cond, true, false = v
        return '\n{indent}if ({cond})\n{indent}{{\n{true}\n{indent}}}\n{indent}else\n{indent}{{\n{false}\n{indent}}}\n'.format(
            cond=condition(cond), true=decompile_vertex(true, indent.inc()), false=decompile_vertex(false, indent.inc()),
            indent=indent.out())

    elif block_type == 'while':
        cond, pre, loop = v
        return '\n{indent}while ({cond})\n{indent}{{\n{loop}\n{pre}\n{indent}}}\n'.format(
            indent=indent.out(), cond=condition(cond),
            pre=decompile_vertex(pre, indent.inc()), loop=decompile_vertex(loop, indent.inc())
        )

    elif block_type == 'cons':
        out = ''
        for b in v:
            out += decompile_vertex(b, indent)
        return out

    return ''

def is_constant(x):
    return re.match("-?0x.*", x)

def repr_int(n):
    """
    Get the representation of an integer.
    
    The representation is chosen based on its Kolmogorov complexity,
     i.e. the repr r is chosen which has the minimal value
     len(zlib.compress(r))
    """
    reprs = [('{0}','{0}'), ('{0:x}', '0x{0:x}')]
    lengths = [len(zlib.compress(r[0].format(n).encode())) for r in reprs]
    return reprs[lengths.index(min(lengths))][1].format(n)

def decompile_line(line, indent):
    '''
    Decompile a line of code. A line contains an instruction and
     some metainformation about that instruction (its location,
     etc.)

    The pseudo-EBNF of lines is as follows:

     line = location, debug, instruction
     instruction = op, argument*
     argument = value, repr | instruction
    '''
    def decompile_ins(ins):
        '''
        Decompile an instruction. Instructions are trees, see
         the EBNF for decompile_line.
        '''
        repr = {}
        for k, arg in ins.items():
            if k not in ('src', 'dest'):
                continue

            if 'op' in ins[k]:
                lhs, rhs = decompile_ins(ins[k])
                repr[k] = '(' + rhs + ')'
            else:
                repr[k] = ins[k]['repr']

            if type(repr[k]) == int:
                repr[k] = repr_int(repr[k])

        if ins['op'] == 'apply':
            lhs = ''
            args = []
            for arg in ins['args']:
                if 'op' in arg:
                    lhs, rhs = decompile_ins(arg)
                    args.append(rhs)
                else:
                    args.append(arg['repr'])
            rhs = '{fun}({args})'.format(fun=ins['function'], args=', '.join(args))

        else:
            try:
                lhs, rhs = representation(ins['op'])
            except KeyError:
                return '', '/* Unsupported instruction: {ins} */'.format(ins=ins)
        return lhs.format(i=repr), rhs.format(i=repr)

    lhs, rhs = decompile_ins(line['ins'])
    line_repr = indent.out() + lhs + rhs
    if lhs+rhs != '':
        line_repr += ';'

    if not line['display']:
        line_repr = ''

    if debug.check('misc'):
        from binascii import hexlify
        line_repr += '\n{indent}{blue}/* {line} */{black}'.format(indent=indent.out(), line=line, blue='\033[94m', black='\033[0m')

    return line_repr

def get_labels(functions):
    labels = {}
    for function in functions:
        for ins in functions[function]:
            if ins['ins']['op'] == 'jump':
                addr = ins['loc']+ins['length']+ins['ins']['dest']['repr']
                labels[addr] = 'loc_{0:x}'.format(addr)

    return labels

def infer_signature(asm):
    return ('int', [])

def output_signature(signature, name):
    fun_type, args = signature

    def f(arg):
        i, type = arg
        return type + ' arg' + i

    pre = fun_type + ' ' + name + '(' + ', '.join(map(f, enumerate(args))) + ')\n{\n'
    post = '\n}'
    return pre, post

def is_register(x):
    registers = map(lambda x: x[0], opcode86.regs)
    return x in registers

def variable_inference(cfg):
    def variable_inference_arg(arg):
        if 'op' in arg:
            variable_inference_ins(arg)
        elif arg['value'] in vars:
            arg.update(vars[arg['value']])
        else:
            if arg['w'] or arg['r']:
                if arg['r'] and is_constant(arg['value']):
                    type = 'const'
                    repr = int(arg['value'], 16)
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


def computation_collapse(cfg):
    def is_writable(ins, k):
        return k in ins and 'w' in ins[k] and ins[k]['w']

    def is_temp_comp(ins, k):
        return k in ins and 'type' in ins[k] and ins[k]['type'] == 'temp'

    def lookup_vars(ins, mem):
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
        ins = line['ins']
        for k in ('dest',):
            if k in ins and is_writable(ins, k) and is_temp_comp(ins, k):
                key = ins[k]['repr']
                mem[key] = lookup_vars(copy.deepcopy(ins), mem)
            line['ins'] = lookup_vars(ins, mem)
        
    def collapse_vertex(vertex, mem):
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
            collapse_vertex(block, copy.deepcopy(mem))

        elif v_type == 'ifelse':
            cond, true, false = v
            for block in (true, false):
                collapse_vertex(block, copy.deepcopy(mem))
        
        elif v_type == 'while':
            cond, pre, loop = v
            for block in (pre, loop):
                collapse_vertex(block, copy.deepcopy(mem))

    for v in cfg.itervertices():
        collapse_vertex(v, {})

def cremate(cfg):
    """
    Remove dead instructions.

    Specifically, traverse the code reverse inorder and:
     * record every read of a temporary variable
     * if you encounter a write to a temporary variable,
        erase it from the set
    
    This way record every necessary write to a temporary variable
     and remove the unnecessary ones.
    """

    def get_read_arg(arg):
        if 'op' in arg:
            return get_read(arg)
        if arg['r'] and arg['type'] == 'temp':
            return {arg['repr']}

        return set()

    def get_read(ins):
        r = set()
        if 'src' in ins:
            r |= get_read_arg(ins['src'])
        return r

    def get_written(ins):
        w = set()
        if 'dest' in ins and ins['dest']['w'] and ins['dest']['type'] == 'temp':
            w |= {ins['dest']['repr']}
        return w

    def consume_block(block, reads_in):
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
        

    for vertex in list(cfg.itervertices()):
         consume_block(vertex, set())
        

def new_var_name():
    for n in count(0):
        yield "var_{0}".format(n)

def new_temp_name():
    for n in count(0):
        yield "temp_{0}".format(n)

def decompile_function(asm, labels, name, symbols):
    signature = infer_signature(asm)
    pre, post = output_signature(signature, name)
    
    cfg = control_flow_graph(asm, labels, name)

    symbols_rev = dict([(symbols[s]['start'], s) for s in symbols])
    function_calls.fold(cfg, symbols_rev)

    variable_inference(cfg)
    computation_collapse(cfg)
    cremate(cfg)

    return pre + decompile(cfg) + post

def decompile_functions(functions, symbols):
    labels = get_labels(functions)

    output = ''
    for name, symbol in symbols.items():
        output += decompile_function(functions[name], labels, name, symbols)
        output += '\n'
    
    #output = postprocessor(output) #comment for disable
    
    return '\n'.join([line for line in output.split('\n') if line.strip()])
