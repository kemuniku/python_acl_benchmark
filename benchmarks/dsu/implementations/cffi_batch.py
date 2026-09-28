SOURCE = 'cffi'
LABEL = 'local/acl-cffi (batched operations)'

from acl_cffi import dsu


def run(data):
    n, operations = data
    with dsu(n) as tree:
        return tree.process(operations)
