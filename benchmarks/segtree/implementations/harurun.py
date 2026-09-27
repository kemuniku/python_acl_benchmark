SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library_codex)'

from operator import add
from library_codex.segment_tree.SegTree import SegTree

def run(data):
    initial, operations = data
    tree = SegTree(add, 0, initial)
    result = []
    for kind, a, b in operations:
        if kind == 0:
            tree.set(a, b)
        else:
            result.append(tree.prod(a, b))
    return result
