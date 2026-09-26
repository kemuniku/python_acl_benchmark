"""Invoked by benchkit.hpy_build in an isolated temporary build directory."""
import os
from pathlib import Path

from setuptools import Extension, setup

source = Path(__file__).resolve().parent
setup(
    name="acl-hpy-native",
    version="0.1.0",
    hpy_ext_modules=[Extension(
        "_acl_hpy_native", [str(source / "native.cpp")],
        include_dirs=[os.environ["ACL_INCLUDE_DIR"]],
        language="c++",
        extra_compile_args=["-std=c++17", "-O3", "-DNDEBUG", "-march=native"],
    )],
)
