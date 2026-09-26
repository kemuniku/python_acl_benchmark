import itertools
import random

def make_input(size, seed):
    rng = random.Random(seed)
    source, sink = 2 * size, 2 * size + 1
    edges = [(source, i, 1) for i in range(size)]
    edges += [(size + i, sink, 1) for i in range(size)]
    edges += [(i, size + rng.randrange(size), 1) for i in range(size) for _ in range(4)]
    return 2 * size + 2, edges, source, sink

def oracle(data):
    n, edges, source, sink = data
    middle = [i for i in range(n) if i not in (source, sink)]
    best = sum(cap for a, b, cap in edges)
    for choices in itertools.product((False, True), repeat=len(middle)):
        reachable = {source} | {i for i, chosen in zip(middle, choices) if chosen}
        best = min(best, sum(cap for a, b, cap in edges if a in reachable and b not in reachable))
    return best

def validation_cases():
    cases = [(2, [], 0, 1), (4, [(0, 1, 3), (0, 2, 2), (1, 2, 1), (1, 3, 2), (2, 3, 3)], 0, 3)]
    cases += [make_input(n, seed) for n in (1, 2, 4) for seed in (0, 42)]
    return [(data, oracle(data)) for data in cases]
