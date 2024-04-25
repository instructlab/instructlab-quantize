# SPDX-License-Identifier: Apache-2.0
"""Run quantize binary on macOS"""

import os
import subprocess
from importlib import resources

__all__ = (
    "QUANTIZE",
    "run_quantize",
)

QUANTIZE = resources.files("instructlab_quantize").joinpath("quantize")


def run_quantize(*quantizeargs, **kwargs):
    """Run quantize with subprocess.check_output

    stdout = quantize("extra", "arguments")
    """
    with resources.as_file(QUANTIZE) as quantize:
        args = [os.fspath(quantize)]
        args.extend(quantizeargs)
        return subprocess.check_output(args, **kwargs)
