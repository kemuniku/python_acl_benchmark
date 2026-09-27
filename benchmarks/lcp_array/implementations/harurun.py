SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library_codex)'

from library_codex.string.SuffixArray import lcp_array

def run(data):
    s, sa = data
    return lcp_array(s, sa)
