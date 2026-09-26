import random

def make_input(size, seed):
    rng = random.Random(seed)
    operations = []
    for i in range(4 * size):
        if i % 2 == 0:
            operations.append((0, rng.randrange(size), rng.randrange(-1000, 1001)))
        else:
            left = rng.randrange(size + 1)
            right = rng.randrange(left, size + 1)
            operations.append((1, left, right))
    return size, operations

def oracle(data):
    n, operations = data
    values = [0] * n
    result = []
    for kind, a, b in operations:
        if kind == 0:
            values[a] += b
        else:
            result.append(sum(values[a:b]))
    return result

def validation_cases():
    cases = [(3, [(0, 0, 5), (0, 2, -2), (1, 0, 3), (1, 1, 1), (1, 2, 3)])]
    cases += [make_input(n, seed) for n in (1, 2, 7, 19) for seed in (0, 42)]
    return [(data, oracle(data)) for data in cases]
