SOURCE = 'tatyam'
LABEL = 'tatyam-prime/acl-cpp-python (C++)'

from acl_cpp.scc import scc_graph

def run(data):
    n, edges = data
    graph = scc_graph(n)
    for a, b in edges:
        graph.add_edge(a, b)
    return sorted(sorted(group) for group in graph.scc())
