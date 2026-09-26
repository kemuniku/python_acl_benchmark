"""One fresh process per implementation and input size."""
import contextlib
import copy
import gc
import hashlib
import importlib.util
import json
import statistics
import sys
import tempfile
import time
from pathlib import Path


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def checksum(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def measure(request):
    case_path = Path(request["case_path"])
    adapter_path = Path(request["adapter_path"])
    sys.path[:0] = [str(adapter_path.parent), str(case_path)]
    if request["source_path"]:
        sys.path.insert(0, request["source_path"])
    workload = load_module("_benchmark_workload", case_path / "workload.py")
    adapter = load_module("_benchmark_adapter", adapter_path)
    validation = list(workload.validation_cases())
    if not validation:
        raise ValueError("validation_cases() must contain at least one independent expected result")
    for data, expected in validation:
        actual = adapter.run(copy.deepcopy(data))
        if checksum(actual) != checksum(expected):
            raise ValueError("Correctness check failed: expected %r, got %r" % (expected, actual))
    settings = request["settings"]
    data = workload.make_input(request["size"], settings["seed"])
    input_checksum = checksum(data)
    function = adapter.run
    baseline = checksum(function(data))
    warmed = 0
    warmup_start = time.perf_counter()
    while warmed < settings["warmup"] or time.perf_counter() - warmup_start < settings["warmup_seconds"]:
        value = function(data)
        if checksum(value) != baseline:
            raise ValueError("Non-deterministic output during warmup")
        warmed += 1
    started = time.perf_counter()
    function(data)
    elapsed = time.perf_counter() - started
    loops = min(10000, max(1, int(settings["sample_seconds"] / max(elapsed, 1e-9))))
    samples = []
    for _ in range(settings["repeat"]):
        gc.collect()
        started = time.perf_counter_ns()
        for _ in range(loops):
            value = function(data)
        seconds = (time.perf_counter_ns() - started) / 1e9 / loops
        if checksum(value) != baseline:
            raise ValueError("Non-deterministic output during measurement")
        samples.append(seconds)
    if checksum(data) != input_checksum:
        raise ValueError("run(data) must not mutate its input; create fresh state inside run")
    return {
        "size": request["size"], "median": statistics.median(samples),
        "min": min(samples), "max": max(samples), "samples": samples,
        "checksum": baseline, "loops": loops, "warmup_runs": warmed,
    }


def main():
    request = json.load(sys.stdin)
    # Timestamp-based .pyc validation can miss same-size edits within one second.
    # An empty private cache prefix forces fresh source imports, including helpers,
    # while leaving the user's existing bytecode cache untouched. -B alone only
    # disables cache writes and would still allow stale cache reads.
    previous_prefix = sys.pycache_prefix
    previous_write_setting = sys.dont_write_bytecode
    with tempfile.TemporaryDirectory(prefix="acl-bytecode-") as bytecode:
        try:
            sys.pycache_prefix = bytecode
            sys.dont_write_bytecode = True
            with contextlib.redirect_stdout(sys.stderr):
                result = measure(request)
        finally:
            sys.pycache_prefix = previous_prefix
            sys.dont_write_bytecode = previous_write_setting
    print(json.dumps(result))


if __name__ == "__main__":
    main()
