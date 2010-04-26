#!/usr/bin/env python
from disassemble import disassemble
from decompile import decompile_function

from subprocess import Popen, PIPE

def objdump(filename):
    p1 = Popen(["objdump", "-h", filename], stdout=PIPE)
    p2 = Popen(["awk", "-f", "sections.awk"], stdin=p1.stdout, stdout=PIPE)
    sections_p = p2.communicate()[0].split()

    p1 = Popen(["objdump", "-t", filename], stdout=PIPE)
    p2 = Popen(["awk", "-f", "symbols.awk"], stdin=p1.stdout, stdout=PIPE)
    symbols_p = p2.communicate()[0].split('\n')

    text = {'start': int(sections_p[0], 16), 'length': int(sections_p[1], 16), 'virt': int(sections_p[2], 16)}
    symbols = {}
    for symbol_p in symbols_p[:-1]:
        symbol = symbol_p.split()
        symbols[symbol[0]] = {'start': int(symbol[1], 16), 'length': int(symbol[2], 16)}

    return text, symbols

if __name__=="__main__":
    import sys
    if len(sys.argv) < 2:
        print "usage: %s <file>" % sys.argv[0]

        sys.exit(0)

    text, symbols = objdump(sys.argv[1])

    f = open(sys.argv[1])

    for name, symbol in symbols.iteritems():
        f.seek(symbol['start']-text['virt']+text['start'])
        buf = f.read(symbol['length'])
        print decompile_function(disassemble(buf), name)
