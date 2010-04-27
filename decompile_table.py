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
('bsf','''
    if(!{i[2]})
        {zf} = 1;
    else
    \{
        {zf} = 0;
        int {temp} = 0;
        while({i[2][{temp}]==0)
        \{
            {temp}++;
            {i[1]}={temp};
        \}
    \}
    ''',None),#temporary variable names stream needed
('bsr', '''
    if(!{i[2]})
        {zf} = 1;
    else
    \{
        {zf} = 0;
        int {temp} = {i[2].size}-1;
        while({i[2][{temp}]==0)
        \{
            {temp}--;
            {i[1]}={temp};
        \}
    \}
    ''',None),#bit size of operand needed
#('bitswap', - dividing operands in four
('bt', '{cf} = {i[1][{i[2]}]};',None),
('btc', '''
    {cf} = {i[1][{i[2]}]};
    {i[1][{i[2]}]} = ~{i[1][{i[2]}]};
    ''', None),
('btr', '''
    {cf} = {i[1][{i[2]}]};
    {i[1][{i[2]}]} = 0;
    ''', None),
('bts', '''
    {cf} = {i[1][{i[2]}]};
    {i[1][{i[2]}]} = 1;
    ''', None),
#('call' - lol'd
#('cbw', '''
#    '''),
#('cwde', '''
#    '''),
#('cdqe', '''
#    ''') 
# operand length dependent
('clc', '{cf} = 0;}',None),
('cld', '{df} = 0;}',None),
('clflush', '_mm_clflush({i[1]});',None),
#('cli', - many lines of code to which tools don't exist yet
('clts', '{cr0.ts[3] = 0}', None),
('cmc', '{eflags.cf[0]} = ~{eflags.cf[0]}', None),
('cmp', 'cmp = {i[1]} - {i[2]};', None),
#('cmovcc - is wildcard available here? many variations of the name

('dec', '{i[1]}--;',None),
('ja', 'if (cmp > 0) goto loc_{extra:x};', lambda env: jump(env)),
('jae', 'if (cmp >= 0) goto loc_{extra:x};', lambda env: jump(env)),
('jb', 'if (cmp < 0) goto loc_{extra:x};', lambda env: jump(env)),
('jbe', 'if (cmp <= 0) goto loc_{extra:x};', lambda env: jump(env)),
('jc', 'if (cmp <= 0) goto loc_{extra:x};', lambda env: jump(env)),
('jcxz', 'if (!{cx}) goto loc_{extra:x};', lambda env: jump(env)),
('jecxz', 'if (!{ecx}) goto loc_{extra:x};', lambda env: jump(env)),
('jrcxz', 'if (!{rcx}) goto loc_{extra:x};', lambda env: jump(env)),
('je', 'if (!cmp) goto loc_{extra:x};', lambda env: jump(env)),
('jg', 'if (cmp > 0) goto loc_{extra:x};', lambda env: jump(env)),
('jge', 'if (cmp >= 0) goto loc_{extra:x};', lambda env: jump(env)),
('jl', 'if (cmp < 0) goto loc_{extra:x};', lambda env: jump(env)),
('jle', 'if (cmp <= 0) goto loc_{extra:x};', lambda env: jump(env)),
('jna', 'if (cmp <= 0) goto loc_{extra:x};', lambda env: jump(env)),
('jnae', 'if (cmp < 0) goto loc_{extra:x};', lambda env: jump(env)),
('jnb', 'if (cmp >= 0) goto loc_{extra:x};', lambda env: jump(env)),
('jnbe', 'if (cmp > 0) goto loc_{extra:x};', lambda env: jump(env)),
('jnc', 'if (cmp >= 0) goto loc_{extra:x};', lambda env: jump(env)),
('jne', 'if (!cmp) goto loc_{extra:x};', lambda env: jump(env)),
('jng', 'if (cmp <= 0) goto loc_{extra:x};', lambda env: jump(env)),
('jnge', 'if (cmp < 0) goto loc_{extra:x};', lambda env: jump(env)),
('jnl', 'if (cmp >= 0) goto loc_{extra:x};', lambda env: jump(env)),
('jnle', 'if (cmp > 0) goto loc_{extra:x};', lambda env: jump(env)),
('jno', 'if (no_overflow) goto loc_{extra:x};', lambda env: jump(env)),
('jnp', 'if (cmp & 1) goto loc_{extra:x};', lambda env: jump(env)),
('jns', 'if ((cmp>0)-(cmp<0) == -1) goto loc_{extra:x};', lambda env: jump(env)),
('jo', 'if (overflow) goto loc_{extra:x};', lambda env: jump(env)),
('jp', 'if (!(cmp & 1)) goto loc_{extra:x};', lambda env: jump(env)),
('jpe', 'if (!(cmp & 1)) goto loc_{extra:x};', lambda env: jump(env)),
('jpo', 'if (cmp & 1) goto loc_{extra:x};', lambda env: jump(env)),
('js', 'if ((cmp>0)-(cmp<0) >= 0) goto loc_{extra:x};', lambda env: jump(env)),
('jnz', 'if (cmp) goto loc_{extra:x};', lambda env: jump(env)),
('jz', 'if (!cmp) goto loc_{extra:x};', lambda env: jump(env)),
('jmp', 'goto loc_{extra:x};', lambda env: jump(env)),
('lea','{i[1]} = {i[2]}',None),
#('leave'
('mov', '{i[1]} = {i[2]};',None),
#('pop', '
#('push', '
('ret', 'return eax;', None),
('sub', '{i[1]} -= {i[2]};',None),
]

def jump(env):
    return env['loc']+env['length']+int(env['ins'][1],16)

def bitlen(op):
    return 8 * (len(str(op))-2)
#is it a workaround? I hope so...



