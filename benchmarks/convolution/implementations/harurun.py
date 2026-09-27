SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library_codex)'

from library_codex.convolution.NTT998 import multiply

def run(data):
    a, b = data
    return multiply(a, b)
