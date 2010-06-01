#!/usr/bin/env python

from libdisassemble.disassemble import *

def disassemble(buf, virt):
    FORMAT="INTEL"
    off = 0

    result = []
    while off != len(buf):
#        try:
            p = Opcode(buf[off:], mode=64)
            pre = p.getPrefix()
            length = p.getSize()
            ins, r, w = p.getOpcode(FORMAT)
            result.append({'prefix': pre, 'ins': ins, 'loc': virt+off, 'length': length, 'bin': buf[off:off+length], 'r': r, 'w': w})
            off += length
# catch-all except... this was bad.
#        except:
#            break
    return result
