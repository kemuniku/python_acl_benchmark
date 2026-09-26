SOURCE = 'cffi'
LABEL = 'local/acl-cffi (CFFI + C++)'

from acl_cffi import dsu

def run(data):
    n, operations = data
    with dsu(n) as tree:
        result = []
        for kind, a, b in operations:
            if kind == 0:
                tree.merge(a, b)
            else:
                result.append(tree.same(a, b))
        return result
