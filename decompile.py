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
('andpd', '{i[1]} = _mm_and_pd({i[1]},{i[2]});'),
('andps', '{i[1]} = _mm_and_ps({i[1]},{i[2]});'),
('andnpd', '{i[1]} = _mm_andnot_pd({i[1]},{i[2]});'),
('andnps', '{i[1]} = _mm_andnot_ps({i[1]},{i[2]});'),
#('arpl', - some weird things - x86 is the stuff
('blendpd', '{i[1]} = _mm_blend_pd({i[1]},{i[2]},{i[2]});'),
('blendps', '{i[1]} = _mm_blend_ps({i[1]},{i[2]},{i[2]});'),
('blendvpd', '{i[1]} = _mm_blendv_pd({i[1]},{i[2]},{i[2]});'),
('blendvps', '{i[1]} = _mm_blendv_ps({i[1]},{i[2]},{i[2]});'),
('bound', 'if({i[1]}<{i[2][0:15]}||{i[1]}>{i[2][16:31]}){#br};'),#32 and 64bit - have to add some unified variable divider
('bsf', '''if(!{i[2]})\n
        {zf} = 1;\n
    else\n
    \{\n
        {zf} = 0;\n
        int {temp} = 0;\n
        while({i[2][{temp}]==0)\n
        \{\n
            {temp}++;\n
            {i[1]}={temp};
        \}\n
    \}\n'''),#temporary variable names stream needed
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
