SOURCE = 'hpy'
LABEL = 'local/acl-hpy (HPy Universal + C++)'

from acl_hpy import floor_sum

def run(data):
    return [floor_sum(n, m, a, b) for n, m, a, b in data]
