#!/usr/bin/env python

from libdisassemble.disassemble import *

def disassemble(buf, virt):
    FORMAT="INTEL"
    off = 0

    result = []
    while off != len(buf):
        try:
            p = Opcode(buf[off:])
            pre = p.getPrefix()
            length = p.getSize()
            result.append({'prefix': pre, 'ins': p.getOpcode(FORMAT), 'loc': virt+off, 'length': length, 'bin': buf[off:off+length]})
            off += length
        except:
            break
    
    return result
