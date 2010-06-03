from libdisassemble.disassemble import *

def disassemble_x64(buf, virt):
    FORMAT="INTEL"
    off = 0

    result = []
    while off != len(buf):
        p = Opcode(buf[off:], mode=64)
        pre = p.getPrefix()
        length = p.getSize()
        ins, r, w = p.getOpcode(FORMAT)
        result.append({'prefix': pre, 'ins': ins, 'loc': virt+off, 'length': length, 'bin': buf[off:off+length], 'r': r, 'w': w})
        off += length
    return result

def disassemble(buf, virt, arch='x64'):
    return disassemble_x64(buf, virt)
