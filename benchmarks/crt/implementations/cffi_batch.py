SOURCE = 'cffi'
LABEL = 'local/acl-cffi (batched CRT)'

from acl_cffi import crt, crt_many


def run(data):
    if any(len(residues) != 4 or len(moduli) != 4 for residues, moduli in data):
        return [list(crt(residues, moduli)) for residues, moduli in data]
    return crt_many(data)
