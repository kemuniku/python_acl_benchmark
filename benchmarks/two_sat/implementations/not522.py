SOURCE = 'not522'
LABEL = 'not522/ac-library-python'

from atcoder.twosat import TwoSAT

def run(data):
    n, clauses = data
    solver = TwoSAT(n)
    for i, f, j, g in clauses:
        solver.add_clause(i, f, j, g)
    possible = solver.satisfiable()
    answer = solver.answer() if possible else None
    valid = answer is None or all(answer[i] == f or answer[j] == g for i, f, j, g in clauses)
    return [possible, valid]
