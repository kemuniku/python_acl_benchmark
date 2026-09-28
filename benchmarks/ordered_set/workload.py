"""Exact ordered_set inputs and expected outputs from Library Checker."""
import bisect
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def prepare_fixture(checkout):
    """Run the pinned upstream generator, including its SHA-256 fixture check."""
    checkout = Path(checkout)
    result = subprocess.run([sys.executable, "generate.py", "-p", "ordered_set"],
                            cwd=checkout, text=True, capture_output=True)
    problem = checkout / "data_structure" / "ordered_set"
    expected = json.loads((problem / "hash.json").read_text())
    if any(not (problem / name.rsplit(".", 1)[-1] / name).is_file() for name in expected):
        raise RuntimeError("Official testcase generation failed:\n" + result.stderr[-4000:])

    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

    # The upstream generator/solution can produce a different result for a few
    # cases on a first run. Regenerate just those cases until the official
    # hash.json matches; never benchmark or accept a different input/output.
    for filename, sha in sorted(expected.items(), key=lambda entry: (entry[0].endswith(".out"), entry[0])):
        extension = filename.rsplit(".", 1)[-1]
        target = problem / extension / filename
        if digest(target) == sha:
            continue
        case = filename.rsplit(".", 1)[0]
        generator, _, number = case.rpartition("_")
        if extension == "in":
            src = problem / "gen" / generator
            command = ([str(src), str(int(number))] if src.is_file() else ["cat", str(problem / "gen" / (case + ".in"))])
        else:
            command = [str(problem / "sol" / "correct")]
        for _ in range(12):
            temporary = target.with_suffix(".retry")
            try:
                with temporary.open("wb") as output:
                    with (problem / "in" / (case + ".in")).open("rb") if extension == "out" else open(os.devnull, "rb") as input_file:
                        subprocess.run(command, stdin=input_file, stdout=output, check=True)
                if digest(temporary) == sha:
                    temporary.replace(target)
                    break
            finally:
                temporary.unlink(missing_ok=True)
        else:
            raise RuntimeError("Official fixture hash mismatch: " + filename)
    actual = {path.name: digest(path) for extension in ("in", "out")
              for path in (problem / extension).glob("*." + extension)}
    if expected != actual:
        raise RuntimeError("Official ordered_set fixtures do not match hash.json")
    if result.returncode:
        print("Recovered upstream generator hash mismatch using official hashes", file=sys.stderr)


def _fixture(size, extension):
    checkout = Path(os.environ["ACL_BENCH_FIXTURES"])
    names = json.loads((Path(__file__).parent / "case.json").read_text())["case_names"]
    if not 1 <= size <= len(names):
        raise ValueError("Unknown ordered_set case index")
    folder = "in" if extension == "in" else "out"
    return checkout / "data_structure" / "ordered_set" / folder / (names[size - 1] + "." + extension)


def make_input(size, seed):
    del seed  # The pinned official generator chooses the seed for each named case.
    with _fixture(size, "in").open() as stream:
        n, q = map(int, stream.readline().split())
        initial = list(map(int, stream.readline().split()))
        queries = [tuple(map(int, stream.readline().split())) for _ in range(q)]
    if len(initial) != n or len(queries) != q:
        raise ValueError("Incomplete official ordered_set input")
    return initial, queries


def expected_output(size):
    return [int(line) for line in _fixture(size, "out").read_text().splitlines()]


def oracle(data):
    initial, queries = data
    tree = sorted(set(initial))
    output = []
    for kind, x in queries:
        left = bisect.bisect_left(tree, x)
        if kind == 0:
            if left == len(tree) or tree[left] != x:
                tree.insert(left, x)
        elif kind == 1:
            if left < len(tree) and tree[left] == x:
                tree.pop(left)
        elif kind == 2:
            output.append(tree[x - 1] if x <= len(tree) else -1)
        elif kind == 3:
            output.append(bisect.bisect_right(tree, x))
        elif kind == 4:
            index = bisect.bisect_right(tree, x) - 1
            output.append(tree[index] if index >= 0 else -1)
        elif kind == 5:
            output.append(tree[left] if left < len(tree) else -1)
    return output


def validation_cases():
    cases = [([], [(0, 7), (0, 7), (3, 7), (2, 1), (2, 2), (4, 6),
                    (4, 7), (5, 8), (1, 8), (1, 7), (2, 1), (3, 7)]),
             ([0, 10, 1000000000], [(2, 3), (3, 0), (4, 0), (5, 1000000000),
                                     (1, 0), (0, 0), (5, 1), (4, 999999999)]),
             ([], [(2, 1), (3, 0), (4, 0), (5, 0)])]
    return [(data, oracle(data)) for data in cases]
