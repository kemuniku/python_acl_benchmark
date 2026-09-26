import math
import random

def make_input(size, seed):
    rng = random.Random(seed)
    data = []
    for _ in range(size):
        moduli = [rng.choice((97, 101, 103, 107, 109, 111)) for _ in range(4)]
        residues = [rng.randrange(m) for m in moduli]
        data.append((residues, moduli))
    return data

def oracle(data):
    result = []
    for residues, moduli in data:
        period = 1
        for m in moduli:
            period = period * m // math.gcd(period, m)
        answer = next((x for x in range(period) if all(x % m == r % m for r, m in zip(residues, moduli))), None)
        result.append([0, 0] if answer is None else [answer, period])
    return result

def validation_cases():
    rng = random.Random(42)
    data = [([], []), ([2, 3], [3, 5]), ([1, 0], [2, 2]), ([-1, 2], [3, 5])]
    for _ in range(50):
        moduli = [rng.randrange(1, 9) for _ in range(3)]
        data.append(([rng.randrange(-8, 9) for _ in moduli], moduli))
    return [(data, oracle(data))]
