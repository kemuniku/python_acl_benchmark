SOURCE = 'not522'
LABEL = 'not522/ac-library-python'

from atcoder.math import crt

def run(data):
    return [list(crt(residues, moduli)) for residues, moduli in data]
