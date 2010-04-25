decompile_table = [
('aaa', 'BCD_AAA();'),
('aad', 'BCD_AAD();'),
('aam', 'BCD_AAM();'),
('aas', 'BCD_AAS();'),
('adc', '{i[1]} += {i[2]} + {cf};'),
('add', '{i[1]} += {i[2]};'),
('addpd', '{i[1]} = _mm_add_pd({i[1]},{i[2]});'),
('addps', '{i[1]} = _mm_add_ps({i[1]},{i[2]});'),
('addsd', '{i[1]} = _mm_add_sd({i[1]},{i[2]});'),
('addss', '{i[1]} = _mm_add_ss({i[1]},{i[2]});'),
('addsubpd', '{i[1]} = _mm_addsub_pd({i[1]},{i[2]});'),
('addsubps', '{i[1]} = _mm_addsub_ps({i[1]},{i[2]});'),
('aesdec', '{i[1]} = _mm_aesdec({i[1]},{i[2]});'),
('aesdeclast', '{i[1]} = _mm_aesdeclast({i[1]},{i[2]});'),
('aesenc', '{i[1]} = _mm_aesenc({i[1]},{i[2]});'),
('aesdeclast', '{i[1]} = _mm_aesendlast({i[1]},{i[2]});'),
('aesimc', '{i[1]} = _mm_aesimc({i[2]});'),
('aeskeygenassist', '{i[1]} = _mm_aesimc({i[1]},{i[2]});'),
('and', '{i[1]} &= {i[2]};'),

('dec', '{i[1]}--;'),
('mov', '{i[1]} = {i[2]};')
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
