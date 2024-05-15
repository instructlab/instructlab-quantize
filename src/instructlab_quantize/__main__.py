# SPDX-License-Identifier: Apache-2.0
import sys

from . import run_quantize

print(run_quantize(*sys.argv[1:]))
