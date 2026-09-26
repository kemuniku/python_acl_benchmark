SOURCE = 'shakayami'
LABEL = 'shakayami/ACL-for-python'

from mincostflow import mcf_graph

def run(data):
    n, edges, source, sink = data
    graph = mcf_graph(n)
    for a, b, capacity, cost in edges:
        graph.add_edge(a, b, capacity, cost)
    return list(graph.flow(source, sink))
