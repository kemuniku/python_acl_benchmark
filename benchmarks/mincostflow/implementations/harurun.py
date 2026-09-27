SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library_codex)'

from library_codex.graph_flow.MinCostFlow import MinCostFlowGraph as MCFGraph

def run(data):
    n, edges, source, sink = data
    graph = MCFGraph(n)
    for a, b, capacity, cost in edges:
        graph.add_edge(a, b, capacity, cost)
    return list(graph.flow(source, sink))
