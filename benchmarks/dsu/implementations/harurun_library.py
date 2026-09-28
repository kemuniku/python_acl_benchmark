SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library)'

from library.UnionFind.UnionFind import DSU

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
