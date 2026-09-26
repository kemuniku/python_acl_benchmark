SOURCE = 'tatyam'
LABEL = 'tatyam-prime/acl-cpp-python (C++)'

from acl_cpp.fenwicktree import fenwick_tree

def run(data):
    n, operations = data
    tree = fenwick_tree(n)
    result = []
    for kind, a, b in operations:
        if kind == 0:
            tree.add(a, b)
        else:
            result.append(tree.sum(a, b))
    return result
