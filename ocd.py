#!/usr/bin/env python
from disassemble import disassemble

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

    print disassemble(buf)

