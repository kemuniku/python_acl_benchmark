SOURCE = 'not522'
LABEL = 'not522/ac-library-python'

from atcoder.maxflow import MFGraph

def run(data):
    n, edges, source, sink = data
    graph = MFGraph(n)
    for a, b, capacity in edges:
        graph.add_edge(a, b, capacity)
    return graph.flow(source, sink)
