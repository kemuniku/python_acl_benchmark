SOURCE = 'not522'
LABEL = 'not522/ac-library-python'

from atcoder.fenwicktree import FenwickTree

def run(data):
    n, operations = data
    tree = FenwickTree(n)
    result = []
    for kind, a, b in operations:
        if kind == 0:
            tree.add(a, b)
        else:
            result.append(tree.sum(a, b))
    return result
