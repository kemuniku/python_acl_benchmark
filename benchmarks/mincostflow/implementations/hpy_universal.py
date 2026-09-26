SOURCE = 'hpy'
LABEL = 'local/acl-hpy (HPy Universal + C++)'

from acl_hpy import mcf_graph

def run(data):
    n, edges, source, sink = data
    with mcf_graph(n) as graph:
        for a, b, capacity, cost in edges:
            graph.add_edge(a, b, capacity, cost)
        return list(graph.flow(source, sink))
