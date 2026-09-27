"""Measure standalone C++ ACL and attach explicitly marked PyPy references."""
from array import array
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import statistics
import subprocess
import tempfile

from .cffi_build import toolchain_environment
from .runner import ROOT, discover, read_json, runtime_info, write_json
from .sources import _native_key, prepare, source_specs
from .worker import checksum, load_module

CASES = frozenset(("dsu", "fenwicktree", "segtree", "lazysegtree", "convolution",
                   "crt", "floor_sum", "scc", "two_sat", "maxflow", "mincostflow",
                   "suffix_array", "lcp_array", "z_algorithm"))
LABEL = "C++ ACL（参考用）"
NOTE = ("参考用：C++内で初期化・操作ループ・結果作成を計測。"
        "Pythonとの値変換・プロセス起動・入出力は計測値に含みません。")
FLAGS = ["-std=c++17", "-O3", "-DNDEBUG", "-march=native"]


def build(root=ROOT):
    root = Path(root).resolve()
    spec = source_specs(root)["cpp"]
    checkout = prepare(root, ["cpp"])["cpp"]
    environment = toolchain_environment()
    compiler = environment["compilers"]["CXX"]["command"]
    flags = FLAGS + shlex.split(os.environ.get("CPPFLAGS", "")) + shlex.split(os.environ.get("CXXFLAGS", ""))
    link_flags = shlex.split(os.environ.get("LDFLAGS", ""))
    info = {"source": spec, "environment": environment, "flags": flags, "link_flags": link_flags,
            "native_key": _native_key(spec)}
    source = root / "acl_cpp" / "benchmark.cpp"
    digest = hashlib.sha256(json.dumps(info, sort_keys=True).encode() + source.read_bytes())
    digest.update(Path(__file__).read_bytes())
    target = root / ".cache" / "cpp-reference" / digest.hexdigest()[:20]
    binary = target / "acl-reference"
    marker = target / ".bench-install-ready"
    if not marker.exists() or not binary.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="build-", dir=target.parent) as directory:
            staged = Path(directory) / "output"
            staged.mkdir()
            subprocess.run(compiler + flags + ["-I", str(checkout), str(source),
                           "-o", str(staged / binary.name)] + link_flags, check=True)
            write_json(staged / marker.name, info)
            if target.exists():
                shutil.rmtree(target)
            staged.rename(target)
    return binary, dict(info, binary_key=digest.hexdigest())


def encode(name, data):
    """Host-endian int64 words; only consumed by a child on this same machine."""
    words = array("q")
    if words.itemsize != 8:
        raise RuntimeError("C++ reference requires 64-bit array('q') words")

    def vector(values):
        if isinstance(values, str):
            values = values.encode("ascii")
        words.append(len(values))
        words.extend(values)

    def rows(values):
        words.append(len(values))
        for row in values:
            words.extend(row)

    if name in ("dsu", "fenwicktree", "scc", "two_sat"):
        words.append(data[0]); rows(data[1])
    elif name == "segtree":
        vector(data[0]); rows(data[1])
    elif name == "lazysegtree":
        rows(data[0]); rows(data[1])
    elif name in ("convolution", "lcp_array"):
        vector(data[0]); vector(data[1])
    elif name in ("suffix_array", "z_algorithm"):
        vector(data)
    elif name == "floor_sum":
        rows(data)
    elif name == "crt":
        words.append(len(data))
        for residues, moduli in data:
            vector(residues); vector(moduli)
    elif name in ("maxflow", "mincostflow"):
        n, edges, source, sink = data
        words.extend((n, source, sink)); rows(edges)
    else:
        raise ValueError("No C++ reference for case: " + name)
    return words.tobytes()


def invoke(binary, name, data, settings, validate=False):
    payload = encode(name, data)
    args = [str(binary), name, "validate" if validate else "measure"]
    args += [str(settings[key]) for key in ("repeat", "warmup", "warmup_seconds", "sample_seconds")]
    process = subprocess.run(args, input=payload, capture_output=True, timeout=settings["timeout"])
    if process.returncode:
        raise RuntimeError("C++ reference failed: " + process.stderr.decode(errors="replace"))
    return json.loads(process.stdout)


def validate(binary, name, workload, settings):
    validation = list(workload.validation_cases())
    if not validation:
        raise ValueError("C++ reference requires independent validation cases")
    for data, expected in validation:
        actual = invoke(binary, name, data, settings, validate=True)
        if checksum(actual) != checksum(expected):
            raise RuntimeError("C++ reference validation failed: " + name)


