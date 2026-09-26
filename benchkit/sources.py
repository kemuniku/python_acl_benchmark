"""Fetch pinned libraries and install native modules into interpreter-local caches."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import sysconfig
import tempfile


def source_specs(root):
    with (Path(root) / "sources.lock.json").open(encoding="utf-8") as stream:
        specs = json.load(stream)
    for name, spec in specs.items():
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", name):
            raise ValueError("Invalid source name: " + name)
        if not re.fullmatch(r"[0-9a-f]{40}", spec.get("rev", "")):
            raise ValueError("Source revisions must be full commit SHAs: " + name)
        if spec.get("install") not in (None, "pip", "cffi"):
            raise ValueError("Unknown source install mode: " + name)
        if spec.get("install") == "cffi":
            from .cffi_build import local_source_files
            if not spec.get("path"):
                raise ValueError("CFFI sources require a local path: " + name)
            local_source_files(root, spec)
    return specs


def _run(args, **kwargs):
    subprocess.run(args, check=True, stdout=sys.stderr, **kwargs)


def _native_key(spec):
    # Upstream uses -march=native: do not reuse native binaries across CPU types.
    cpu = ""
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        cpu = "\n".join(sorted(set(
            line for line in cpuinfo.read_text().splitlines()
            if line.startswith(("model name", "flags", "Features"))
        )))
    info = [sys.version, sys.executable, sysconfig.get_config_var("SOABI"),
            platform.platform(), platform.machine(), cpu, spec]
    return hashlib.sha256(json.dumps(info, sort_keys=True).encode()).hexdigest()[:20]


def prepare(root, source_ids):
    """Return source_id -> PYTHONPATH directory for the running interpreter.

    No global packages are installed. Failed fetches/builds never create the
    completion marker, so rerunning retries them instead of using partial data.
    """
    root = Path(root).resolve()
    source_ids = sorted(set(source_ids))
    if not source_ids:
        return {}
    specs = source_specs(root)
    paths = {}
    for source_id in source_ids:
        if source_id not in specs:
            raise ValueError("Unknown source in sources.lock.json: " + source_id)
        spec = specs[source_id]
        base = root / ".cache" / "sources" / source_id
        checkout = base / spec["rev"]
        marker = checkout / ".bench-source-ready"
        if not marker.exists():
            base.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="fetch-", dir=base) as directory:
                staged = Path(directory) / "checkout"
                _run(["git", "init", "--quiet", str(staged)])
                _run(["git", "-C", str(staged), "fetch", "--quiet", "--depth=1", spec["url"], spec["rev"]])
                _run(["git", "-C", str(staged), "checkout", "--quiet", "--detach", "FETCH_HEAD"])
                actual = subprocess.check_output(
                    ["git", "-C", str(staged), "rev-parse", "HEAD"], text=True
                ).strip()
                if actual != spec["rev"]:
                    raise RuntimeError("Fetched revision does not match source lock")
                (staged / marker.name).write_text(actual + "\n")
                if checkout.exists():
                    shutil.rmtree(checkout)
                staged.rename(checkout)
        if spec.get("install") == "cffi":
            from .cffi_build import build
            paths[source_id] = build(root, checkout, spec, _native_key(spec))
            continue
        if spec.get("install") != "pip":
            paths[source_id] = checkout
            continue
        target = base / (spec["rev"] + "-" + _native_key(spec))
        installed = target / ".bench-install-ready"
        if not installed.exists():
            with tempfile.TemporaryDirectory(prefix="build-", dir=base) as directory:
                directory = Path(directory)
                staged = directory / "site-packages"
                build_source = directory / "checkout"
                shutil.copytree(checkout, build_source, ignore=shutil.ignore_patterns(".git"))
                env = dict(os.environ)
                env.setdefault("CMAKE_BUILD_PARALLEL_LEVEL", "2")
                dependencies = spec.get("build_dependencies", [])
                if dependencies:
                    constraints = directory / "constraints.txt"
                    constraints.write_text("\n".join(dependencies) + "\n")
                    # Inherited by pip's isolated build environment as well.
                    env["PIP_CONSTRAINT"] = str(constraints)
                    env["PIP_BUILD_CONSTRAINT"] = str(constraints)
                _run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
                      "--no-deps", "--no-cache-dir", "--target", str(staged), str(build_source)], env=env)
                (staged / installed.name).write_text(json.dumps(spec, sort_keys=True) + "\n")
                if target.exists():
                    shutil.rmtree(target)
                staged.rename(target)
        paths[source_id] = target
    return paths
