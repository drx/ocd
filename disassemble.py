#!/usr/bin/env python

from libdisassemble.disassemble import *

def disassemble(buf):
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
    
    return result
