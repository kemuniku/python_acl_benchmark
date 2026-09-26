import random

def make_input(size, seed):
    rng = random.Random(seed)
    edges = []
    # Bounded block depth keeps this workload usable for recursive PyPy ports.
    for _ in range(4 * size):
        a = rng.randrange(size)
        start = (a // 32) * 32
        b = rng.randrange(start, min(size, start + 32))
        if rng.randrange(4) == 0:
            b = rng.randrange(a, size)
        edges.append((a, b))
    return size, edges

def oracle(data):
    n, edges = data
    reachable = [[i == j for j in range(n)] for i in range(n)]
    for a, b in edges:
        reachable[a][b] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reachable[i][j] = reachable[i][j] or (reachable[i][k] and reachable[k][j])
    remaining = set(range(n))
    groups = []
    while remaining:
        a = min(remaining)
        group = sorted(b for b in remaining if reachable[a][b] and reachable[b][a])
        groups.append(group)
        remaining.difference_update(group)
    return groups

def validation_cases():
    cases = [(0, []), (4, []), (5, [(0, 1), (1, 0), (1, 2), (2, 3), (3, 2), (3, 4)])]
    cases += [make_input(n, seed) for n in (1, 7, 19, 35) for seed in (0, 42)]
    return [(data, oracle(data)) for data in cases]
