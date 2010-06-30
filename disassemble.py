from libdisassemble.disassemble import *
import debug

def repr_x64(ins, r, w):
    def arg(n):
        return {'value': ins[n+1], 'repr': ins[n+1], 'r': r[n], 'w': w[n]}

    def jump_dest():
        dest = {'type':'const', 'value': ins[1], 'r': True, 'w': False}
        try:
            dest['repr'] = int(ins[1],16)
        except ValueError:
            dest['repr'] = ins[1]
        return dest

    nop = {'op': 'nop'}

    if ins[0][0] == 'j':
        cond = ins[0][1:]
        if cond == 'mp':
            cond = 'true'
        return {'op': 'jump', 'cond': cond, 'dest': jump_dest()}
    elif ins[0] == 'call':
        return {'op': 'call', 'dest': jump_dest()}
    elif ins[0] == 'leave':
        return nop
    elif ins[0] == 'cmp':
        cmp = {'value': 'cmp', 'repr': 'cmp', 'r': False, 'w': True}
        src = {'op': 'sub', 'dest': arg(0), 'src': arg(1)}
        return {'op': 'mov', 'dest': cmp, 'src': src}
    elif ins[0] == 'ret':
        dest = {'value': 'eax', 'repr': 'eax', 'r': True, 'w': False}
        return {'op': 'return', 'src': dest}
    elif len(ins) == 1:
        return {'op': ins[0]}
    elif len(ins) == 2:
        return {'op': ins[0], 'dest': arg(0)}
    elif len(ins) == 3:
        return {'op': ins[0], 'dest': arg(0), 'src': arg(1)}
    elif len(ins) == 4:
        return {'op': ins[0], 'dest': arg(0), 'src': arg(1), 'arg3': arg(2)}
    
    raise Exception('Bad x64 instruction: '+str(ins))

def disassemble_x64(buf, virt):
    """x64 disassembly"""
    FORMAT="INTEL"
    entries = [virt]

    result = {}
    while entries:
        addr = entries.pop()
        off = addr-virt
        while off < len(buf):
            p = Opcode(buf[off:], mode=64)
            pre = p.getPrefix()
            length = p.getSize()
            try:
                ins, r, w = p.getOpcode(FORMAT)
            except ValueError:
                break
            ins = repr_x64(ins, r, w)

            if debug.check('asm_rw'):
                print ins, r, w

            debug_dis = {
                'prefix': pre,
                'binary': buf[off:off+length]
            }
            result[addr] = {'ins': ins, 'loc': addr, 'length': length, 'debug': debug_dis, 'display': True}
            if ins['op'] == 'return':
                break
#            if ins['op'] == 'call':
#                j_addr = addr+length+ins['dest']['repr']
#                if j_addr not in result:
#                    entries.append(j_addr)
            if ins['op'] == 'jump':
                j_addr = addr+length+ins['dest']['repr']
#                if j_addr not in result:
                entries.append(j_addr)
                if ins['cond'] == 'true':
                    break
            off += length
            addr += length
    
    return [result[key] for key in sorted(result.keys())]

def disassemble(buf, virt, arch='x64'):
    archs = {
        'x64': disassemble_x64

    }
    return archs[arch](buf, virt)
