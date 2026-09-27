SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library_codex)'

from library_codex.graph_flow.MaxFlow import MaxFlowGraph as MFGraph

def run(data):
    n, edges, source, sink = data
    graph = MFGraph(n)
    for a, b, capacity in edges:
        graph.add_edge(a, b, capacity)
    return graph.flow(source, sink)
