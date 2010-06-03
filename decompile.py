from control_flow import control_flow_graph
from copy import copy
from decompile_table import decompile_table
from itertools import izip, starmap, repeat, count
import debug
import libdisassemble.opcode86 as opcode86
import re

def find(f, seq):
    for item in seq:
        if f(item):
            return item
    raise LookupError

class Indent():
    def __init__(self, level=0):
        self.level = level

    def inc(self):
        new = copy(self)
        new.level += 1
        return new

    def out(self):
        return '\t'*self.level

def decompile(cfg):
    return '\n'.join(map(decompile_vertex, sorted(cfg.vertices().iteritems(), lambda ((a,b),c), ((d,e),f): cmp(b,e))))

def decompile_vertex((t, v), indent=None):
    block_type, block_start = t
    if indent is None:
        indent = Indent(1)
    if block_type == 'block':
        return '\n'.join(starmap(decompile_ins, izip(v, repeat(indent))))

    elif block_type == 'if':
        condition, block = v
        return '{indent}if ({cond})\n{indent}{{\n{block}\n{indent}}}\n'.format(
            cond=condition, block=decompile_vertex(block, indent.inc()), indent=indent.out())

    elif block_type == 'ifelse':
        condition, true, false = v
        return '{indent}if ({cond})\n{indent}{{\n{true}\n{indent}}}\n{indent}else\n{indent}{{\n{false}\n{indent}}}\n'.format(
            cond=condition, true=decompile_vertex(true, indent.inc()), false=decompile_vertex(false, indent.inc()),
            indent=indent.out())

    elif block_type == 'while':
        condition, pre, loop = v
        return '{indent}while ({cond})\n{indent}{{\n{loop}\n{pre}\n{indent}}}\n'.format(
            indent=indent.out(), cond=condition,
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

def decompile_ins(ins, indent):
    opcode = ins['ins']['op']
    extra_lambda = None

    # would be nice to find a nicer way to do this
    for k, arg in ins['ins'].iteritems():
        if k not in ('src', 'dest'):
            continue
        try:
            ins['ins'][k] = ins['ins'][k]['repr']
        except KeyError:
            pass

    # special instructions
    if opcode[0] == '!':
        if opcode == '!label':
            fmt = '{i[1]}:'

    elif opcode[0] == 'j':
        return ''
        
    else:
        try:
            i, fmt, extra_lambda = find(lambda t: t[0] == opcode, decompile_table)
        except LookupError:
            fmt = '// {env[ins]}'

        fmt = indent.out()+fmt

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

def variable_inference(asm, labels):
    var_names = new_var_name()
    temp_names = new_temp_name()
    vars = {}

    #TODO: copy asm
    for line, ins in enumerate(asm):
        for k, arg in ins['ins'].iteritems():
            if k not in ('src', 'dest'):
                continue

            if arg['value'] in vars:
                asm[line]['ins'][k] = vars[arg['value']]
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

def new_var_name():
    for n in count(0):
        yield "var_{0}".format(n)

def new_temp_name():
    for n in count(0):
        yield "temp_{0}".format(n)

def decompile_function(asm, labels, name):
    signature = infer_signature(asm)
    pre, post = output_signature(signature, name)
    
    asm = variable_inference(asm, labels)
    cfg = control_flow_graph(asm, labels, name)

    return pre + decompile(cfg) + post

def decompile_functions(functions, symbols):
    labels = get_labels(functions)
    rfunctions = labelize_functions(functions, labels)

    output = ''
    for name, symbol in symbols.iteritems():
        output += decompile_function(functions[name], labels, name)
        output += '\n'

    return output
