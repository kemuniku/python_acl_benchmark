import itertools
import random

def make_input(size, seed):
    rng = random.Random(seed)
    answer = [bool(rng.randrange(2)) for _ in range(size)]
    clauses = []
    for _ in range(4 * size):
        # Keep connected components small to avoid recursive implementation stack limits.
        i = rng.randrange(size)
        start = (i // 32) * 32
        j = rng.randrange(start, min(size, start + 32))
        f, g = bool(rng.randrange(2)), bool(rng.randrange(2))
        if answer[i] != f and answer[j] != g:
            f = answer[i]
        clauses.append((i, f, j, g))
    return size, clauses

def oracle(data):
    n, clauses = data
    satisfiable = any(all(answer[i] == f or answer[j] == g for i, f, j, g in clauses)
                      for answer in itertools.product((False, True), repeat=n))
    return [satisfiable, True]

def validation_cases():
    cases = [(0, []), (1, [(0, True, 0, True), (0, False, 0, False)]),
             (2, [(0, True, 1, False), (0, False, 1, True)])]
    cases += [make_input(n, seed) for n in (1, 3, 7) for seed in (0, 42)]
    return [(data, oracle(data)) for data in cases]
