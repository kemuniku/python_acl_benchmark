import random

def suffix_array_doubling(s):
    # Independent input preparation; no compared library runs outside its adapter.
    n = len(s)
    sa = list(range(n))
    rank = [ord(c) for c in s]
    width = 1
    while width < n:
        def key(i):
            return rank[i], rank[i + width] if i + width < n else -1
        sa.sort(key=key)
        updated = [0] * n
        for i in range(1, n):
            updated[sa[i]] = updated[sa[i - 1]] + (key(sa[i - 1]) != key(sa[i]))
        rank = updated
        if rank[sa[-1]] == n - 1:
            break
        width *= 2
    return sa

def make_input(size, seed):
    rng = random.Random(seed)
    s = ''.join(rng.choice('aaaabbbbcccdde') for _ in range(size))
    return s, suffix_array_doubling(s)

def oracle(data):
    s, sa = data
    result = []
    for a, b in zip(sa, sa[1:]):
        common = 0
        while a + common < len(s) and b + common < len(s) and s[a + common] == s[b + common]:
            common += 1
        result.append(common)
    return result

def validation_cases():
    cases = [(s, sorted(range(len(s)), key=lambda i: s[i:])) for s in ('a', 'aaaaaa', 'banana', 'mississippi')]
    cases += [make_input(n, 42) for n in (2, 7, 41, 100)]
    return [(data, oracle(data)) for data in cases]
