from collections import defaultdict

graphfile = None

class Graph:
    def __init__(self):
        self.pred = defaultdict(list)
        self.succ = defaultdict(list)

    def __str__(self):
        return 'Graph(pred=' + str(self.pred) + ', succ=' + str(self.succ) + ')'

    def __contains__(self, (v, t)):
        if t == 'in':
            return (v in self.pred)
        if t == 'out':
            return (v in self.succ)
        if t == None:
            return (v in self.pred or v in self.succ)

    def __getitem__(self, key):
        return self.succ[key]

    def add_edge(self, v_in, v_out):
        self.succ[v_in].append(v_out)
        self.pred[v_out].append(v_in)
        

def cfg(function, labels, name):
    '''
    Analyze the control flow graph (cfg) of the function
    '''

    graph = Graph()
    lastloc = None
    lastok = False
    for ins in function:
        ok = True 
        if ins['ins'][0][0] == 'j': # jumps (and only jumps)
            loc_cur = ins['loc']
            loc_j = ins['loc']+ins['length']+int(ins['ins'][1],16)
            graph.add_edge(loc_cur, loc_j)
            if ins['ins'][0] != 'jmp':
                print ins['ins'][0]
                graph.add_edge(loc_cur, loc_cur+ins['length'])
            else:
                ok = False
        if ins['loc'] in labels and lastok:
            # pass-through edge
            graph.add_edge(lastloc, ins['loc'])
        lastloc = ins['loc']
        lastok = ok
    
    start = None
    end = None
    lastloc = None
    blocks = {}
    for ins in function:
        if start is None:
            start = ins['loc']
            lastloc = ins['loc']
        if (ins['loc'], 'in') in graph:
            blocks[start] = lastloc
            start = ins['loc']
        end = ins['loc']
        lastloc = ins['loc']
    blocks[start] = end

    if graphfile:
        graphfile.write("\tsubgraph {0} {{\n".format(name))
        for block in blocks:
            graphfile.write("\t\tb_{0:x} [label=\"block\\n{0:x}:{1:x}\"];\n".format(block, blocks[block]))
            for v_out in graph[blocks[block]]:
                graphfile.write("\t\tb_{0:x} -> b_{1:x};\n".format(block, v_out))
        graphfile.write("\t}\n")

    return function
