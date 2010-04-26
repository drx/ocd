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
    '''),#temporary variable names stream needed
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
    '''),#bit size of operand needed
#('bitswap', - dividing operands in four
('bt', '{cf} = {i[1][{i[2]}]};'),
('btc', '''
    {cf} = {i[1][{i[2]}]};
    {i[1][{i[2]}]} = ~{i[1][{i[2]}]};
    '''),
('btr', '''
    {cf} = {i[1][{i[2]}]};
    {i[1][{i[2]}]} = 0;
    '''),
('bts', '''
    {cf} = {i[1][{i[2]}]};
    {i[1][{i[2]}]} = 1;
    '''),
('dec', '{i[1]}--;'),
('mov', '{i[1]} = {i[2]};'),
#('call' - lol'd
#('cbw', '''
#    '''),
#('cwde', '''
#    '''),
#('cdqe', '''
#    ''') 
# operand length dependent
('clc', '{cf} = 0;}'),
('cld', '{df} = 0;}'),
('clflush', '_mm_clflush({i[1]});'),
#('cli', - many lines

]

