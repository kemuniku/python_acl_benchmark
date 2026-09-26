import random

def make_input(size, seed):
    rng = random.Random(seed)
    values = [rng.randrange(-1000, 1001) for _ in range(size)]
    operations = []
    for i in range(4 * size):
        if i % 2 == 0:
            operations.append((0, rng.randrange(size), rng.randrange(-1000, 1001)))
        else:
            left = rng.randrange(size + 1)
            operations.append((1, left, rng.randrange(left, size + 1)))
    return values, operations

def oracle(data):
    initial, operations = data
    values = initial[:]
    result = []
    for kind, a, b in operations:
        if kind == 0:
            values[a] = b
        else:
            result.append(sum(values[a:b]))
    return result

def validation_cases():
    return [(data, oracle(data)) for data in [make_input(n, seed) for n in (1, 2, 7, 19) for seed in (0, 42)]]
