SOURCE = 'hpy'
LABEL = 'local/acl-hpy (HPy Universal + C++)'

from acl_hpy import z_algorithm

def run(data):
    return z_algorithm(data)
