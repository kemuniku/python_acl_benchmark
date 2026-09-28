SOURCE = 'cffi'
LABEL = 'CFFI Ordered Set (AVL)'

from acl_cffi import ordered_set

def run(data):
    initial, queries = data
    output = []
    with ordered_set() as tree:
        for value in initial:
            tree.add(value)
        for kind, x in queries:
            if kind == 0:
                tree.add(x)
            elif kind == 1:
                tree.discard(x)
            elif kind == 2:
                output.append(tree.kth(x))
            elif kind == 3:
                output.append(tree.count_leq(x))
            elif kind == 4:
                output.append(tree.le(x))
            else:
                output.append(tree.ge(x))
    return output
