decompile_table = [
('dec', '{i[1]}--;'),
('mov', '{i[1]} = {i[2]};'),
]

def find(f, seq):
    for item in seq:
        if f(item):
            return item
    raise LookupError

def decompile(ins):
    try:
        i, fmt = find(lambda t: t[0] == ins[0], decompile_table)
        return fmt.format(i=ins)
    except LookupError:
        return '//' + ' '.join(ins)

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
