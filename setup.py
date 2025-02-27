import os
import platform
import subprocess
import sys

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.dist import Distribution
from wheel.bdist_wheel import bdist_wheel as bdist_wheel

CMAKE_ARGS = [
    "-DCMAKE_BUILD_TYPE=Release",
    "-DBUILD_SHARED_LIBS=OFF",
    # build with base ISA
    "-DGGML_NATIVE=OFF",
    "-DLLAMA_NATIVE=OFF",
    "-DLLAMA_BUILD_TESTS=OFF",
    "-DLLAMA_BUILD_SERVER=OFF",
]
CMAKE_ARGS_X86_64 = [
    # force x86_64-v2 ISA
    "-DGGML_AVX=OFF",
    "-DGGML_AVX2=OFF",
    "-DGGML_FMA=OFF",
    "-DGGML_F16C=OFF",
    "-DLLAMA_AVX=OFF",
    "-DLLAMA_AVX2=OFF",
    "-DLLAMA_FMA=OFF",
    "-DLLAMA_F16C=OFF",
]
CMAKE_ARGS_DARWIN_AARCH64 = [
    # build and embed METAL on Apple M
    "-DGGML_METAL=ON",
    "-DGGML_METAL_EMBED_LIBRARY=ON",
    "-DLLAMA_METAL=ON",
    "-DLLAMA_METAL_EMBED_LIBRARY=ON",
]
QUANTIZE_BINARY = "llama-quantize"


class Py3NoneBdistWheel(bdist_wheel):
    """Tag wheel as py3-none-{tag}"""

    def finalize_options(self) -> None:
        super().finalize_options()
        self.root_is_pure = False

    def get_tag(self) -> tuple[str, str, str]:
        _py, _abi, plat_name = super().get_tag()
        return "py3", "none", plat_name


class QuantizeBuildPy(build_py):
    """Hack to build and copy quantize binary with Python files"""

    def build_quantize(self) -> None:
        # Switch to scikit-build-core? I have not found an example how to
        # ship a program with scikit-build-core.
        arch = platform.uname().machine
        build_cmd = self.get_finalized_command("build")
        package_name = self.distribution.packages[0]
        build_temp = build_cmd.build_temp
        cmake_args = [
            "cmake",
            "-S",
            "llama.cpp",
            "-B",
            build_temp,
        ]
        cmake_args.extend(CMAKE_ARGS)
        if sys.platform == "darwin" and arch == "aarch64":
            cmake_args.extend(CMAKE_ARGS_DARWIN_AARCH64)
        elif arch == "x86_64":
            cmake_args.extend(CMAKE_ARGS_X86_64)
        print(f"Run {' '.join(cmake_args)}")
        subprocess.check_call(cmake_args)

        build_args = [
            "cmake",
            "--build",
            build_temp,
            "--config",
            "Release",
            "--target",
            QUANTIZE_BINARY,
        ]
        print(f"Run {' '.join(build_args)}")
        subprocess.check_call(build_args)

        infile = os.path.join(build_temp, "bin", QUANTIZE_BINARY)
        outname = f"quantize-{arch}-{sys.platform}"
        outfile = os.path.join(self.build_lib, package_name, outname)
        directory = os.path.dirname(outfile)
        os.makedirs(directory, exist_ok=True)
        self.copy_file(infile, outfile, preserve_mode=True)
        self.package_data[package_name] = [outname]

    def run(self) -> None:
        self.build_quantize()
        return super().run()


class BinaryDistribution(Distribution):
    """Mark package has platlib package"""

    def has_ext_modules(foo) -> bool:
        return True


setup(
    distclass=BinaryDistribution,
    cmdclass={
        "bdist_wheel": Py3NoneBdistWheel,
        "build_py": QuantizeBuildPy,
    },
)
