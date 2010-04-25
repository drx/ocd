#!/usr/bin/env python

from libdisassemble.disassemble import *

#data = "\xeb\xfe\xeb\x00"
if __name__=="__main__":
    import sys
    if len(sys.argv) < 4:
        print "usage: %s <file> <offset> <size>" % sys.argv[0]
        print "\t file: file to disassemble"
        print "\t offset: offset to beggining of code (base 16)"
        print "\t size: amount of bytes to dissasemble (base 16)\n"

        sys.exit(0)

    f = open(sys.argv[1])
    offset = int(sys.argv[2], 16)
    f.seek(offset)
    buf = f.read(int(sys.argv[3], 16))

    FORMAT="INTEL"
    off = 0

    result = []
    while off != len(buf):
        try:
            p = Opcode(buf[off:])
            result.append( p.getOpcode(FORMAT) )
            off += p.getSize()
        except:
            break
    
    print result
