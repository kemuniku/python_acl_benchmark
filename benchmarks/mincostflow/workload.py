import itertools
import random

def make_input(size, seed):
    rng = random.Random(seed)
    source, sink = 2 * size, 2 * size + 1
    edges = [(source, i, 1, 0) for i in range(size)]
    edges += [(size + i, sink, 1, 0) for i in range(size)]
    edges += [(i, size + rng.randrange(size), 1, rng.randrange(100)) for i in range(size) for _ in range(3)]
    return 2 * size + 2, edges, source, sink

def oracle(data):
    # Exhaust all integral edge flows on tiny networks; independent of shortest paths.
    n, edges, source, sink = data
    best = (0, 0)
    for amounts in itertools.product(*(range(cap + 1) for a, b, cap, cost in edges)):
        balance = [0] * n
        cost = 0
        for (a, b, capacity, price), amount in zip(edges, amounts):
            balance[a] -= amount
            balance[b] += amount
            cost += price * amount
        if any(balance[i] for i in range(n) if i not in (source, sink)):
            continue
        flow = balance[sink]
        if flow > best[0] or (flow == best[0] and cost < best[1]):
            best = flow, cost
    return list(best)

def validation_cases():
    cases = [(2, [], 0, 1),
             (4, [(0, 1, 2, 1), (1, 3, 1, 4), (0, 2, 1, 2), (2, 3, 2, 1), (1, 2, 1, 0)], 0, 3)]
    cases += [make_input(n, seed) for n in (1, 2) for seed in (0, 42)]
    return [(data, oracle(data)) for data in cases]
