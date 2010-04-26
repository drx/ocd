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
        i, fmt = find(lambda t: t[0] == ins['ins'][0], decompile_table)
    except LookupError:
        fmt = '// {instr}'

    fmt += debug('\t\t/* {loc:x}: {length} ({bin}) */')
    return fmt.format(i=ins['ins'], loc=ins['loc'], length=ins['length'], bin=hexlify(ins['bin']), instr=' '.join(ins['ins']))

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
