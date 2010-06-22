from control_flow import control_flow_graph
from copy import copy
from decompile_table import conditions, condition_negs, decompile_table
from itertools import izip, starmap, repeat, count
from postprocessor import postprocessor
import debug
import libdisassemble.opcode86 as opcode86
import re
import copy

def find(f, seq):
    for item in seq:
        if f(item):
            return item
    raise LookupError

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
    return '\n'.join(map(decompile_vertex, sorted(cfg.vertices().iteritems(), lambda ((a,b),c), ((d,e),f): cmp(b,e))))

def decompile_vertex((t, v), indent=None):
    block_type, block_start = t
    if indent is None:
        indent = Indent(1)
    if block_type == 'block':
        return '\n'.join(starmap(decompile_ins_outer, izip(v, repeat(indent))))

    elif block_type == 'if':
        cond, block = v
        return '{indent}if ({cond})\n{indent}{{\n{block}\n{indent}}}\n'.format(
            cond=condition(cond), block=decompile_vertex(block, indent.inc()), indent=indent.out())

    elif block_type == 'ifelse':
        cond, true, false = v
        return '{indent}if ({cond})\n{indent}{{\n{true}\n{indent}}}\n{indent}else\n{indent}{{\n{false}\n{indent}}}\n'.format(
            cond=condition(cond), true=decompile_vertex(true, indent.inc()), false=decompile_vertex(false, indent.inc()),
            indent=indent.out())

    elif block_type == 'while':
        cond, pre, loop = v
        return '{indent}while ({cond})\n{indent}{{\n{loop}\n{pre}\n{indent}}}\n'.format(
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

def decompile_ins_outer(ins, indent):
    return decompile_ins(ins, indent, False)

def decompile_ins(ins, indent, inner):
    opcode = ins['ins']['op']
    extra_lambda = None

    # would be nice to find a nicer way to do this
    for k, arg in ins['ins'].iteritems():
        if k not in ('src', 'dest'):
            continue
        try:
            ins['ins'][k] = ins['ins'][k]['repr']
        except KeyError:
            try:
                ins['ins'][k] = ins['ins'][k]['value']
            except KeyError:
                pass
                #print "<KeyError>"
                #print ins['ins'][k] #hmm
        except TypeError:
            pass
            #print "<TypeError>"
            #print ins

    # special instructions
    if opcode[0] == '!':
        if opcode == '!label':
            fmt = '{i[1]}:'

    elif opcode[0] == 'j':
        return ''
        
    else:
        for k in ('src', 'dest'):
           if has_instruction_inside(ins, k):
               ins['ins'][k] = '(' + decompile_ins(ins['ins'][k], indent, True) + ')'
        try:
            i, lhs, rhs, extra_lambda = find(lambda t: t[0] == opcode, decompile_table)
            if inner:
                fmt = rhs
            else:
                fmt = indent.out() + lhs + rhs
        except LookupError:
            if inner:
                fmt = '/* {env[ins]} */'
            else:
                fmt = indent.out() + '// {env[ins]}'

    env = {
        'loc': ins['loc'],
        'length': ins['length'],
        'ins': ins['ins'],
    }

    if debug.check('misc'):
        from binascii import hexlify
        fmt += '\t\t/* {env[loc]:x}: {env[length]} ({env[bin]}) {env[prefix]} */'
        env['bin'] = hexlify(ins['debug']['binary'])
        env['prefix'] = ins['debug']['prefix']

    extra = ''
    if extra_lambda:
        extra = extra_lambda(env)

    return fmt.format(i=ins['ins'], extra=extra, env=env)

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

def labelize_functions(functions, labels):
    for name, function in functions.iteritems():
        f = []
        for ins in function:
#            if ins['loc'] in labels:
#                f.append({'prefix': '', 'bin': '', 'loc': ins['loc'], 'length': 0, 'ins': ['!label', labels[ins['loc']]]})
            f.append(ins)
                
        functions[name] = f

    return functions        

def is_register(x):
    registers = map(lambda (x,y,z): x, opcode86.regs)
    return x in registers

def variable_inference(asm):
    var_names = new_var_name()
    temp_names = new_temp_name()
    vars = {}

    for line, ins in enumerate(asm[:]):
        for k, arg in ins['ins'].iteritems():
            if k not in ('src', 'dest'):
                continue

            if arg['value'] in vars:
                asm[line]['ins'][k].update(vars[arg['value']])
            else:
                if arg['w'] or arg['r']:
                    if arg['r'] and is_constant(arg['value']):
                        type = 'const'
                        repr = int(arg['value'], 16)
                    elif is_register(arg['value']):
                        type = 'temp'
                        repr = temp_names.next()
                    else:
                        type = 'var'
                        repr = var_names.next()
                    info = {'type':type, 'repr':repr, 'value': arg['value']}
                    vars[arg['value']] = info
                    asm[line]['ins'][k].update(info)

    return asm

def has_field(ins, k):
    if type(ins) == dict and 'ins' in ins and k in ins['ins']:
        return True
    else:
        return False

def has_instruction_inside(ins, k):
    if has_field(ins, k) and type(ins['ins'][k]) == dict and 'ins' in ins['ins'][k]:
        return True
    else:
        return False

def is_writable(ins, k):
    if has_field(ins, k) and type(ins['ins'][k]) == dict and 'w' in ins['ins'][k] and ins['ins'][k]['w']:
        return True
    else:
        return False

def is_temp_comp(ins, k):
    if has_field(ins, k) and type(ins['ins'][k]) == dict and ins['ins'][k]['type'] == 'temp':
        return True
    else:
        return False

def computation_collapse(asm):
    mem = {}
    code = []

    def lookup_vars(ins, mem):
        for k in ('src', 'dest'):
            if has_instruction_inside(ins, k):
                ins['ins'][k] = lookup_vars(ins['ins'][k], mem)
            elif has_field(ins, k) and 'repr' in ins['ins'][k] and ins['ins'][k]['repr'] in mem:
                ins['ins'][k] = mem[ins['ins'][k]['repr']]
            else:
                continue #doesn't have the k field
        return ins

    for ins in copy.deepcopy(asm):
        for k in ('dest'):#here, in the future will appear a way to distinct writing to src/dest at the same time with different data
            if has_field(ins, k):
                if is_writable(ins, k) and is_temp_comp(ins, k): 
                    mem[ins['ins'][k]['repr']] = lookup_vars(ins, mem)
                else:
                    code.append(lookup_vars(ins, mem))
            else: #no dest field
                code.append(lookup_vars(ins, mem))

    return code

def new_var_name():
    for n in count(0):
        yield "var_{0}".format(n)

def new_temp_name():
    for n in count(0):
        yield "temp_{0}".format(n)

def decompile_function(asm, labels, name):
    signature = infer_signature(asm)
    pre, post = output_signature(signature, name)
    
    asm = variable_inference(asm)
    clp_asm = computation_collapse(asm)
    cfg = control_flow_graph(asm, labels, name)
    #cfg = control_flow_graph(clp_asm, labels, name)

    return pre + decompile(cfg) + post

def decompile_functions(functions, symbols):
    labels = get_labels(functions)
    rfunctions = labelize_functions(functions, labels)

    output = ''
    for name, symbol in symbols.iteritems():
        output += decompile_function(functions[name], labels, name)
        output += '\n'
    
    output = postprocessor(output) #comment for disable
    
    return output
