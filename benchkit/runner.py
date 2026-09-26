"""Discover cases, invalidate affected results, and run isolated workers."""
import ast
import hashlib
import json
import math
import statistics
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def runtime_info():
    cpu = platform.processor() or platform.machine()
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    return {
        "id": platform.python_implementation().lower(),
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
        "build": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu": cpu,
        "runner_image": os.environ.get("ImageOS", "local"),
        "runner_image_version": os.environ.get("ImageVersion", "local"),
    }


def adapter_info(path):
    metadata = {"id": path.stem, "label": path.stem, "source": None, "path": path}
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id in ("SOURCE", "LABEL"):
                    value = ast.literal_eval(statement.value)
                    if not isinstance(value, str):
                        raise ValueError("%s: %s must be a string literal" % (path, target.id))
                    metadata[{"SOURCE": "source", "LABEL": "label"}[target.id]] = value
    return metadata


def discover(root=ROOT):
    cases = {}
    for config_path in sorted((root / "benchmarks").glob("*/case.json")):
        name = config_path.parent.name
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", name):
            raise ValueError("Case directory must use letters, digits, '_' or '-': " + name)
        config = read_json(config_path)
        sizes = config.get("sizes")
        if (not isinstance(sizes, list) or not sizes
                or any(type(n) is not int or n < 1 for n in sizes)
                or sizes != sorted(set(sizes))):
            raise ValueError("%s: sizes must be increasing positive integers" % config_path)
        for key, default, minimum in (("repeat", 5, 1), ("warmup", 3, 0), ("seed", 42, 0)):
            value = config.setdefault(key, default)
            if type(value) is not int or value < minimum:
                raise ValueError("%s: invalid %s" % (config_path, key))
        for key, default, minimum in (("timeout", 120, 0.01), ("warmup_seconds", 0.25, 0), ("sample_seconds", 0.025, 0)):
            value = config.setdefault(key, default)
            if type(value) not in (int, float) or not minimum <= value < float("inf"):
                raise ValueError("%s: invalid %s" % (config_path, key))
        if not (config_path.parent / "workload.py").is_file():
            raise ValueError("Missing workload.py in " + name)
        adapters = [adapter_info(p) for p in sorted((config_path.parent / "implementations").glob("*.py")) if not p.name.startswith("_")]
        if not adapters:
            raise ValueError("No implementations found in " + name)
        cases[name] = {"name": name, "path": config_path.parent, "config": config, "adapters": adapters}
    return cases


def settings_for(case, quick=False):
    config = case["config"]
    settings = {k: config[k] for k in ("sizes", "seed", "repeat", "warmup", "timeout", "warmup_seconds", "sample_seconds")}
    settings["quick"] = bool(quick)
    if quick:
        settings.update(sizes=config["sizes"][:1], repeat=2, warmup=1, warmup_seconds=0, sample_seconds=0)
    return settings


def fingerprint(root, case, runtime, settings, sources):
    digest = hashlib.sha256()
    # Report appearance changes never invalidate measurements.
    shared = [root / "benchkit" / f for f in ("runner.py", "worker.py", "sources.py", "__init__.py")]
    shared += list((root / ".github" / "workflows").glob("*.yml"))
    files = shared + [p for p in case["path"].rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".pyo")]
    from .cffi_build import local_source_files
    for spec in sources.values():
        if spec.get("install") == "cffi":
            files.extend(local_source_files(root, spec))
            files.extend([root / "benchkit" / "cffi_build.py", root / "requirements-cffi.txt"])
        elif spec.get("install") == "hpy":
            from .hpy_build import local_source_files as hpy_source_files
            files.extend(hpy_source_files(root, spec))
            files.extend([root / "benchkit" / "hpy_build.py",
                          root / "benchkit" / "cffi_build.py", root / "requirements-hpy.txt"])
    for path in sorted(set(files)):
        if path.exists():
            digest.update(str(path.relative_to(root)).encode())
            digest.update(b"\0" + path.read_bytes() + b"\0")
    environment = {k: v for k, v in runtime.items() if k != "executable"}
    if runtime and any(spec.get("install") == "cffi" for spec in sources.values()):
        from .cffi_build import build_environment
        environment["cffi_build"] = build_environment()
    if runtime and any(spec.get("install") == "hpy" for spec in sources.values()):
        from .hpy_build import build_environment
        environment["hpy_build"] = build_environment()
    digest.update(json.dumps({"schema": SCHEMA_VERSION, "runtime": environment, "settings": settings, "sources": sources}, sort_keys=True).encode())
    return digest.hexdigest()


def reusable(path, expected_fingerprint, case, settings):
    try:
        previous = read_json(path)
        if previous["schema_version"] != SCHEMA_VERSION or previous["fingerprint"] != expected_fingerprint:
            return False
        if previous["case"] != case["name"]:
            return False
        if [s["id"] for s in previous["series"]] != [a["id"] for a in case["adapters"]]:
            return False
        for series in previous["series"]:
            if [p["size"] for p in series["points"]] != settings["sizes"]:
                return False
            for point in series["points"]:
                samples = point["samples"]
                if len(samples) != settings["repeat"] or not point["checksum"]:
                    return False
                if any(type(n) not in (float, int) or not math.isfinite(n) or n <= 0 for n in samples):
                    return False
                summaries = [point[name] for name in ("median", "min", "max")]
                if any(type(n) not in (float, int) or not math.isfinite(n) or n <= 0 for n in summaries):
                    return False
                if (point["median"] != statistics.median(samples)
                        or point["min"] != min(samples) or point["max"] != max(samples)):
                    return False
        return True
    except (OSError, ValueError, KeyError, TypeError, OverflowError):
        return False


