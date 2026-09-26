SOURCE = 'not522'
LABEL = 'not522/ac-library-python'

from atcoder.string import lcp_array

def run(data):
    s, sa = data
    return lcp_array(s, sa)
