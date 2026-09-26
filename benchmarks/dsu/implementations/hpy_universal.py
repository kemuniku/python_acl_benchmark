SOURCE = 'hpy'
LABEL = 'local/acl-hpy (HPy Universal + C++)'

from acl_hpy import dsu

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
