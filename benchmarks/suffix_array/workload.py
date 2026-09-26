import random

def make_input(size, seed):
    rng = random.Random(seed)
    return ''.join(rng.choice('aaaabbbbcccdde') for _ in range(size))

def oracle(data):
    return sorted(range(len(data)), key=lambda i: data[i:])

def validation_cases():
    cases = ['', 'a', 'aaaaaa', 'banana', 'mississippi', 'zyxwvuts']
    cases += [make_input(n, 42) for n in (2, 7, 41, 100)]
    return [(data, oracle(data)) for data in cases]
