SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library_codex)'

from library_codex.segment_tree.LazySegTree import LazySegTree

def op(a, b):
    return a[0] + b[0], a[1] + b[1]

def mapping(f, value, length):
    return value[0] + f * value[1], value[1]

def composition(f, g):
    return f + g

def run(data):
    initial, operations = data
    tree = LazySegTree(op, (0, 0), mapping, composition, 0, initial)
    result = []
    for kind, left, right, amount in operations:
        if kind == 0:
            tree.apply(left, right, amount)
        else:
            result.append(tree.prod(left, right)[0])
    return result
