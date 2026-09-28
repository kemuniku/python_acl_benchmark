SOURCE = 'cffi'
LABEL = 'CFFI Lazy Segment Tree (Python callbacks)'

from acl_cffi import lazy_segtree


def op(a, b):
    return a[0] + b[0], a[1] + b[1]


def mapping(f, value):
    return value[0] + f * value[1], value[1]


def composition(f, g):
    return f + g


def run(data):
    initial, operations = data
    result = []
    with lazy_segtree(op, (0, 0), mapping, composition, 0, initial) as tree:
        for kind, left, right, amount in operations:
            if kind == 0:
                tree.apply(left, right, amount)
            else:
                result.append(tree.prod(left, right))
    return result
