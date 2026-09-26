SOURCE = 'not522'
LABEL = 'not522/ac-library-python'

from atcoder.mincostflow import MCFGraph

def run(data):
    n, edges, source, sink = data
    graph = MCFGraph(n)
    for a, b, capacity, cost in edges:
        graph.add_edge(a, b, capacity, cost)
    return list(graph.flow(source, sink))
