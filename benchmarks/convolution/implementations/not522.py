SOURCE = 'not522'
LABEL = 'not522/ac-library-python'

from atcoder.convolution import convolution

def run(data):
    a, b = data
    return convolution(998244353, a, b)
