SOURCE = 'cffi'
LABEL = 'local/acl-cffi (CFFI + C++)'

from acl_cffi import floor_sum

def run(data):
    return [floor_sum(n, m, a, b) for n, m, a, b in data]
