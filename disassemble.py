from libdisassemble.disassemble import *

from UserDict import DictMixin

class OrderedDict(dict, DictMixin):

    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        try:
            self.__end
        except AttributeError:
            self.clear()
        self.update(*args, **kwds)

    def clear(self):
        self.__end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.__map = {}                 # key --> [key, prev, next]
        dict.clear(self)

    def __setitem__(self, key, value):
        if key not in self:
            end = self.__end
            curr = end[1]
            curr[2] = end[1] = self.__map[key] = [key, curr, end]
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        key, prev, next = self.__map.pop(key)
        prev[2] = next
        next[1] = prev

    def __iter__(self):
        end = self.__end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.__end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def popitem(self, last=True):
        if not self:
            raise KeyError('dictionary is empty')
        if last:
            key = reversed(self).next()
        else:
            key = iter(self).next()
        value = self.pop(key)
        return key, value

    def __reduce__(self):
        items = [[k, self[k]] for k in self]
        tmp = self.__map, self.__end
        del self.__map, self.__end
        inst_dict = vars(self).copy()
        self.__map, self.__end = tmp
        if inst_dict:
            return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    def keys(self):
        return list(self)

    setdefault = DictMixin.setdefault
    update = DictMixin.update
    pop = DictMixin.pop
    values = DictMixin.values
    items = DictMixin.items
    iterkeys = DictMixin.iterkeys
    itervalues = DictMixin.itervalues
    iteritems = DictMixin.iteritems

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.items())

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __eq__(self, other):
        if isinstance(other, OrderedDict):
            return len(self)==len(other) and self.items() == other.items()
        return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self == other


def repr_x64(ins, r, w):
    def arg(n):
        return {'value': ins[n+1], 'r': r[n], 'w': w[n]}

    def jump_dest(ins):
        dest = {'type':'const', 'value': ins[1], 'repr': repr, 'r': True, 'w': False}
        try:
            dest['repr'] = int(ins[1],16)
        except ValueError:
            pass
        return dest


    if ins[0][0] == 'j':
        cond = ins[0][1:]
        if cond == 'mp':
            cond = 'true'
        return {'op': 'jump', 'cond': cond, 'dest': jump_dest(ins)}
    elif ins[0] == 'call':
        return {'op': 'call', 'dest': jump_dest(ins)}
    elif ins[0] == 'ret':
        dest = {'value': 'eax', 'r': True, 'w': False}
        return {'op': 'return', 'dest': dest}
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

"""Intelligent x64 disassembly"""
def disassemble_x64_int(buf, virt):
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
            debug = {
                'prefix': pre,
                'binary': buf[off:off+length]
            }
            result[addr] = {'ins': ins, 'loc': addr, 'length': length, 'debug': debug}
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
        'x64': disassemble_x64_int

    }
    return archs[arch](buf, virt)
