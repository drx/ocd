decompile_table = [
('aaa', 'BCD_AAA();',None),
('aad', 'BCD_AAD();',None),
('aam', 'BCD_AAM();',None),
('aas', 'BCD_AAS();',None),
('adc', '{i[1]} += {i[2]} + {cf};',None),
('add', '{i[1]} += {i[2]};',None),
('addpd', '{i[1]} = _mm_add_pd({i[1]},{i[2]});',None),
('addps', '{i[1]} = _mm_add_ps({i[1]},{i[2]});',None),
('addsd', '{i[1]} = _mm_add_sd({i[1]},{i[2]});',None),
('addss', '{i[1]} = _mm_add_ss({i[1]},{i[2]});',None),
('addsubpd', '{i[1]} = _mm_addsub_pd({i[1]},{i[2]});',None),
('addsubps', '{i[1]} = _mm_addsub_ps({i[1]},{i[2]});',None),
('aesdec', '{i[1]} = _mm_aesdec({i[1]},{i[2]});',None),
('aesdeclast', '{i[1]} = _mm_aesdeclast({i[1]},{i[2]});',None),
('aesenc', '{i[1]} = _mm_aesenc({i[1]},{i[2]});',None),
('aesdeclast', '{i[1]} = _mm_aesendlast({i[1]},{i[2]});',None),
('aesimc', '{i[1]} = _mm_aesimc({i[2]});',None),
('aeskeygenassist', '{i[1]} = _mm_aesimc({i[1]},{i[2]});',None),
('and', '{i[1]} &= {i[2]};',None),
('andpd', '{i[1]} = _mm_and_pd({i[1]},{i[2]});',None),
('andps', '{i[1]} = _mm_and_ps({i[1]},{i[2]});',None),
('andnpd', '{i[1]} = _mm_andnot_pd({i[1]},{i[2]});',None),
('andnps', '{i[1]} = _mm_andnot_ps({i[1]},{i[2]});',None),
#('arpl', - some weird things - x86 is the stuff
('blendpd', '{i[1]} = _mm_blend_pd({i[1]},{i[2]},{i[2]});',None),
('blendps', '{i[1]} = _mm_blend_ps({i[1]},{i[2]},{i[2]});',None),
('blendvpd', '{i[1]} = _mm_blendv_pd({i[1]},{i[2]},{i[2]});',None),
('blendvps', '{i[1]} = _mm_blendv_ps({i[1]},{i[2]},{i[2]});',None),
('bound', 'if({i[1]}<{i[2][0:15]}||{i[1]}>{i[2][16:31]}){#br};',None),#32 and 64bit - have to add some unified variable divider
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
('bsr', '''if(!{i[2]})\n
        {zf} = 1;\n
    else\n
    \{\n
        {zf} = 0;\n
        int {temp} = {i[2].size}-1;\n
        while({i[2][{temp}]==0)\n
        \{\n
            {temp}--;\n
            {i[1]}={temp};
        \}\n
    \}\n''',None),#bit size of operand needed

('dec', '{i[1]}--;',None),
('jmp', 'goto loc_{extra:x};', lambda env: env['loc']+env['length']+int(env['ins'][1],16)),
('mov', '{i[1]} = {i[2]};',None),
]

