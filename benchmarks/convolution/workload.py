import random
MOD = 998244353

def make_input(size, seed):
    rng = random.Random(seed)
    return [rng.randrange(MOD) for _ in range(size)], [rng.randrange(MOD) for _ in range(size)]

def oracle(data):
    a, b = data
    if not a or not b:
        return []
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] = (result[i + j] + x * y) % MOD
    return result

def validation_cases():
    cases = [([], []), ([], [1]), ([0], [5]), ([1, 2, 3], [4, 5])]
    # Cross both libraries' naive / NTT thresholds, including non powers of two.
    cases += [make_input(n, 42) for n in (1, 7, 41, 61, 67)]
    return [(data, oracle(data)) for data in cases]
