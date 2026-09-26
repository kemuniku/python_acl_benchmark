SOURCE = 'shakayami'
LABEL = 'shakayami/ACL-for-python'

from operator import add
from segtree import segtree

def run(data):
    initial, operations = data
    tree = segtree(initial, add, 0)
    result = []
    for kind, a, b in operations:
        if kind == 0:
            tree.set(a, b)
        else:
            result.append(tree.prod(a, b))
    return result
