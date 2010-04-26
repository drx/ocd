from debug import debug
from binascii import hexlify
from decompile_table import decompile_table

def find(f, seq):
    for item in seq:
        if f(item):
            return item
    raise LookupError

def decompile(ins):
    try:
        i, fmt, extra_lambda = find(lambda t: t[0] == ins['ins'][0], decompile_table)
    except LookupError:
        fmt, extra_lambda = '// {env[instr]}', None

    fmt += debug('\t\t/* {env[loc]:x}: {env[length]} ({env[bin]}) */')
    env = {
        'loc': ins['loc'],
        'length': ins['length'],
        'bin': hexlify(ins['bin']),
        'instr': ' '.join(ins['ins']),
        'ins': ins['ins'],
    }
    extra = ''
    if extra_lambda:
        extra = extra_lambda(env)

    return '\t'+fmt.format(i=ins['ins'], extra=extra, env=env)

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

def decompile_function(asm, name):
    signature = infer_signature(asm)
    pre, post = output_signature(signature, name)
    return pre + '\n'.join(map(decompile, asm)) + post
