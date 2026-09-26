import random

def make_input(size, seed):
    rng = random.Random(seed)
    return [(rng.randrange(1, 10**6), rng.randrange(1, 10**6), rng.randrange(10**6), rng.randrange(10**6)) for _ in range(size)]

def validation_cases():
    rng = random.Random(42)
    values = [(1, 1, 0, 0), (5, 7, 3, 2), (7, 1, 100, 42)]
    values += [(rng.randrange(1, 50), rng.randrange(1, 50), rng.randrange(100), rng.randrange(100)) for _ in range(100)]
    return [(values, [sum((a * i + b) // m for i in range(n)) for n, m, a, b in values])]
