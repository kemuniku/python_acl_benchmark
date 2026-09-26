"""Copy this directory to benchmarks/<case_name>/ to add a comparison.

Every implementation receives the same JSON-serializable input and must return
the same JSON-serializable result. Input generation runs outside the timer.
"""

import random


def make_input(n, seed):
    rng = random.Random(seed)
    return {"values": [rng.randrange(-1000, 1001) for _ in range(n)]}


def validation_cases():
    """Independent expected answers; do not call the benchmark implementation."""
    return [
        ({"values": []}, []),
        ({"values": [7]}, [7]),
        ({"values": [3, -5, 0, 8, -2]}, [3, -2, -2, 6, 4]),
        ({"values": [10**20, 1, -(10**20)]}, [10**20, 10**20 + 1, 1]),
    ]
