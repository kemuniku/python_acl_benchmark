SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library)'

from library.graph.twosat import twosat

def run(data):
    n, clauses = data
    literals = [(i if f else ~i, j if g else ~j) for i, f, j, g in clauses]
    answer = twosat(n, literals)
    possible = answer is not None
    valid = answer is None or all(answer[i] == f or answer[j] == g for i, f, j, g in clauses)
    return [possible, valid]
