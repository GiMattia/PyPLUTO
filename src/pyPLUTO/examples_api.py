"""Helpers to access PyPLUTO examples without packaging them in src/."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

_REPO_OWNER = "GiMattia"
_REPO_NAME = "PyPLUTO"
_DEFAULT_BRANCH = "master"


def _repo_examples_path() -> Path | None:
    """Return repo-root Examples path when available (dev/editable installs)."""
    package_dir = Path(__file__).resolve().parent
    for parent in (package_dir, *package_dir.parents):
        examples = parent / "Examples"
        if examples.is_dir() and (parent / "pyproject.toml").exists():
            return examples
    return None


def _package_version() -> str:
    try:
        return version("py-pluto")
    except PackageNotFoundError:
        return "main"


def _cached_examples_dir() -> Path:
    ver = _package_version()
    safe_ver = ver.replace("/", "_")
    return Path.home() / ".cache" / "pypluto" / "examples" / safe_ver


def _download_examples() -> Path:
    """Download examples from GitHub archive and cache them locally."""
    cache_dir = _cached_examples_dir()
    examples_dir = cache_dir / "Examples"
    if examples_dir.is_dir():
        return examples_dir

    cache_dir.mkdir(parents=True, exist_ok=True)

    candidates = []
    if (ver := _package_version()) != "main":
        candidates.append(f"v{ver}")
        candidates.append(ver)
    candidates.append(_DEFAULT_BRANCH)

    last_error: Exception | None = None
    for ref in candidates:
        archive_url = f"https://github.com/{_REPO_OWNER}/{_REPO_NAME}/archive/refs/heads/{ref}.zip"
        if ref != _DEFAULT_BRANCH:
            archive_url = f"https://github.com/{_REPO_OWNER}/{_REPO_NAME}/archive/refs/tags/{ref}.zip"

        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / "pypluto_examples.zip"
            try:
                urllib.request.urlretrieve(archive_url, zip_path)
                with zipfile.ZipFile(zip_path) as zf:
                    top_dirs = {
                        name.split("/", 1)[0]
                        for name in zf.namelist()
                        if "/" in name
                    }
                    if not top_dirs:
                        raise FileNotFoundError(
                            "Invalid GitHub archive structure."
                        )
                    top_dir = sorted(top_dirs)[0]
                    prefix = f"{top_dir}/Examples/"
                    members = [m for m in zf.namelist() if m.startswith(prefix)]
                    if not members:
                        raise FileNotFoundError(
                            "Examples directory not found in archive."
                        )
                    zf.extractall(cache_dir)
                extracted = cache_dir / top_dir / "Examples"
                if examples_dir.exists():
                    shutil.rmtree(examples_dir)
                shutil.move(str(extracted), str(examples_dir))
                leftover = cache_dir / top_dir
                if leftover.exists():
                    shutil.rmtree(leftover)
                return examples_dir
            except Exception as exc:
                last_error = exc

    raise RuntimeError(
        "Unable to download examples from GitHub. "
        "Please check your internet connection and repository URLs."
    ) from last_error


def examples_path(download: bool = True) -> Path:
    """Return a local path to the full examples tree.

    The function prefers a local repository checkout and falls back to a
    cached GitHub download for installed wheels.
    """
    if (local := _repo_examples_path()) is not None:
        return local
    if not download:
        raise FileNotFoundError(
            "Examples not found locally and download=False."
        )
    return _download_examples()


def copy_examples(
    dst: str | Path = "pypluto_examples", overwrite: bool = False
) -> Path:
    """Copy the full examples tree to a writable destination."""
    destination = Path(dst).expanduser().resolve()
    src = examples_path(download=True)

    if destination.exists() and not overwrite:
        raise FileExistsError(
            f"Destination already exists: {destination}. "
            "Pass overwrite=True to merge content."
        )

    shutil.copytree(src, destination, dirs_exist_ok=overwrite)
    return destination


def list_examples() -> list[Path]:
    """List top-level runnable Python example scripts."""
    src = examples_path(download=True)
    return sorted(src.glob("test*.py"))


def run_example(example: str, *args: str) -> int:
    """Run an example script by name."""
    script = example if example.endswith(".py") else f"{example}.py"
    src = examples_path(download=True)
    script_path = src / script

    if not script_path.exists():
        available = ", ".join(p.name for p in list_examples())
        raise FileNotFoundError(
            f"Example '{script}' not found in {src}. Available scripts: {available}"
        )

    cmd = [sys.executable, str(script_path), *args]
    completed = subprocess.run(cmd, check=False)
    return completed.returncode
