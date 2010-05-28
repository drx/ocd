from collections import defaultdict
from itertools import dropwhile

graphfile = None

class Graph:
    def __init__(self):
        self._pred = defaultdict(list)
        self._succ = defaultdict(list)
        self._vertices = {}

    def __str__(self):
        return 'Graph(vertices=' + str(self._vertices) + ', pred=' + str(self._pred) + ', succ=' + str(self._succ) + ')'

    def __contains__(self, (v, t)):
        if t == 'in':
            return (v in self._pred)
        if t == 'out':
            return (v in self._succ)
        if t == None:
            return (v in self._pred or v in self._succ)

    def successors(self, key):
        return self._succ[key]

    def set_vertex(self, k, v=None):
        self._vertices[k] = v

    def vertices(self):
        return self._vertices

    def add_edge(self, v_in, v_out):
        self._succ[v_in].append(v_out)
        self._pred[v_out].append(v_in)

    def export(self, f, name):
        def block_end(block):
            return block[-1]['loc']

        f.write("\tsubgraph {0} {{\n".format(name))
        for (block_type, block_loc), block in self.vertices().iteritems():
            f.write("\t\t{0}_{1:x} [label=\"{0}\\n{1:x}:{2:x}\"];\n".format(block_type, block_loc, block_end(block)))
            for v_type, v_out in self.successors((block_type, block_loc)):
                f.write("\t\t{0}_{1:x} -> {2}_{3:x};\n".format(block_type, block_loc, v_type, v_out))
        f.write("\t}\n")       

def control_flow_graph(function, labels, name):
    '''
    Analyze the control flow graph (cfg) of the function
    '''

    graph = Graph()
    block_acc = []
    block_cur = None
    block_last = None
    block_change = True
    pass_through = False
    for ins in function:
        if ins['loc'] in labels or block_change:
            if block_last is not None:
                graph.set_vertex(block_last, block_acc)
            block_cur = ('block', ins['loc'])
            block_acc = []
            graph.set_vertex(block_cur)

        if ins['loc'] in labels and pass_through:
            # pass-through edge
            graph.add_edge(block_last, ('block', ins['loc']))

        block_change = False
        pass_through = True

        if ins['ins'][0][0] == 'j': # jumps (and only jumps)
            loc_next = ins['loc']+ins['length']
            loc_j = loc_next+int(ins['ins'][1], 16)
            graph.add_edge(block_cur, ('block', loc_j))
            block_change = True
            if ins['ins'][0] != 'jmp':
                graph.add_edge(block_cur, ('block', loc_next))
            else:
                pass_through = False
        block_last = block_cur
        block_acc.append(ins)

    graph.set_vertex(block_last, block_acc)
  
    if graphfile:
        graph.export(graphfile, name)

    return graph_transform(graph)

def flip(x):
    '''
    flip(x)(f) = f(x)
    '''
    def f(g):
        return g(x)
    return f

def graph_transform(graph):
    '''
    Perform one step transformations of the graph according to
     preset rules until no more transformations can be performed.

    The rewriting system used here is decreasing (i.e. all transformations
     decrease the size of the graph) therefore it will always stop at
     some point.
    '''
    def trivial(graph):
        return False, graph

    rules = [trivial]

    i = dropwhile(lambda (x, y): not x, map(flip(graph), rules))
    try:
        return graph_transform(i.next())
    except StopIteration:
        return graph