def measure_point(binary, name, workload, size, settings):
    data = workload.make_input(size, settings["seed"])
    result = invoke(binary, name, data, settings)
    samples = result["samples"]
    if (len(samples) != settings["repeat"] or
            any(type(t) not in (int, float) or not math.isfinite(t) or t <= 0 for t in samples)):
        raise RuntimeError("Invalid C++ timing samples: " + name)
    return {"size": size, "samples": samples, "median": statistics.median(samples),
            "min": min(samples), "max": max(samples), "loops": result["loops"],
            "warmup_runs": result["warmup_runs"], "checksum": checksum(result["output"]),
            "input_checksum": checksum(data)}


def check_outputs(reference, record):
    """Compare every overlapping size with every saved Python implementation."""
    reference_points = {p["size"]: p for p in reference["points"]}
    for series in record["series"]:
        for point in series["points"]:
            other = reference_points.get(point["size"])
            if other and (other["checksum"] != point["checksum"] or
                          ("input_checksum" in point and other["input_checksum"] != point["input_checksum"])):
                raise RuntimeError("C++/Python result mismatch: %s/%s n=%s" %
                                   (record["case"], series["id"], point["size"]))


def reference_key(root, case, settings, build_info):
    payload = {"settings": settings, "build": build_info, "host": runtime_info()}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode())
    digest.update((case["path"] / "workload.py").read_bytes())
    digest.update(Path(__file__).read_bytes())
    return digest.hexdigest()


def attach(results, selected=None, force=False, root=ROOT):
    """Preserve all Python samples; only replace the standalone reference field."""
    root, results = Path(root).resolve(), Path(results).resolve()
    cases = discover(root)
    selected = set(selected) if selected else CASES & set(cases)
    if selected - CASES or selected - set(cases):
        raise ValueError("Unsupported C++ reference cases: " + ", ".join(sorted(selected - (CASES & set(cases)))))
    paths = [(name, results / "pypy" / (name + ".json")) for name in sorted(selected)]
    paths = [(name, path) for name, path in paths if path.exists()]
    if not paths:
        raise ValueError("No saved PyPy results to annotate in " + str(results / "pypy"))
    binary, build_info = build(root)
    host = runtime_info()
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True)
    measured = 0
    for name, path in paths:
        case, record = cases[name], read_json(path)
        if record["runtime"]["id"] != "pypy" or record["case"] != name:
            raise ValueError("Expected a PyPy result: " + str(path))
        # Do not silently overlay timings taken on another CPU/OS.
        for field in ("cpu", "machine", "platform"):
            if record["runtime"].get(field) != host.get(field):
                raise ValueError("C++ reference host differs from saved PyPy results: " + field)
        settings = dict(record["settings"])
        key = reference_key(root, case, settings, build_info)
        previous = next((r for r in record.get("references", []) if r.get("id") == "cpp_acl"), None)
        if not force and previous and previous.get("fingerprint") == key:
            check_outputs(previous, record)
            print("SKIP cpp-reference/" + name + " (unchanged)", flush=True)
            continue
        workload = load_module("_cpp_workload_" + name, case["path"] / "workload.py")
        validate(binary, name, workload, settings)
        reference = {
            "id": "cpp_acl", "label": LABEL, "reference": True, "note": NOTE,
            "runtime": dict(host, id="cpp", implementation="C++", version="17", executable=str(binary),
                            build=build_info["environment"]["compilers"]["CXX"]["version"].splitlines()[0]
                                  + " | " + " ".join(build_info["flags"]),
                            cpp_build=build_info),
            "settings": settings, "sources": {"cpp": source_specs(root)["cpp"]},
            "commit": revision.stdout.strip() if revision.returncode == 0 else "uncommitted",
            "fingerprint": key, "points": [], "timeouts": [],
        }
        for size in settings["sizes"]:
            print("RUN cpp-reference/%s n=%d" % (name, size), flush=True)
            try:
                point = measure_point(binary, name, workload, size, settings)
            except subprocess.TimeoutExpired:
                reference["timeouts"].append({"size": size, "timeout_seconds": settings["timeout"]})
                print("TIMEOUT cpp-reference/%s n=%d" % (name, size), flush=True)
            else:
                reference["points"].append(point)
        check_outputs(reference, record)
        reference["measured_at"] = datetime.now(timezone.utc).isoformat()
        record["references"] = [r for r in record.get("references", []) if r.get("id") != "cpp_acl"] + [reference]
        write_json(path, record)
        measured += 1
    return measured
