from subprocess import Popen, PIPE

def sections(filename):
    sections = {}
    p = Popen(["objdump", "-h", filename], stdout=PIPE)
    p_out = p.communicate()[0].decode()

    for line in p_out.split('\n'):
        words = line.split()
        if len(words) > 0 and words[0].isdigit():
            sections[words[1]] = {'start': int(words[5], 16), 'length': int(words[2], 16), 'virt': int(words[3],16)}
    return sections

def symbols(filename):
    symbols = {}
    p = Popen(["objdump", "-t", filename], stdout=PIPE)
    p_out = p.communicate()[0].decode()

    for line in p_out.split('\n'):
        words = line.split()
        if len(words) > 0 and words[1] == 'g' and not words[-1].startswith('_'):
            symbols[words[-1]] = {'start': int(words[0], 16), 'length': int(words[-2], 16), 'type': words[2]}
    
    return symbols

def objdump(filename):
    '''
    Find sections and symbols in an object file.
    '''
    obj_sections = sections(filename)
    obj_symbols = symbols(filename)

    return obj_sections, obj_symbols
