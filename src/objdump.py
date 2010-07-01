from subprocess import Popen, PIPE

def objdump(filename):
    p1 = Popen(["objdump", "-h", filename], stdout=PIPE)
    p2 = Popen(["awk", "-f", "src/sections.awk"], stdin=p1.stdout, stdout=PIPE)
    sections_p = p2.communicate()[0].split()

    p1 = Popen(["objdump", "-t", filename], stdout=PIPE)
    p2 = Popen(["awk", "-f", "src/symbols.awk"], stdin=p1.stdout, stdout=PIPE)
    #symbols_p_raw = p2.communicate()[0]
    #print(type(symbols_p_raw))
    symbols_p = p2.communicate()[0].decode().split('\n')

    text = {'start': int(sections_p[0], 16), 'length': int(sections_p[1], 16), 'virt': int(sections_p[2], 16)}
    symbols = {}
    for symbol_p in symbols_p[:-1]:
        symbol = symbol_p.split()
        symbols[symbol[0]] = {'start': int(symbol[1], 16), 'length': int(symbol[2], 16)}

    return text, symbols
