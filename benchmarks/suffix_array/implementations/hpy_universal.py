SOURCE = 'hpy'
LABEL = 'local/acl-hpy (HPy Universal + C++)'

from acl_hpy import suffix_array

def run(data):
    return suffix_array(data)
