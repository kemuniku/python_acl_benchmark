SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library)'

from library.string.string import lcp_array

def run(data):
    s, sa = data
    return lcp_array(s, sa)
