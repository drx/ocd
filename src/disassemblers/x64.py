from disassemblers.libdisassemble.disassemble import *
import debug

def repr_ins(ins, r, w, objbounds, sections, binary):
    '''
    Represent an x64 instruction in the immediate instruction format.
    '''
    def arg(n):
        '''
        Helper function for converting arguments.
        '''
        value = ins[n+1]
        arg_repr = value

        if value.startswith('0x'):
            val = int(value, 16)
            if val >= objbounds[0] and val < objbounds[1]:
                '''Likely candidate for a constant'''
    
                ro = sections['.rodata']
                if val >= ro['virt'] and val < ro['virt']+ro['length']:
                    addr = ro['start']+val-ro['virt']
                    for i, b in enumerate(binary[addr:]):
                        if b == 0:
                            s = binary[addr:addr+i].decode()
                            s = '"' + repr(s)[1:-1] + '"'
                            arg_repr = s
                            break
                        if i > 100:
                            break

        return {'value': value, 'repr': arg_repr, 'r': r[n], 'w': w[n]}

    def translate(op):
        '''
        Some instructions are easy to translate, but have weird names,
         for example imul -> mul.
        '''
        ins[0] = op
        return repr_ins(ins, r, w, objbounds, sections, binary)

    def jump_dest():
        '''
        Calculate a jump operand.
        '''
        dest = {'type':'const', 'value': ins[1], 'r': True, 'w': False}
        try:
            dest['repr'] = int(ins[1],16)
        except ValueError:
            dest['repr'] = ins[1]
        return dest

    def parse_addr(addr, r=True, w=False):
        '''
        Parse the addressing mode (e.g. in a LEA).
        '''
        addr = addr.strip().strip('[]')

        for op, repr in [('sub', '-'), ('add', '+'), ('mul', '*')]:
            parts = addr.partition(repr)
            if parts[1]:
                return {'op': op, 'dest': parse_addr(parts[0], r, w), 'src': parse_addr(parts[2], r, w)}
       
        return {'value': addr, 'repr': addr, 'r': r, 'w': w}
         

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
    elif ins[0] == 'lea':
        src = parse_addr(ins[2])
        return {'op': 'mov', 'dest': arg(0), 'src': src}
    elif ins[0] == 'push':
        return nop
    elif ins[0] == 'imul':
        # libdisassemble bug fix :(
        w[0] = True
        return translate('mul')
    elif ins[0] == 'idiv':
        return translate('div')
    elif ins[0] == 'cmp':
        cmp = {'value': 'cmp', 'repr': 'cmp', 'r': False, 'w': True}
        src = {'op': 'sub', 'dest': arg(0), 'src': arg(1)}
        return {'op': 'mov', 'dest': cmp, 'src': src}
    elif ins[0] == 'test':
        cmp = {'value': 'cmp', 'repr': 'cmp', 'r': False, 'w': True}
        src = {'op': 'and', 'dest': arg(0), 'src': arg(1)}
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

def disassemble(buf, virt, sections, binary):
    '''
    Disassemble a block of x64 code.
    '''

    virts = [(sections[sect]['virt'], sections[sect]['length']) for sect in sections if sections[sect]['virt']]
    objmin = min(virt[0] for virt in virts)
    objmax = max(virt[0]+virt[1] for virt in virts)
    objbounds = (objmin, objmax)

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
            ins = repr_ins(ins, r, w, objbounds, sections, binary)

            if debug.check('asm_rw'):
                print(ins, r, w)

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
                if j_addr not in result:
                    entries.append(j_addr)
                result[addr]['display'] = False
                if ins['cond'] == 'true':
                    break
            off += length
            addr += length
    
    return [result[key] for key in sorted(result.keys())]
