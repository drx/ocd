from debug import debug_sprint
from binascii import hexlify
from decompile_table import decompile_table
from control_flow import control_flow_graph
from itertools import izip, starmap, repeat
from copy import copy

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
    elif block_type == 'ifelse':
        condition, true, false = v
        return '{3}\n{4}if ({0})\n{4}{{\n{1}\n{4}}}\n{4}else\n{4}{{\n{2}\n{4}}}\n'.format(
            condition, decompile_vertex(true, indent.inc()), decompile_vertex(false, indent.inc()),
            '', indent.out())
    elif block_type == 'cons':
        out = ''
        for b in v:
            out += decompile_vertex(b, indent)
        return out
    return ''

def decompile_ins(ins, indent):
    opcode = ins['ins'][0]
    extra_lambda = None

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
            fmt = '// {env[instr]}'

        fmt = indent.out()+fmt

    fmt += debug_sprint('\t\t/* {env[loc]:x}: {env[length]} ({env[bin]}) {env[prefix]} */', 'misc')
    env = {
        'loc': ins['loc'],
        'length': ins['length'],
        'bin': hexlify(ins['bin']),
        'instr': ' '.join(ins['ins']),
        'ins': ins['ins'],
        'prefix': ins['prefix'],
    }
    extra = ''
    if extra_lambda:
        extra = extra_lambda(env)

    return fmt.format(i=ins['ins'], extra=extra, env=env)

def get_labels(functions):
    labels = {}
    for function in functions:
        for ins in functions[function]:
            if ins['ins'][0][0] == 'j': # all jumps and only them
                addr = ins['loc']+ins['length']+int(ins['ins'][1],16)
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

def decompile_function(asm, labels, name):
    signature = infer_signature(asm)
    pre, post = output_signature(signature, name)

    cfg = control_flow_graph(asm, labels, name)

    return pre + decompile(cfg) + post

def decompile_functions(functions, symbols):
    labels = get_labels(functions)
    functions = labelize_functions(functions, labels)

    output = ''
    for name, symbol in symbols.iteritems():
        output += decompile_function(functions[name], labels, name)
        output += '\n'

    return output
