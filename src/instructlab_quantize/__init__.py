# SPDX-License-Identifier: Apache-2.0
"""Run quantize binary on macOS"""

import os
import platform
import subprocess
import sys
from importlib import resources

__all__ = ("run_quantize",)


def run_quantize(*quantizeargs, **kwargs):
    """Run quantize with subprocess.check_output

    stdout = quantize("extra", "arguments")
    """
    machine = platform.machine().lower()
    quantize_bin = f"quantize-{machine}-{sys.platform}"

    files = resources.files("instructlab_quantize")

    with resources.as_file(files.joinpath(quantize_bin)) as quantize:
        if not quantize.exists():
            raise FileNotFoundError(quantize)
        args = [os.fspath(quantize)]
        args.extend(quantizeargs)
        return subprocess.check_output(args, **kwargs)
