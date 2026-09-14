"""Test of the examples_api.py file."""

import pytest

from pyPLUTO.utils import examples_api as api


# In a repository checkout the examples are found next to the sources
def test_repo_examples_path():
    found = api._repo_examples_path()
    assert found is not None
    assert found.name == "Examples"
    assert (found.parent / "pyproject.toml").exists()


# The version string is used to keep one cache per release
def test_package_version_is_a_string():
    assert isinstance(api._package_version(), str)
    assert api._package_version() != ""


# The cache directory is named after the version
def test_cached_examples_dir():
    cache = api._cached_examples_dir()
    assert api._package_version().replace("/", "_") == cache.name
    assert "pypluto" in str(cache)


# A missing package version falls back to the main branch
def test_package_version_fallback(monkeypatch):
    def _raise(_name):
        raise api.PackageNotFoundError

    monkeypatch.setattr(api, "version", _raise)
    assert api._package_version() == "main"


# The local checkout is preferred over any download
def test_examples_path_prefers_local():
    assert api.examples_path() == api._repo_examples_path()


# Without a local checkout and without downloading there is nothing to return
def test_examples_path_no_local_no_download(monkeypatch):
    monkeypatch.setattr(api, "_repo_examples_path", lambda: None)
    with pytest.raises(FileNotFoundError, match="download=False"):
        api.examples_path(download=False)


# The runnable examples are the test scripts of the examples tree
def test_list_examples():
    scripts = api.list_examples()
    assert scripts
    assert all(p.suffix == ".py" for p in scripts)
    assert all(p.name.startswith("test") for p in scripts)


# The list is sorted, so the CLI output is stable
def test_list_examples_is_sorted():
    scripts = api.list_examples()
    assert scripts == sorted(scripts)


# The examples tree can be copied somewhere writable
def test_copy_examples(tmp_path):
    dest = api.copy_examples(tmp_path / "copied")
    assert dest.exists()
    assert (dest / "test01_sod.py").exists()


# Copying onto an existing directory is refused unless asked for
def test_copy_examples_existing(tmp_path):
    dest = tmp_path / "copied"
    dest.mkdir()
    with pytest.raises(FileExistsError, match="already exists"):
        api.copy_examples(dest)


# With overwrite the copy is merged into the existing directory
def test_copy_examples_overwrite(tmp_path):
    dest = tmp_path / "copied"
    dest.mkdir()
    api.copy_examples(dest, overwrite=True)
    assert (dest / "test01_sod.py").exists()


# An unknown example name is reported together with the available ones
def test_run_example_unknown():
    with pytest.raises(FileNotFoundError, match="not found"):
        api.run_example("nosuchexample")


# The script is run in a subprocess, and its exit code is passed back
def test_run_example_returns_exit_code(monkeypatch):
    """LONG TEST: CHECK"""
    seen = {}

    class _Completed:
        returncode = 3

    def _fake_run(cmd, check):
        seen["cmd"] = cmd
        return _Completed()

    monkeypatch.setattr(api.subprocess, "run", _fake_run)

    assert api.run_example("test01_sod", "--flag") == 3
    assert seen["cmd"][1].endswith("test01_sod.py")
    assert seen["cmd"][-1] == "--flag"


# The .py suffix is optional in the example name
def test_run_example_accepts_suffix(monkeypatch):
    class _Completed:
        returncode = 0

    monkeypatch.setattr(api.subprocess, "run", lambda cmd, check: _Completed())
    assert api.run_example("test01_sod.py") == 0
