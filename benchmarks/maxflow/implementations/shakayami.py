SOURCE = 'shakayami'
LABEL = 'shakayami/ACL-for-python'

from maxflow import mf_graph

def run(data):
    n, edges, source, sink = data
    graph = mf_graph(n)
    for a, b, capacity in edges:
        graph.add_edge(a, b, capacity)
    return graph.flow(source, sink)
