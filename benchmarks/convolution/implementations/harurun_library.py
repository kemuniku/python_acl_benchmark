SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library)'

from library.convolution.multiply import multiply

def run(data):
    a, b = data
    if not a or not b:
        return []
    return multiply(a, b)
