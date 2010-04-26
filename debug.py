_debug = False

def debug_start():
    global _debug
    _debug = True

def debug(str):
    global _debug
    if _debug:
        return str
    else:
        return ''
