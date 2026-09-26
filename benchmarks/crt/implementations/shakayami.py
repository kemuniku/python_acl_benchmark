SOURCE = 'shakayami'
LABEL = 'shakayami/ACL-for-python'

from acl_math import crt

def run(data):
    return [list(crt(residues, moduli)) for residues, moduli in data]
