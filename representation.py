repr_table_c = {
'adc': ('{i[dest]} = ', '{i[dest]} + {i[src]} + {cf}'),
'add': ('{i[dest]} = ', '{i[dest]} + {i[src]}'),
'and': ('({i[dest]} = ', '{i[dest]} & {i[src]}'),
'bt': ('{cf} = ', '{i[dest][{i[src]}]}'),
'clc': ('{cf} = ', '0'),
'cld': ('{df} = ', '0'),
'cmp': ('cmp = ', '{i[dest]} - {i[src]}'),
'imul': ('{i[dest]} = ', '{i[dest]} * {i[src]}'),
'dec': ('{i[dest]} = ', '{i[dest]} - 1'),
'lea': ('{i[dest]} = ', '{i[src]}'),
'mov': ('{i[dest]} = ', '{i[src]}'),
#'pop', '
#'push', '
'jump': ('', ''),
'nop': ('', ''),
'return': ('return {i[src]}', ''),
'sub': ('{i[dest]} = ', '{i[dest]} - {i[src]}'),
'xor': ('{i[dest]} = ', '{i[dest]} ^ {i[src]}'),
}

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

def representation(op, lang='C'):
    langs = {
        'C': repr_table_c
    }
    return langs[lang][op]
