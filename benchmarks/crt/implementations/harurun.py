SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library_codex)'

from library_codex.number_theory.ChineseRemainder import chinese_remainder as crt

def run(data):
    return [list(crt(residues, moduli)) for residues, moduli in data]
