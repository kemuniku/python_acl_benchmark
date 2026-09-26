SOURCE = 'cffi'
LABEL = 'local/acl-cffi (CFFI + C++)'

from acl_cffi import scc_graph

def run(data):
    n, edges = data
    with scc_graph(n) as graph:
        for a, b in edges:
            graph.add_edge(a, b)
        return sorted(sorted(group) for group in graph.scc())
