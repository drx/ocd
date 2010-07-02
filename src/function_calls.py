from disassemblers.libdisassemble.opcode86 import regs
from copy import deepcopy

legal_integers = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
legal_sse = ['xmm0', 'xmm1', 'xmm2', 'xmm3', 'xmm4', 'xmm5', 'xmm6', 'xmm7']
legal_other = ['rax']

def reg_normalize(reg):
    '''
    Normalize a register to a form independent of its size.
    '''
    idx = list(map(lambda x: x[0], regs)).index(reg)
    return regs[idx&0xF][0]

class Params:
    '''
    A data structure that holds the current list of parameters used
     and is able to let you know when it ends using some heuristics.
    '''
    def __init__(self):
        self.memory = []
        self.integers = []
        self.sse = []
        self.other = []
        self.args = []

    def add(self, reg, arg):
        '''
        Try to add a register to the list of params.

        If its the next legal register in a list of parameters, it's added
         and True is returned. If it isn't, False is returned so that the
         function can be wrapped.
        '''
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
    '''
    Fold as many function calls as its possible, infering arguments lists
     along the way.
    '''
    for block, depth in cfg.iterblocks():
        inside_call = False
        for n, line in enumerate(reversed(block)):
            if inside_call:
                if 'dest' not in line['ins']:
                    continue
                dest = line['ins']['dest']
                param = dest['value']
                if call_params.add(param, dest):
                    pass
                else:
                    apply_ins = {'op': 'apply', 'function': function_name, 'args': call_params.args}
                    eax = {'value': 'eax', 'repr': 'eax', 'r': False, 'w': True}
                    mov_ins = {'op': 'mov', 'src': apply_ins, 'dest': eax}
                    block[len(block)-call_n-1]['ins'] = mov_ins
                    inside_call = False
                    call_params = None
            if line['ins']['op'] == 'call':
                inside_call = True
                call_n = n
                call_params = Params()
                function_name = 'unknown_function'
                if 'repr' in line['ins']['dest']:
                    if type(line['ins']['dest']['repr']) == int:
                        addr = line['loc']+line['length']+line['ins']['dest']['repr']
                        if addr in symbols:
                            function_name = symbols[addr]
                    
