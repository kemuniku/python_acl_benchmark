SOURCE = 'hpy'
LABEL = 'local/acl-hpy (HPy Universal + C++)'

from acl_hpy import two_sat

def run(data):
    n, clauses = data
    with two_sat(n) as solver:
        for i, f, j, g in clauses:
            solver.add_clause(i, f, j, g)
        possible = solver.satisfiable()
        answer = solver.answer() if possible else None
        valid = answer is None or all(answer[i] == f or answer[j] == g for i, f, j, g in clauses)
        return [possible, valid]
