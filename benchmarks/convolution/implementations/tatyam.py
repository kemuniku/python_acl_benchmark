SOURCE = 'tatyam'
LABEL = 'tatyam-prime/acl-cpp-python (C++)'

from acl_cpp.convolution import convolution998244353

def run(data):
    a, b = data
    return convolution998244353(a, b)
