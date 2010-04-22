from libdisassemble.disassemble import *

data = "\xeb\xfe\xeb\x00"

buf = data
FORMAT="AT&T"
off = 0


result = []
while off != len(data):
    try:
            p = Opcode(buf[off:])
            result.append( p.getOpcode(FORMAT) )
            off += p.getSize()
    except:
            break

print result
