SOURCE = 'not522'
LABEL = 'not522/ac-library-python'

from operator import add
from atcoder.segtree import SegTree

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
