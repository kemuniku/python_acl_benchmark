SOURCE = 'cffi'
LABEL = 'local/acl-cffi (batched operations)'

from acl_cffi import fenwick_tree


def run(data):
    n, operations = data
    with fenwick_tree(n) as tree:
        return tree.process(operations)
