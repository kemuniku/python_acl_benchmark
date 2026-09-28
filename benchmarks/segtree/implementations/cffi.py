SOURCE = 'cffi'
LABEL = 'CFFI Segment Tree (Python op)'

from operator import add
from acl_cffi import segtree


def run(data):
    initial, operations = data
    result = []
    with segtree(add, 0, initial) as tree:
        for kind, a, b in operations:
            if kind == 0:
                tree.set(a, b)
            else:
                result.append(tree.prod(a, b))
    return result