def run_worker(case, adapter, size, settings, source_paths):
    request = {
        "case_path": str(case["path"].resolve()),
        "adapter_path": str(adapter["path"].resolve()),
        "source_path": str(source_paths[adapter["source"]]) if adapter["source"] else None,
        "size": size,
        "settings": settings,
    }
    environment = dict(os.environ, PYTHONHASHSEED="0")
    try:
        process = subprocess.run(
            [sys.executable, "-m", "benchkit.worker"], input=json.dumps(request), text=True,
            capture_output=True, timeout=settings["timeout"], cwd=str(ROOT), env=environment,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("%s/%s n=%s timed out after %ss" % (case["name"], adapter["id"], size, settings["timeout"])) from error
    if process.returncode:
        raise RuntimeError("%s/%s n=%s failed:\n%s" % (case["name"], adapter["id"], size, process.stderr[-12000:]))
    try:
        return json.loads(process.stdout)
    except ValueError as error:
        raise RuntimeError("Worker returned invalid JSON: " + process.stdout[-1000:]) from error


def run(results, selected=None, force=False, quick=False, root=ROOT):
    from .sources import prepare

    root = Path(root)
    results = Path(results)
    cases = discover(root)
    selected = set(selected or cases)
    unknown = selected - set(cases)
    if unknown:
        raise ValueError("Unknown cases: " + ", ".join(sorted(unknown)))
    if not cases:
        raise ValueError("No benchmarks/*/case.json found")
    runtime = runtime_info()
    lock = read_json(root / "sources.lock.json") if (root / "sources.lock.json").exists() else {}
    for path in results.glob("*/*.json"):
        if path.stem not in cases:
            path.unlink()
    pending = []
    for name in sorted(selected):
        case = cases[name]
        source_ids = {a["source"] for a in case["adapters"] if a["source"]}
        missing = source_ids - set(lock)
        if missing:
            raise ValueError("Unknown SOURCE in %s: %s" % (name, ", ".join(sorted(missing))))
        sources = {key: lock[key] for key in sorted(source_ids)}
        settings = settings_for(case, quick)
        key = fingerprint(root, case, runtime, settings, sources)
        destination = results / runtime["id"] / (name + ".json")
        if not force and reusable(destination, key, case, settings):
            print("SKIP %s/%s (unchanged)" % (runtime["id"], name), flush=True)
        else:
            pending.append((case, settings, sources, key, destination))
    source_ids = sorted({key for _, _, sources, _, _ in pending for key in sources})
    source_paths = prepare(root, source_ids) if source_ids else {}
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(root), capture_output=True, text=True)
    commit = revision.stdout.strip() if revision.returncode == 0 else "uncommitted"
    for case, settings, sources, key, destination in pending:
        series = []
        expected_checksums = {}
        for adapter in case["adapters"]:
            points = []
            for size in settings["sizes"]:
                print("RUN %s/%s/%s n=%s" % (runtime["id"], case["name"], adapter["id"], size), flush=True)
                point = run_worker(case, adapter, size, settings, source_paths)
                reference = expected_checksums.setdefault(size, point["checksum"])
                if point["checksum"] != reference:
                    raise RuntimeError("Result mismatch: %s/%s n=%s" % (case["name"], adapter["id"], size))
                points.append(point)
            series.append({"id": adapter["id"], "label": adapter["label"], "points": points})
        # Compare runtimes only when all workload, source and measurement settings
        # agree; an older result must not be mistaken for this version's oracle.
        workload_fingerprint = fingerprint(root, case, {}, settings, sources)
        for peer_path in results.glob("*/" + case["name"] + ".json"):
            if peer_path == destination:
                continue
            try:
                peer = read_json(peer_path)
                if not isinstance(peer, dict):
                    continue
                if peer.get("workload_fingerprint") != workload_fingerprint:
                    continue
                peer_checksums = {(s["id"], p["size"]): p["checksum"]
                                  for s in peer["series"] for p in s["points"]}
            except (OSError, ValueError, TypeError, KeyError):
                continue
            for item in series:
                for point in item["points"]:
                    peer_checksum = peer_checksums.get((item["id"], point["size"]))
                    if peer_checksum is not None and peer_checksum != point["checksum"]:
                        raise RuntimeError("Cross-runtime result mismatch: %s/%s n=%s" %
                                           (case["name"], item["id"], point["size"]))
        record_runtime = dict(runtime)
        if any(spec.get("install") == "cffi" for spec in sources.values()):
            from .cffi_build import build_environment
            record_runtime["cffi_build"] = build_environment()
        if any(spec.get("install") == "hpy" for spec in sources.values()):
            from .hpy_build import build_environment
            record_runtime["hpy_build"] = build_environment()
        write_json(destination, {
            "schema_version": SCHEMA_VERSION, "case": case["name"],
            "title": case["config"].get("title", case["name"]),
            "description": case["config"].get("description", ""),
            "runtime": record_runtime, "fingerprint": key, "workload_fingerprint": workload_fingerprint, "commit": commit,
            "measured_at": datetime.now(timezone.utc).isoformat(),
            "settings": settings, "sources": sources, "series": series,
        })
        print("SAVED " + str(destination), flush=True)
    return len(pending)
