from libdisassemble.opcode86 import regs
from copy import deepcopy

legal_integers = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
legal_sse = ['xmm0', 'xmm1', 'xmm2', 'xmm3', 'xmm4', 'xmm5', 'xmm6', 'xmm7']
legal_other = ['rax']

def reg_normalize(reg):
    idx = map(lambda (x,y,z): x, regs).index(reg)
    return regs[idx&0xF][0]

class Params:
    def __init__(self):
        self.memory = []
        self.integers = []
        self.sse = []
        self.other = []
        self.args = []

    def add(self, reg, arg):
        arg = deepcopy(arg)
        if 'w' in arg:
            arg['w'] = False
            arg['r'] = True
        try:
            param = reg_normalize(reg)
        except ValueError:
            return False
        try:
            if legal_integers[len(self.integers)] == param:
                self.integers.append(reg)
                self.args.append(arg)
                return True
            elif legal_sse[len(self.sse)] == reg:
                #fix normalization here
                self.sse.append(reg)
                self.args.append(arg)
                return True
            elif legal_other[len(self.other)] == param:
                self.other.append(reg)
                return True
            else:
                return False
        except IndexError:
            return False

def fold(cfg, symbols):
    for block in cfg.iterblocks():
        inside_call = False
        for n, line in enumerate(reversed(block)):
            if inside_call:
                dest = line['ins']['dest']
                param = dest['value']
                if call_params.add(param, dest):
                    pass
                else:
                    apply_ins = {'op': 'apply', 'function': function_name, 'args': call_params.args}
                    block[len(block)-call_n-1]['ins'] = apply_ins
                    inside_call = False
                    call_params = None
            if line['ins']['op'] == 'call':
                inside_call = True
                call_n = n
                call_params = Params()
                function_name = 'unknown_function'
                if 'repr' in line['ins']['dest']:
                    addr = line['loc']+line['length']+line['ins']['dest']['repr']
                    if addr in symbols:
                        function_name = symbols[addr]
                    
