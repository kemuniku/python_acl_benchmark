"""Build the local CFFI API binding against the pinned ACL checkout."""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import sysconfig
import tempfile


def local_source_files(root, spec):
    """Only source code participates in build/measurement invalidation."""
    if not spec.get("path"):
        return []
    root = Path(root).resolve()
    source = (root / spec["path"]).resolve()
    if not source.is_relative_to(root) or source == root or not source.is_dir():
        raise ValueError("Local source path must be a directory inside the repository")
    return sorted(path for path in source.rglob("*")
                  if path.is_file() and path.suffix in {".py", ".h", ".hpp", ".cpp"}
                  and "__pycache__" not in path.parts)


_BUILD_VARIABLES = (
    "CC", "CXX", "CPP", "CFLAGS", "CXXFLAGS", "CPPFLAGS", "LDFLAGS",
    "LDSHARED", "LDCXXSHARED", "AR", "ARFLAGS", "RANLIB", "CPATH",
    "C_INCLUDE_PATH", "CPLUS_INCLUDE_PATH", "LIBRARY_PATH", "LD_LIBRARY_PATH",
    "SDKROOT", "MACOSX_DEPLOYMENT_TARGET", "ARCHFLAGS",
)


def build_environment():
    """Describe the toolchain used by both build and measurement caches."""
    try:
        import cffi
        import setuptools
        import pycparser
    except ImportError as error:
        raise RuntimeError("Install CFFI build dependencies: python -m pip install -r requirements-cffi.txt") from error
    configured = {name: sysconfig.get_config_var(name) for name in _BUILD_VARIABLES}
    environment = {name: os.environ.get(name) for name in _BUILD_VARIABLES}
    compilers = {}
    for name, fallback in (("CC", "cc"), ("CXX", "c++")):
        command = shlex.split(environment[name] or configured[name] or fallback)
        if not command:
            raise ValueError("Empty compiler command: " + name)
        executable = shutil.which(command[0])
        if executable is None:
            raise RuntimeError("Compiler not found: " + command[0])
        version = subprocess.check_output(command + ["--version"], text=True, stderr=subprocess.STDOUT)
        compilers[name] = {"command": command, "executable": str(Path(executable).resolve()), "version": version}
    return {
        "packages": {"cffi": cffi.__version__, "setuptools": setuptools.__version__,
                     "pycparser": pycparser.__version__},
        "compilers": compilers, "environment": environment, "sysconfig": configured,
    }


@contextlib.contextmanager
def _build_output():
    """Keep Python and compiler subprocess output off --print-path stdout."""
    sys.stdout.flush()
    saved_stdout = os.dup(1)
    try:
        os.dup2(2, 1)
        with contextlib.redirect_stdout(sys.stderr):
            yield
    finally:
        try:
            sys.stderr.flush()
        finally:
            os.dup2(saved_stdout, 1)
            os.close(saved_stdout)


def build(root, checkout, spec, native_key):
    environment = build_environment()
    import cffi
    root, checkout = Path(root).resolve(), Path(checkout).resolve()
    source = root / spec["path"]
    digest = hashlib.sha256()
    info = {"native_key": native_key, "environment": environment}
    digest.update(json.dumps(info, sort_keys=True).encode())
    files = [(str(path.relative_to(root)), path) for path in local_source_files(root, spec)]
    files += [("benchkit/cffi_build.py", Path(__file__)),
              ("requirements-cffi.txt", root / "requirements-cffi.txt")]
    for name, path in files:
        digest.update(name.encode() + b"\0" + path.read_bytes() + b"\0")
    target = checkout.parent / (spec["rev"] + "-" + digest.hexdigest()[:20])
    marker = target / ".bench-install-ready"
    if marker.exists():
        return target
    with tempfile.TemporaryDirectory(prefix="cffi-build-", dir=checkout.parent) as directory:
        staged = Path(directory) / "module"
        staged.mkdir()
        builder = cffi.FFI()
        builder.cdef((source / "cdef.h").read_text())
        builder.set_source(
            "_acl_cffi_native", '#include "native.cpp"', source_extension=".cpp",
            include_dirs=[str(source), str(checkout)],
            extra_compile_args=["-std=c++17", "-O3", "-DNDEBUG", "-march=native"],
        )
        with _build_output():
            builder.compile(tmpdir=str(staged), verbose=False)
        (staged / marker.name).write_text(json.dumps({"source": spec, "build": info}, sort_keys=True) + "\n")
        if target.exists():
            shutil.rmtree(target)
        staged.rename(target)
    return target
