SOURCE = 'hpy'
LABEL = 'local/acl-hpy (HPy Universal + C++)'

from acl_hpy import lcp_array

def run(data):
    s, sa = data
    return lcp_array(s, sa)
