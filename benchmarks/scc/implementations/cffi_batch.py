SOURCE = 'cffi'
LABEL = 'local/acl-cffi (batched edges)'

from acl_cffi import scc_graph


def run(data):
    n, edges = data
    with scc_graph(n) as graph:
        graph.add_edges(edges)
        return sorted(sorted(group) for group in graph.scc())
