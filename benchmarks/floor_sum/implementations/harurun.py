SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library_codex)'

from library_codex.number_theory.FloorSum import floor_sum

def run(data):
    return [floor_sum(n, m, a, b) for n, m, a, b in data]
