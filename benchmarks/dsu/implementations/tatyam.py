SOURCE = 'tatyam'
LABEL = 'tatyam-prime/acl-cpp-python (C++)'

from acl_cpp.dsu import dsu

def run(data):
    n, operations = data
    tree = dsu(n)
    result = []
    for kind, a, b in operations:
        if kind == 0:
            tree.merge(a, b)
        else:
            result.append(tree.same(a, b))
    return result
