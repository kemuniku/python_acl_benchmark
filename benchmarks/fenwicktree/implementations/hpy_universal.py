SOURCE = 'hpy'
LABEL = 'local/acl-hpy (HPy Universal + C++)'

from acl_hpy import fenwick_tree

def run(data):
    n, operations = data
    with fenwick_tree(n) as tree:
        result = []
        for kind, a, b in operations:
            if kind == 0:
                tree.add(a, b)
            else:
                result.append(tree.sum(a, b))
        return result
