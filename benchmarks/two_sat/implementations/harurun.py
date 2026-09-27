SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library_codex)'

from library_codex.graph.TwoSAT import TwoSAT

def run(data):
    n, clauses = data
    solver = TwoSAT(n)
    for i, f, j, g in clauses:
        solver.add_clause(i, f, j, g)
    answer = solver.solve()
    possible = answer is not None
    valid = answer is None or all(answer[i] == f or answer[j] == g for i, f, j, g in clauses)
    return [possible, valid]
