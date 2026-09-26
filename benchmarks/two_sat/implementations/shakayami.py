SOURCE = 'shakayami'
LABEL = 'shakayami/ACL-for-python'

from two_sat import two_sat

def run(data):
    n, clauses = data
    answer = two_sat(n, clauses)
    valid = answer is None or all(answer[i] == f or answer[j] == g for i, f, j, g in clauses)
    return [answer is not None, valid]
