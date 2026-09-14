"""Test of the examples_cli.py file."""

import pytest

from pyPLUTO.utils import examples_cli as cli


def _run(monkeypatch, argv):
    """Run the CLI with the given arguments and give back its exit code."""
    monkeypatch.setattr(cli.sys, "argv", ["pypluto-examples", *argv])
    return cli.main()


# The parser knows every subcommand the CLI offers
@pytest.mark.parametrize("command", ["path", "list", "copy", "run"])
def test_parser_knows_commands(command):
    parser = cli._build_parser()
    assert parser.parse_args([command, "x"] if command == "run" else [command])


# A subcommand is required
def test_parser_requires_a_command():
    with pytest.raises(SystemExit):
        cli._build_parser().parse_args([])


# The copy destination has a default value
def test_parser_copy_default():
    args = cli._build_parser().parse_args(["copy"])
    assert args.dst == "pypluto_examples"
    assert args.overwrite is False


# 'path' prints the examples directory
def test_path_command(monkeypatch, capsys):
    assert _run(monkeypatch, ["path"]) == 0
    assert capsys.readouterr().out.strip().endswith("Examples")


# 'list' prints one example script per line
def test_list_command(monkeypatch, capsys):
    assert _run(monkeypatch, ["list"]) == 0
    printed = capsys.readouterr().out.split()
    assert "test01_sod.py" in printed


# 'copy' copies the tree and prints where it went
def test_copy_command(monkeypatch, capsys, tmp_path):
    dest = tmp_path / "copied"
    assert _run(monkeypatch, ["copy", str(dest)]) == 0
    assert capsys.readouterr().out.strip() == str(dest)
    assert (dest / "test01_sod.py").exists()


# 'copy --overwrite' is accepted on an existing directory
def test_copy_overwrite(monkeypatch, tmp_path):
    dest = tmp_path / "copied"
    dest.mkdir()
    assert _run(monkeypatch, ["copy", str(dest), "--overwrite"]) == 0
    assert (dest / "test01_sod.py").exists()


# 'run' forwards the exit code of the example script
def test_run_command(monkeypatch):
    monkeypatch.setattr(cli, "run_example", lambda name, *args: 7)
    assert _run(monkeypatch, ["run", "test01_sod"]) == 7


# The arguments after the example name are forwarded to it
def test_run_command_forwards_arguments(monkeypatch):
    seen = {}

    def _fake(name, *args):
        seen["name"], seen["args"] = name, args
        return 0

    monkeypatch.setattr(cli, "run_example", _fake)
    _run(monkeypatch, ["run", "test01_sod", "--", "--flag"])
    assert seen["name"] == "test01_sod"
    assert seen["args"] == ("--flag",)
