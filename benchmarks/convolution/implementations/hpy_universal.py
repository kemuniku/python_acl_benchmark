SOURCE = 'hpy'
LABEL = 'local/acl-hpy (HPy Universal + C++)'

from acl_hpy import convolution998244353

def run(data):
    a, b = data
    return convolution998244353(a, b)
