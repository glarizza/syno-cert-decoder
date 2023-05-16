#!/usr/bin/env python
"""Tests for `syno_cert_decoder` package."""
from typer.testing import CliRunner
from syno_cert_decoder.cli import app
import syno_cert_decoder


runner = CliRunner()


def test_app():
    """Test the version subcommand"""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert syno_cert_decoder.__version__ in result.stdout


def test_version():
    """Test there is a version string"""
    assert syno_cert_decoder.__version__ == "1.0.0"
