#!/usr/bin/env python3
from disassemble import disassemble
from decompile import decompile_functions
from objdump import objdump
import control_flow
import debug
import representation

if __name__=="__main__":
    import sys
    from optparse import OptionParser

    usage = "usage: %prog [options] file"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--debug", dest="debug", action="append",
        help="turn debug option on", default=[], choices=debug.options,
        metavar="OPTION")
    parser.add_option("-g", "--graph", action="store", dest="graphfile",
        metavar="FILE", type="string", help="output a control flow graph")

    options, args = parser.parse_args()

    for option in options.debug:
        debug.set(option)    

    if len(args) < 1:
        parser.print_help()

        sys.exit(0)

    filename = args[0]

    f = open(filename, "rb")

    text, symbols = objdump(filename)

    if options.graphfile:
        gf = open(options.graphfile, 'w')
        gf.write("digraph cfg {\n")
        control_flow.graphfile = gf


    functions = {}
    if symbols:
        for name, symbol in symbols.items():
            f.seek(symbol['start']-text['virt']+text['start'])
            functions[name] = disassemble(f.read(symbol['length']), symbol['start'])
    else:
        f.seek(text['start'])
        functions['start'] = disassemble(f.read(text['length']), text['virt'])
        symbols['start'] = {'start': text['virt'], 'length': text['length']}

    decompiled_functions = decompile_functions(functions, symbols)

    print(representation.output_functions(decompiled_functions))

    if options.graphfile:
        gf.write("}\n")
        gf.close()
