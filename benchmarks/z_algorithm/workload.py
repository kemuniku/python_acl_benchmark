import random

def make_input(size, seed):
    rng = random.Random(seed)
    return ''.join(rng.choice('aaaabbbbcccdde') for _ in range(size))

def oracle(data):
    result = []
    for i in range(len(data)):
        common = 0
        while i + common < len(data) and data[common] == data[i + common]:
            common += 1
        result.append(common)
    return result

def validation_cases():
    cases = ['', 'a', 'aaaaaa', 'banana', 'abababab', 'mississippi']
    cases += [make_input(n, 42) for n in (2, 7, 41, 100)]
    return [(data, oracle(data)) for data in cases]
