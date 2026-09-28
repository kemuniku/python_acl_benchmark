SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library)'

from library.graph.SCC import SCC_construct

def run(data):
    n, edges = data
    graph = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)
    _, groups = SCC_construct(graph)
    return sorted(sorted(group) for group in groups)
