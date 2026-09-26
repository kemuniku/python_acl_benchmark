SOURCE = 'not522'
LABEL = 'not522/ac-library-python'

from atcoder.scc import SCCGraph

def run(data):
    n, edges = data
    graph = SCCGraph(n)
    for a, b in edges:
        graph.add_edge(a, b)
    return sorted(sorted(group) for group in graph.scc())
