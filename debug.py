'''
Debug module

Acceptable debug levels: all, graph, misc
'''

debug_options = ['all', 'graph', 'misc']

__debug = []

def check(cond):
    global __debug
    return (cond in __debug or 'all' in __debug)    

def set(cond=None):
    global __debug
    if cond is None:
        __debug.append('all')
    else:
        __debug.append(cond)

def sprint(str, cond):
    if debug_check(cond):
        return str
    else:
        return ''
