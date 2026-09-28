SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library)'

from library.string.Z_algorism import Z_algorism

def run(data):
    if not data:
        return []
    return Z_algorism(data)
