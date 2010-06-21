decompile_table = [
#('aaa', 'BCD_AAA();', None),
#('aad', 'BCD_AAD();', None),
#('aam', 'BCD_AAM();', None),
#('aas', 'BCD_AAS();', None),
('adc', '{i[dest]} = ', '{i[dest]} + {i[src]} + {cf};', None),
('add', '{i[dest]} = ', '{i[dest]} + {i[src]};', None),
#('addpd', '{i[dest]} = _mm_add_pd({i[1]},{i[src]});', None),
#('addps', '{i[dest]} = _mm_add_ps({i[1]},{i[src]});', None),
#('addsd', '{i[dest]} = _mm_add_sd({i[1]},{i[src]});', None),
#('addss', '{i[dest]} = _mm_add_ss({i[1]},{i[src]});', None),
#('addsubpd', '{i[dest]} = _mm_addsub_pd({i[1]},{i[src]});', None),
#('addsubps', '{i[dest]} = _mm_addsub_ps({i[1]},{i[src]});', None),
#('aesdec', '{i[dest]} = _mm_aesdec({i[1]},{i[src]});', None),
#('aesdeclast', '{i[dest]} = _mm_aesdeclast({i[1]},{i[src]});', None),
#('aesenc', '{i[dest]} = _mm_aesenc({i[1]},{i[src]});', None),
#('aesdeclast', '{i[dest]} = _mm_aesendlast({i[1]},{i[src]});', None),
#('aesimc', '{i[dest]} = _mm_aesimc({i[src]});', None),
#('aeskeygenassist', '{i[dest]} = _mm_aesimc({i[1]},{i[src]});', None),
('and', '{i[dest]} = ', '{i[dest]} & {i[src]};', None),
#('andpd', '{i[dest]} = _mm_and_pd({i[1]},{i[src]});', None),
#('andps', '{i[dest]} = _mm_and_ps({i[1]},{i[src]});', None),
#('andnpd', '{i[dest]} = _mm_andnot_pd({i[1]},{i[src]});', None),
#('andnps', '{i[dest]} = _mm_andnot_ps({i[1]},{i[src]});', None),
#('arpl', - some weird things - x86 is the stuff
#('blendpd', '{i[dest]} = _mm_blend_pd({i[1]},{i[src]},{i[2]});', None),
#('blendps', '{i[dest]} = _mm_blend_ps({i[1]},{i[src]},{i[2]});', None),
#('blendvpd', '{i[dest]} = _mm_blendv_pd({i[1]},{i[src]},{i[2]});', None),
#('blendvps', '{i[dest]} = _mm_blendv_ps({i[1]},{i[src]},{i[2]});', None),
#('bound', 'if({i[dest]}<{i[src][0:15]}||{i[1]}>{i[2][16:31]}){#br};', None),#32 and 64bit - have to add some unified variable divider
#('bsf','''
#    if(!{i[src]})
#        {zf} = 1;
#    else
#    \{
#        {zf} = 0;
#        int {temp} = 0;
#        while({i[src][{temp}]==0)
#        \{
#            {temp}++;
#            {i[dest]}={temp};
#        \}
#    \}
#    ''', None),#temporary variable names stream needed
#('bsr', '''
#    if(!{i[src]})
#        {zf} = 1;
#    else
#    \{
#        {zf} = 0;
#        int {temp} = {i[src].size}-1;
#        while({i[src][{temp}]==0)
#        \{
#            {temp}--;
#            {i[dest]}={temp};
#        \}
#    \}
#    ''', None),#bit size of operand needed
#('bitswap', - dividing operands in four
('bt', '{cf} = ', '{i[dest][{i[src]}]};', None),
#('btc', '''
#    {cf} = {i[dest][{i[src]}]};
#    {i[dest][{i[src]}]} = ~{i[1][{i[2]}]};
#    ''', None),
#('btr', '''
#    {cf} = {i[dest][{i[src]}]};
#    {i[dest][{i[src]}]} = 0;
#    ''', None),
#('bts', '''
#    {cf} = {i[dest][{i[src]}]};
#    {i[dest][{i[src]}]} = 1;
#    ''', None),
#('call' - lol'd
#('cbw', '''
#    '''),
#('cwde', '''
#    '''),
#('cdqe', '''
#    ''') 
# operand length dependent
('clc', '{cf} = ', '0;}', None),
('cld', '{df} = ', '0;}', None),
#('clflush', '_mm_clflush({i[dest]});', None),
#('cli', - many lines of code to which tools don't exist yet
#('clts', '{cr0.ts[3] = 0}', None),
#('cmc', '{eflags.cf[0]} = ~{eflags.cf[0]}', None),
('cmp', 'cmp = ', '{i[dest]} - {i[src]};', None),
#('cmovcc - is wildcard available here? many variations of the name

('dec', '{i[dest]} = ', '{i[dest]} - 1;', None),
('ja', 'if (cmp > 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jae', 'if (cmp >= 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jb', 'if (cmp < 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jbe', 'if (cmp <= 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jc', 'if (cmp <= 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jcxz', 'if (!{cx}) goto loc_{extra:x};', '', lambda env: jump(env)),
('jecxz', 'if (!{ecx}) goto loc_{extra:x};', '', lambda env: jump(env)),
('jrcxz', 'if (!{rcx}) goto loc_{extra:x};', '', lambda env: jump(env)),
('je', 'if (!cmp) goto loc_{extra:x};', '', lambda env: jump(env)),
('jg', 'if (cmp > 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jge', 'if (cmp >= 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jl', 'if (cmp < 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jle', 'if (cmp <= 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jna', 'if (cmp <= 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jnae', 'if (cmp < 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jnb', 'if (cmp >= 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jnbe', 'if (cmp > 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jnc', 'if (cmp >= 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jne', 'if (!cmp) goto loc_{extra:x};', '', lambda env: jump(env)),
('jng', 'if (cmp <= 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jnge', 'if (cmp < 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jnl', 'if (cmp >= 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jnle', 'if (cmp > 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jno', 'if (no_overflow) goto loc_{extra:x};', '', lambda env: jump(env)),
('jnp', 'if (cmp & 1) goto loc_{extra:x};', '', lambda env: jump(env)),
('jns', 'if ((cmp>0)-(cmp<0) == -1) goto loc_{extra:x};', '', lambda env: jump(env)),
('jo', 'if (overflow) goto loc_{extra:x};', '', lambda env: jump(env)),
('jp', 'if (!(cmp & 1)) goto loc_{extra:x};', '', lambda env: jump(env)),
('jpe', 'if (!(cmp & 1)) goto loc_{extra:x};', '', lambda env: jump(env)),
('jpo', 'if (cmp & 1) goto loc_{extra:x};', '', lambda env: jump(env)),
('js', 'if ((cmp>0)-(cmp<0) >= 0) goto loc_{extra:x};', '', lambda env: jump(env)),
('jnz', 'if (cmp) goto loc_{extra:x};', '', lambda env: jump(env)),
('jz', 'if (!cmp) goto loc_{extra:x};', '', lambda env: jump(env)),
('jmp', 'goto loc_{extra:x};', '', lambda env: jump(env)),
('lea','{i[dest]} = ', '{i[src]}', None),
('leave', '', '', None),
('mov', '{i[dest]} = ', '{i[src]};', None),
#('pop', '
#('push', '
('return', 'return {i[dest]};', '', None),
('sub', '{i[dest]} = ', '{i[dest]} - {i[src]};', None),
]

