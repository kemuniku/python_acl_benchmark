SOURCE = 'tatyam'
LABEL = 'tatyam-prime/acl-cpp-python (C++)'

from acl_cpp.math import floor_sum

def run(data):
    return [floor_sum(n, m, a, b) for n, m, a, b in data]
