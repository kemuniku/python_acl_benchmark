SOURCE = 'cffi'
LABEL = 'CFFI Ordered Set (AVL)'

from acl_cffi import ordered_set

def run(data):
    initial, queries = data
    output = []
    with ordered_set() as tree:
        add, discard, kth = tree.add, tree.discard, tree.kth
        count_leq, le, ge = tree.count_leq, tree.le, tree.ge
        for value in initial:
            add(value)
        for kind, x in queries:
            if kind == 0:
                add(x)
            elif kind == 1:
                discard(x)
            elif kind == 2:
                output.append(kth(x))
            elif kind == 3:
                output.append(count_leq(x))
            elif kind == 4:
                output.append(le(x))
            else:
                output.append(ge(x))
    return output
