'''
Debug module

Acceptable debug levels: all, graph, misc
'''

debug_options = ['all', 'graph', 'misc']

_debug = []

def debug_check(cond):
    global _debug
    return (cond in _debug or 'all' in _debug)    

def debug_set(cond=None):
    global _debug
    if cond is None:
        _debug.append('all')
    else:
        _debug.append(cond)

def debug_sprint(str, cond):
    if debug_check(cond):
        return str
    else:
        return ''

