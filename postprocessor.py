import copy
import re

def postprocessor(output):
    mem = {}
    pr = ""
    for line in copy.deepcopy(output).splitlines(True):
        m = re.search("\s*(temp_.*?)\s*=\s*(.*?);", line)
        if m:
            v = m.group(2)
            for key, val in mem.iteritems():
                v = v.replace(key, "({0})".format(val))
            mem[m.group(1)] = v
        else:
            for key, val in mem.iteritems():
                line = line.replace(key, "({0})".format(val))

            pr = pr + line
    return pr

