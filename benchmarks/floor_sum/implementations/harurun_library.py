SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library)'

from library.number_theory.floor_sum import floor_sum

def run(data):
    return [floor_sum(n, m, a, b) for n, m, a, b in data]
