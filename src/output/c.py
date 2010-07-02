from output.indent import Indent
from output.conditions import conditions, condition_negs
import debug
import zlib

def operator(op, precedence):
    '''
    Helper function for C operators.
    '''
    return ('{i[dest]} = ', '{i[dest]} '+op+' {i[src]}', precedence)

ins_table = {
'add': operator('+', 12),
'and': operator('&', 8),
'div': operator('/', 13),
'mul': operator('*', 13),
'mov': ('{i[dest]} = ', '{i[src]}', 2),
'nop': ('', '', 0),
'return': ('return {i[src]}', '', 0),
'sar': operator('>>', 11),
'sal': operator('<<', 11),
'sub': operator('-', 12),
'xor': operator('^', 7),
}

def condition(cond, var='cmp'):
    '''
    Output a jump condition.
    '''
    if cond[0] == '!':
        cond = condition_negs[cond[1:]]
    return conditions[cond].format(cond=var)

def striplines(s):
    '''
    Strip empty lines from string.
    '''
    return '\n'.join(line for line in s.split('\n') if line.strip())

def repr_int(n):
    '''
    Get the representation of an integer.
    
    The representation is chosen based on its Kolmogorov complexity,
     i.e. the repr r is chosen which has the minimal value
     len(zlib.compress(r)).
    '''
    reprs = [('{0}','{0}'), ('{0:x}', '0x{0:x}')]
    lengths = [len(zlib.compress(r[0].format(n).encode())) for r in reprs]
    return reprs[lengths.index(min(lengths))][1].format(n)


def output_op(op):
    '''
    Output an instruction according to it's opcode.
    '''
    return ins_table[op]

def output_line(line, indent):
    '''
    Output a line of code. A line contains an instruction and
     some metainformation about that instruction (its location,
     etc.)

    The pseudo-EBNF of lines is as follows:

     line = location, debug, instruction
     instruction = op, argument*
     argument = value, repr | instruction
    '''
    def output_ins(ins):
        '''
        Decompile an instruction. Instructions are trees, see
         the EBNF for output_line.
        '''
        repr = {}
        prec = {}
        for k, arg in ins.items():
            if k not in ('src', 'dest'):
                continue

            if 'op' in ins[k]:
                lhs, rhs, prec[k] = output_ins(ins[k])
                repr[k] = rhs
            else:
                repr[k] = ins[k]['repr']
                prec[k] = 20

            if type(repr[k]) == int:
                repr[k] = repr_int(repr[k])

        if ins['op'] == 'apply':
            lhs = ''
            args = []
            for arg in ins['args']:
                if 'op' in arg:
                    lhs, rhs, inner_prec = output_ins(arg)
                    args.append(rhs)
                else:
                    args.append(arg['repr'])
            rhs = '{fun}({args})'.format(fun=ins['function'], args=', '.join(args))
            outer_prec = 20

        else:
            try:
                lhs, rhs, outer_prec = output_op(ins['op'])
            except KeyError:
                lhs, rhs = '', '/* Unsupported immediate instruction: {ins[op]} */'.format(ins=ins)
                outer_prec = 20

        for k in dict(repr):
            if outer_prec > prec[k]:
                repr[k] = '(' + repr[k] + ')'

        return lhs.format(i=repr), rhs.format(i=repr), outer_prec

    lhs, rhs, prec = output_ins(line['ins'])
    line_repr = indent.out() + lhs + rhs
    if lhs+rhs != '':
        line_repr += ';'

    if not line['display']:
        line_repr = ''

    if debug.check('misc'):
        from binascii import hexlify
        line_repr += '\n{indent}{blue}/* {line} */{black}'.format(indent=indent.out(), line=line, blue='\033[94m', black='\033[0m')

    return line_repr

def output_vertex(vertex, indent=None):
    '''
    Output a CFG vertex.
    '''
    key, block = vertex
    block_type, block_start = key

    if indent is None:
        indent = Indent(1)
 
    if block_type == 'block':
        return '\n'.join(output_line(line, indent) for line in block)

    elif block_type == 'if':
        cond, true = block
        fmt = ('\n'
              '{indent}if ({cond})\n'
              '{indent}{{\n'
              '{true}\n'
              '{indent}}}\n')
        return fmt.format(cond=condition(cond), true=output_vertex(true, indent.inc()), indent=indent.out())

    elif block_type == 'ifelse':
        cond, true, false = block
        fmt = ('\n'
              '{indent}if ({cond})\n'
              '{indent}{{\n'
              '{true}\n'
              '{indent}}}\n'
              '{indent}else\n'
              '{indent}{{\n'
              '{false}\n'
              '{indent}}}\n')
        return fmt.format(cond=condition(cond),
            true=output_vertex(true, indent.inc()), false=output_vertex(false, indent.inc()), indent=indent.out())

    elif block_type == 'while':
        cond, pre, loop = block
        fmt = ('\n'
              '{indent}while ({cond})\n'
              '{indent}{{\n'
              '{loop}\n'
              '{pre}\n'
              '{indent}}}\n')
        return fmt.format(indent=indent.out(), cond=condition(cond),
            pre=output_vertex(pre, indent.inc()), loop=output_vertex(loop, indent.inc()))

    elif block_type == 'cons':
        out = ''
        for b in block:
            out += output_vertex(b, indent)
        return out

    return '/* Error: unsupported block type */'

def output_signature(signature, name):
    '''
    Output the signature of a function.
    '''
    fun_type, args = signature

    pre = fun_type + ' ' + name + '(' + ', '.join(args) + ')\n{\n'
    post = '\n}'
    return pre, post

def output_function(function, name):
    '''
    Output a function.
    '''
    cfg, signature = function

    pre, post = output_signature(signature, name)
    
    innards = '\n/*----*/\n'.join(output_vertex(v) for v in cfg.sortedvertices())

    return pre + innards + post

def output(functions):
    '''
    Output everything.
    '''
    out = ''
    for name, function in functions.items():
        out += output_function(function, name)
        out += '\n'

    return striplines(out)
