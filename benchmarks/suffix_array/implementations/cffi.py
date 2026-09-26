SOURCE = 'cffi'
LABEL = 'local/acl-cffi (CFFI + C++)'

from acl_cffi import suffix_array

def run(data):
    return suffix_array(data)
