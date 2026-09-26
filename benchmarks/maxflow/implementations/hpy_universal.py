SOURCE = 'hpy'
LABEL = 'local/acl-hpy (HPy Universal + C++)'

from acl_hpy import mf_graph

def run(data):
    n, edges, source, sink = data
    with mf_graph(n) as graph:
        for a, b, capacity in edges:
            graph.add_edge(a, b, capacity)
        return graph.flow(source, sink)
