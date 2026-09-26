SOURCE = 'shakayami'
LABEL = 'shakayami/ACL-for-python'

from convolution import FFT

def run(data):
    a, b = data
    return FFT(998244353).convolution(a, b)
