SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library_codex)'

from library_codex.graph_connectivity.StronglyConnectedComponents import SCC

def run(data):
    n, edges = data
    graph = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)
    return sorted(sorted(group) for group in SCC(graph).groups)
