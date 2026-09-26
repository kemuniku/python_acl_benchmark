SOURCE = 'cffi'
LABEL = 'local/acl-cffi (CFFI + C++)'

from acl_cffi import crt

def run(data):
    return [list(crt(residues, moduli)) for residues, moduli in data]
