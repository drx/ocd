from libdisassemble.disassemble import *

data = "\xeb\xfe"
p = Opcode(data)
print p.getOpcode("AT&T")
