#!/usr/bin/env python
from disassemble import disassemble
from decompile import decompile_function
from debug import debug_start

from subprocess import Popen, PIPE

def objdump(filename):
    print filename
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
    from optparse import OptionParser

    usage = "usage: %prog [options] file"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--debug", dest="debug", action="store_true",
        help="turn debug mode on", default=False)

    options, args = parser.parse_args()

    if options.debug:
        debug_start()    

    if len(args) < 1:
        parser.print_help()

        sys.exit(0)

    filename = args[0]
    text, symbols = objdump(filename)

    f = open(filename)

    for name, symbol in symbols.iteritems():
        f.seek(symbol['start']-text['virt']+text['start'])
        buf = f.read(symbol['length'])
        print decompile_function(disassemble(buf, symbol['start']), name)
