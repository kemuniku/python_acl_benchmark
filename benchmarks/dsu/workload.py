import random

def make_input(size, seed):
    rng = random.Random(seed)
    return size, [(i % 2, rng.randrange(size), rng.randrange(size)) for i in range(4 * size)]

def oracle(data):
    n, operations = data
    labels = list(range(n))
    result = []
    for kind, a, b in operations:
        if kind == 0:
            old, new = labels[b], labels[a]
            labels = [new if label == old else label for label in labels]
        else:
            result.append(labels[a] == labels[b])
    return result

def validation_cases():
    cases = [(4, [(1, 0, 1), (0, 0, 1), (0, 2, 3), (1, 0, 1), (1, 1, 2), (0, 1, 3), (1, 0, 2)])]
    cases += [make_input(n, seed) for n in (1, 2, 7, 19) for seed in (0, 42)]
    return [(data, oracle(data)) for data in cases]
