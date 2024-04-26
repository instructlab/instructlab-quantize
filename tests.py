# SPDX-License-Identifier: Apache-2.0
# pylint: disable=redefined-outer-name
import os
import pathlib
import platform
import subprocess
import sys
from unittest import mock

import instructlab_quantize
import pytest

PKG_DIR = pathlib.Path(instructlab_quantize.__file__).absolute().parent


@pytest.fixture()
def m_check_output():
    with mock.patch("subprocess.check_output") as m_check_output:
        yield m_check_output


def test_mock_run_quantize(m_check_output: mock.Mock):
    quantize = os.fspath(PKG_DIR.joinpath("quantize"))
    instructlab_quantize.run_quantize("egg", "spam")
    m_check_output.assert_called_with([quantize, "egg", "spam"])
    m_check_output.reset_mock()

    instructlab_quantize.run_quantize("--help", stderr=subprocess.STDOUT)
    m_check_output.assert_called_with([quantize, "--help"], stderr=subprocess.STDOUT)


@pytest.mark.skipif(
    sys.platform != "darwin" and platform.machine() != "arm64",
    reason="binary is Apple M1-only",
)
def test_run_quantize(tmp_path: pathlib.Path):
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        instructlab_quantize.run_quantize("--help", stderr=subprocess.STDOUT, text=True)

    exc = exc_info.value
    assert exc.output.startswith("usage: ")
    # "quantize --help" exits with return code 1
    assert exc.returncode == 1

    quant_type = "Q4_K_M"
    outfile = tmp_path / "ggml-vocab-{quant_type}.gguf"
    instructlab_quantize.run_quantize(
        "llama.cpp/models/ggml-vocab-llama.gguf",
        os.fspath(outfile),
        quant_type,
    )
    assert outfile.is_file()
