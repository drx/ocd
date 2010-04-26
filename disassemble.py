#!/usr/bin/env python

from libdisassemble.disassemble import *

def disassemble(buf, virt):
    FORMAT="INTEL"
    off = 0

    result = []
    while off != len(buf):
        try:
            p = Opcode(buf[off:])
            length = p.getSize()
            result.append({'ins': p.getOpcode(FORMAT), 'loc': virt+off, 'length': length, 'bin': buf[off:off+length]})
            off += length
        except:
            break
    
    return result
