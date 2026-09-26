SOURCE = 'cffi'
LABEL = 'local/acl-cffi (CFFI + C++)'

from acl_cffi import lcp_array

def run(data):
    s, sa = data
    return lcp_array(s, sa)
