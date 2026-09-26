SOURCE = 'cffi'
LABEL = 'local/acl-cffi (CFFI + C++)'

from acl_cffi import convolution998244353

def run(data):
    a, b = data
    return convolution998244353(a, b)
