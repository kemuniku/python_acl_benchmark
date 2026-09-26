SOURCE = 'cffi'
LABEL = 'local/acl-cffi (CFFI + C++)'

from acl_cffi import z_algorithm

def run(data):
    return z_algorithm(data)
