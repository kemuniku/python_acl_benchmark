SOURCE = 'tatyam'
LABEL = 'tatyam-prime/acl-cpp-python (C++)'

from acl_cpp.math import crt

def run(data):
    return [list(crt(residues, moduli)) for residues, moduli in data]
