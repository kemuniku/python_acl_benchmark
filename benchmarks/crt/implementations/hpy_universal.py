SOURCE = 'hpy'
LABEL = 'local/acl-hpy (HPy Universal + C++)'

from acl_hpy import crt

def run(data):
    return [list(crt(residues, moduli)) for residues, moduli in data]
