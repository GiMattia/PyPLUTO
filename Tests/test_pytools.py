import os
import sys
import types
import warnings

import pytest

import pyPLUTO.pytools as pt

# ---- find_example -----------------------------------------------------------


def test_find_example_local_exists(tmp_path, monkeypatch):
    """Covers local path resolution success."""
    test_dir = tmp_path / "Test_Problems" / "prob"
    test_dir.mkdir(parents=True)
    fake_file = tmp_path / "caller.py"
    fake_file.write_text("pass")

    # Return two frames so [1] works
    monkeypatch.setattr(
        pt.inspect,
        "stack",
        lambda: [object(), types.SimpleNamespace(filename=fake_file)],
    )
    result = pt.find_example("prob")
    assert result == test_dir


def test_find_example_env_exists(tmp_path, monkeypatch):
    """Covers the fallback.exists() -> return fallback branch."""
    fake_file = tmp_path / "caller.py"
    fake_file.write_text("pass")

    # Make PLUTO_DIR/Test_Problems/prob exist
    pluto_dir = tmp_path / "pluto"
    fallback = pluto_dir / "Test_Problems" / "prob"
    fallback.mkdir(parents=True)

    # Mock stack to have two frames
    monkeypatch.setattr(
        pt.inspect,
        "stack",
        lambda: [object(), types.SimpleNamespace(filename=fake_file)],
    )
    # Set the env var so fallback path can be resolved
    monkeypatch.setenv("PLUTO_DIR", str(pluto_dir))

    result = pt.find_example("prob")
    # ✅ verifies that fallback.exists() was True and returned
    assert result == fallback


def test_find_example_env_set_but_missing(tmp_path, monkeypatch):
    """Covers branch where $PLUTO_DIR is set but fallback path doesn't exist (33→37)."""
    # Fake caller file (so base_dir = tmp_path)
    fake_file = tmp_path / "caller.py"
    fake_file.write_text("pass")

    # Make sure the local path does NOT exist (we don't create Test_Problems/prob)

    # Set PLUTO_DIR to a dir that DOESN'T contain Test_Problems/prob
    pluto_dir = tmp_path / "pluto"
    pluto_dir.mkdir()

    # Provide a 2-frame stack so stack()[1].filename works
    monkeypatch.setattr(
        pt.inspect,
        "stack",
        lambda: [object(), types.SimpleNamespace(filename=fake_file)],
    )
    monkeypatch.setenv("PLUTO_DIR", str(pluto_dir))

    # With env set but no fallback dir, we must hit the raise after the env block
    with pytest.raises(FileNotFoundError):
        pt.find_example("prob")


def test_find_example_not_found(tmp_path, monkeypatch):
    """Covers FileNotFoundError branch."""
    fake_file = tmp_path / "caller.py"
    fake_file.write_text("pass")

    monkeypatch.setattr(
        pt.inspect,
        "stack",
        lambda: [object(), types.SimpleNamespace(filename=fake_file)],
    )
    monkeypatch.delenv("PLUTO_DIR", raising=False)

    with pytest.raises(FileNotFoundError):
        pt.find_example("no_prob")


# ---- savefig ---------------------------------------------------------------


def test_savefig_raises():
    """Covers NotImplementedError."""
    with pytest.raises(NotImplementedError):
        pt.savefig()


# ---- show ------------------------------------------------------------------


def test_show(monkeypatch):
    """Covers plt.show() call."""
    called = {}
    monkeypatch.setattr(
        pt.plt, "show", lambda block=True: called.setdefault("b", block)
    )
    pt.show(block=False)
    assert called["b"] is False


# ---- ring ------------------------------------------------------------------


def test_ring_windows(monkeypatch):
    """Covers Windows branch (winsound present)."""
    called = {}
    fake_beep = lambda freq, dur: called.setdefault("ok", (freq, dur))
    fake_mod = types.SimpleNamespace(Beep=fake_beep)
    monkeypatch.setitem(sys.modules, "winsound", fake_mod)
    monkeypatch.setattr(pt, "windows", True)
    pt.ring(length=0.1, freq=1000)
    assert "ok" in called


def test_ring_windows_warn(monkeypatch):
    """Covers missing winsound warning branch."""
    monkeypatch.setitem(sys.modules, "winsound", None)
    monkeypatch.setattr(pt, "windows", True)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Simulate warning from winsound import
        def bad_import(name):
            raise UserWarning

        monkeypatch.setitem(
            sys.modules,
            "winsound",
            types.SimpleNamespace(
                Beep=lambda *a, **k: (_ for _ in ()).throw(UserWarning())
            ),
        )
        # Should fall into warning path
        pt.ring()
        assert any("winsound" in str(wi.message) for wi in w)


def test_ring_posix(monkeypatch):
    """Covers os.name == 'posix' branch."""
    monkeypatch.setattr(os, "name", "posix")
    monkeypatch.setattr(pt, "windows", None)
    monkeypatch.setattr(os, "system", lambda cmd: 0)
    pt.ring(length=0.1, freq=220)


def test_ring_posix_warn(monkeypatch):
    """Covers posix UserWarning inside try/except."""
    monkeypatch.setattr(os, "name", "posix")
    monkeypatch.setattr(pt, "windows", None)

    def bad_system(cmd):
        raise UserWarning

    monkeypatch.setattr(os, "system", bad_system)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        pt.ring()
        assert any("sox" in str(wi.message) for wi in w)


def test_ring_other_os(monkeypatch):
    """Covers fallback else branch for unsupported OS."""
    monkeypatch.setattr(os, "name", "weirdOS")
    monkeypatch.setattr(pt, "windows", None)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        pt.ring()
        assert any("not implemented" in str(wi.message) for wi in w)