condition_negs = {
    'a': 'be', 'ae': 'b', 'b': 'ae', 'be': 'a', 'c': 'a',
    'e': 'ne', 'ne': 'e',
    'g': 'le', 'ge': 'l', 'l': 'ge', 'le': 'g',
    'na': 'a', 'nae': 'ae', 'nb': 'b', 'nbe': 'be', 'nc': 'c',
    'ng': 'g', 'nge': 'ge', 'nl': 'l', 'nle': 'le',
    'no': 'o', 'o': 'no', 's': 'ns',  'ns': 's',
    'p': 'np', 'np': 'p', 'pe': 'np', 'po': 'p',
    'z': 'nz', 'nz': 'z', 'true': 'false', 'false': 'true'
}

conditions = {
    'a': '{cond} > 0',
    'ae': '{cond} >= 0',
    'b': '{cond} < 0',
    'be': '{cond} <= 0',
    'c': '{cond} <= 0',
    'cxz': '!{cx}',
    'ecxz': '!{ecx}',
    'rcxz': '!{rcx}',
    'e': '!{cond}',
    'g': '{cond} > 0',
    'ge': '{cond} >= 0',
    'l': '{cond} < 0',
    'le': '{cond} <= 0',
    'na': '{cond} <= 0',
    'nae': '{cond} < 0',
    'nb': '{cond} >= 0',
    'nbe': '{cond} > 0',
    'nc': '{cond} >= 0',
    'ne': '!{cond}',
    'ng': '{cond} <= 0',
    'nge': '{cond} < 0',
    'nl': '{cond} >= 0',
    'nle': '{cond} > 0',
    'no': 'no_overflow',
    'np': '{cond} & 1',
    'ns': '({cond}>0)-(cmp<0) == -1',
    'o': 'overflow',
    'p': '!({cond} & 1)',
    'pe': '!({cond} & 1)',
    'po': '{cond} & 1',
    's': '({cond}>0)-(cmp<0) >= 0',
    'nz': '{cond}',
    'z': '!{cond}',
    'true': '1',
    'false': '0',
} 

def jump(env):
    return env['loc']+env['length']+int(env['ins']['dest'],16)

def bitlen(op):
    return 8 * (len(str(op))-2)
#is it a workaround? I hope so...



