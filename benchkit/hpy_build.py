"""Build the HPy Universal binding against the pinned ACL checkout."""
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from .cffi_build import local_source_files as _source_files, toolchain_environment


def local_source_files(root, spec):
    # The checked C++ kernel is compiled into the HPy module; CFFI itself is unused.
    return _source_files(root, spec) + [Path(root) / "acl_cffi" / name
                                      for name in ("native.cpp", "cdef.h")]


def build_environment():
    try:
        import hpy.devel
        import hpy.universal
        import setuptools
    except ImportError as error:
        raise RuntimeError("Install HPy dependencies: python -m pip install -r requirements-hpy.txt") from error
    if hasattr(sys, "pypy_version_info") and sys.pypy_version_info < (7, 3, 14):
        raise RuntimeError("HPy 0.9 requires PyPy >= 7.3.14; CI uses PyPy 7.3.20")
    return dict(toolchain_environment(), abi="universal",
                packages={"hpy": version("hpy"), "setuptools": setuptools.__version__},
                runtime=list(hpy.universal.get_version()),
                mode=os.environ.get("HPY", "universal"),
                log=os.environ.get("HPY_LOG", ""))


def build(root, checkout, spec, native_key):
    root, checkout = Path(root).resolve(), Path(checkout).resolve()
    info = {"native_key": native_key, "environment": build_environment()}
    digest = hashlib.sha256(json.dumps(info, sort_keys=True).encode())
    files = local_source_files(root, spec) + [Path(__file__),
        root / "benchkit" / "cffi_build.py", root / "requirements-hpy.txt"]
    for path in sorted(set(files)):
        digest.update(str(path.relative_to(root)).encode() + b"\0" + path.read_bytes() + b"\0")
    target = checkout.parent / (spec["rev"] + "-" + digest.hexdigest()[:20])
    marker = target / ".bench-install-ready"
    if marker.exists():
        return target
    with tempfile.TemporaryDirectory(prefix="hpy-build-", dir=checkout.parent) as directory:
        build_lib = Path(directory) / "module"
        # HPy's build command appends its ABI to build_lib and build_temp.
        staged = Path(str(build_lib) + "-hpy-universal")
        # Running setup in a child process keeps setuptools state and build output
        # out of the harness and --print-path stdout.
        subprocess.run([sys.executable, str(root / spec["path"] / "setup.py"),
                        "--hpy-abi=universal", "build", "--build-lib", str(build_lib),
                        "--build-temp", str(Path(directory) / "temp")],
                       cwd=directory, env=dict(os.environ, ACL_INCLUDE_DIR=str(checkout)),
                       stdout=sys.stderr, check=True)
        (staged / marker.name).write_text(json.dumps({"source": spec, "build": info}, sort_keys=True) + "\n")
        if target.exists():
            shutil.rmtree(target)
        staged.rename(target)
    return target
