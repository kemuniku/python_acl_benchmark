SOURCE = 'tatyam'
LABEL = 'tatyam-prime/acl-cpp-python (C++)'

from acl_cpp.twosat import two_sat

def run(data):
    n, clauses = data
    solver = two_sat(n)
    for i, f, j, g in clauses:
        solver.add_clause(i, f, j, g)
    possible = solver.satisfiable()
    answer = solver.answer() if possible else None
    valid = answer is None or all(answer[i] == f or answer[j] == g for i, f, j, g in clauses)
    return [possible, valid]
