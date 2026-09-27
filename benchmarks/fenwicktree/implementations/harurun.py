SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library_codex)'

from library_codex.fenwick_tree.BIT import BIT as FenwickTree

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
