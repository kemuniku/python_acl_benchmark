SOURCE = 'tatyam'
LABEL = 'tatyam-prime/acl-cpp-python (C++)'

from acl_cpp.string import lcp_array

def run(data):
    s, sa = data
    return lcp_array(s, sa)
