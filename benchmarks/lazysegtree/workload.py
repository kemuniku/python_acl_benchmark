import random

def make_input(size, seed):
    rng = random.Random(seed)
    initial = [(rng.randrange(-1000, 1001), 1) for _ in range(size)]
    operations = []
    for i in range(2 * size):
        left = rng.randrange(size + 1)
        right = rng.randrange(left, size + 1)
        operations.append((i % 2, left, right, rng.randrange(-1000, 1001)))
    return initial, operations

def oracle(data):
    initial, operations = data
    values = [value for value, length in initial]
    result = []
    for kind, left, right, amount in operations:
        if kind == 0:
            for i in range(left, right):
                values[i] += amount
        else:
            result.append(sum(values[left:right]))
    return result

def validation_cases():
    return [(data, oracle(data)) for data in [make_input(n, seed) for n in (1, 2, 7, 19) for seed in (0, 42)]]
