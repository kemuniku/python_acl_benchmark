SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library)'

from library.SegTree.BIT import BIT

def run(data):
    n, operations = data
    tree = BIT(n)
    result = []
    for kind, a, b in operations:
        if kind == 0:
            tree.add(a, b)
        else:
            result.append(tree.sum(a, b))
    return result
