SOURCE = 'not522'
LABEL = 'not522/ac-library-python'

from atcoder.dsu import DSU

def run(data):
    n, operations = data
    tree = DSU(n)
    result = []
    for kind, a, b in operations:
        if kind == 0:
            tree.merge(a, b)
        else:
            result.append(tree.same(a, b))
    return result
