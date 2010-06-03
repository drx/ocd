from libdisassemble.disassemble import *

def repr_x64(ins, r, w):
    def arg(n):
        return {'value': ins[n+1], 'r': r[n], 'w': w[n]}

    if ins[0][0] == 'j':
        cond = ins[0][1:]
        if cond == 'mp':
            cond = 'true'
        dest = {'type':'const', 'value': ins[1], 'repr': int(ins[1],16), 'r': True, 'w': False}
        return {'op': 'jump', 'cond': cond, 'dest': dest}
    elif ins[0] == 'ret':
        dest = {'value': 'eax', 'r': True, 'w': False}
        return {'op': 'return', 'dest': dest}
    elif len(ins) == 1:
        return {'op': ins[0]}
    elif len(ins) == 2:
        return {'op': ins[0], 'dest': arg(0)}
    elif len(ins) == 3:
        return {'op': ins[0], 'dest': arg(0), 'src': arg(1)}
    
    raise Exception('Bad x64 instruction')

def disassemble_x64(buf, virt):
    FORMAT="INTEL"
    off = 0

    result = []
    while off != len(buf):
        p = Opcode(buf[off:], mode=64)
        pre = p.getPrefix()
        length = p.getSize()
        ins, r, w = p.getOpcode(FORMAT)
        ins = repr_x64(ins, r, w)
        debug = {
            'prefix': pre,
            'binary': buf[off:off+length]
        }
        result.append({'ins': ins, 'loc': virt+off, 'length': length, 'debug': debug})
        off += length
    return result

def disassemble(buf, virt, arch='x64'):
    archs = {
        'x64': disassemble_x64
    }
    return archs[arch](buf, virt)
