"""Run the gallery scripts and compare their figures pixel by pixel.

The gallery in ``Gallery/`` is the visual user guide: one short script per
case, grouped by topic, each drawing on synthetic data. sphinx-gallery runs
them to build the gallery pages of the documentation, collecting every figure
left open, and this module does the same and compares each figure with its
reference in ``Tests/Ref_figs/gallery/<topic>/``.

Unlike ``_test_examples.py`` these scripts are quick, so this module is part
of the normal suite: a change that moves a colorbar, drops a label or alters
a colormap shows up in every run.

The scripts save nothing themselves, as in matplotlib's gallery, so that
they read as plain user code; each runs in a fresh interpreter, which saves
the figures afterwards as ``<script>.png`` (``<script>_<n>.png`` for a second
figure and the next ones).

Updating the references
-----------------------
A deliberate change in what a script draws, or a new script, needs new
references::

    python Tests/test_gallery.py --check    # report what differs
    python Tests/test_gallery.py --update   # overwrite those references

As for the examples, check the difference before accepting it: a size off by
one pixel is layout rounding, a changed region is a real plotting change.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from _test_examples import compare_images

ROOT_DIR = Path(__file__).parent.parent.resolve()
GALLERY_DIR = (ROOT_DIR / "Gallery").resolve()
REFERENCE_DIR = (Path(__file__).parent / "Ref_figs" / "gallery").resolve()

# Run one script as __main__, then save every figure it left open, as
# sphinx-gallery collects them
RUNNER = """
import runpy, sys
import matplotlib.pyplot as plt
script, out, stem = sys.argv[1], sys.argv[2], sys.argv[3]
runpy.run_path(script, run_name="__main__")
for i, num in enumerate(plt.get_fignums()):
    name = stem if i == 0 else f"{stem}_{i}"
    plt.figure(num).savefig(f"{out}/{name}.png", dpi=80)
"""


def find_gallery_scripts() -> list[Path]:
    """Return every gallery script, sorted by topic and name.

    Returns
    -------
    - list[Path]
        The scripts in the topic folders of ``Gallery/``.

    Examples
    --------
    - Example #1: the colorbar scripts come first

        >>> find_gallery_scripts()[0].parent.name
        'colorbar'

    """
    return sorted(GALLERY_DIR.glob("*/*.py"))


def draw_script(script: Path, out: Path) -> list[Path]:
    """Run one gallery script in a fresh interpreter and save its figures.

    A fresh process keeps one script from inheriting the figures, the
    settings or the pyPLUTO state of another, as each will in the
    documentation build. ``check=True`` turns a failing script into an
    error, rather than into a missing figure.

    Parameters
    ----------
    - script (not optional): Path
        The gallery script to run.
    - out (not optional): Path
        The folder where its figures are saved.

    Returns
    -------
    - list[Path]
        The figures saved, sorted by name.

    Examples
    --------
    - Example #1: the figure of one script

        >>> draw_script(GALLERY_DIR / "colorbar" / "zoom.py", tmp_path)
        [PosixPath('.../zoom.png')]

    """
    environment = {**os.environ, "MPLBACKEND": "Agg"}
    subprocess.run(
        [sys.executable, "-c", RUNNER, str(script), str(out), script.stem],
        check=True,
        cwd=script.parent,
        env=environment,
        stdout=subprocess.DEVNULL,
    )
    return sorted(out.glob(f"{script.stem}*.png"))


def reference_of(script: Path, figure: Path) -> Path:
    """Return where the reference of a figure of a script is kept.

    Parameters
    ----------
    - script (not optional): Path
        The gallery script that drew the figure.
    - figure (not optional): Path
        The figure it drew.

    Returns
    -------
    - Path
        The reference, in the folder of the script's topic.

    Examples
    --------
    - Example #1: the reference of the zoom figure

        >>> reference_of(script, figure).relative_to(REFERENCE_DIR)
        PosixPath('colorbar/zoom.png')

    """
    return REFERENCE_DIR / script.parent.name / figure.name


SCRIPTS = [
    pytest.param(s, id=f"{s.parent.name}/{s.stem}")
    for s in find_gallery_scripts()
]


def test_the_gallery_is_not_empty() -> None:
    """Find the gallery scripts at all.

    An empty gallery, from a wrong path or a checkout without it, would turn
    the comparison below into zero tests that all pass.
    """
    assert SCRIPTS


@pytest.mark.parametrize("script", SCRIPTS)
def test_gallery_script(script: Path, tmp_path: Path) -> None:
    """Run one gallery script and compare its figures with the references.

    One test per script, so a failure names the case that changed. A
    failure is either a real change in what pyPLUTO draws, to be understood
    before the references are updated, or a new matplotlib rounding its
    layout differently.
    """
    figures = draw_script(script, tmp_path)
    assert figures, f"{script.name} drew no figure"

    mismatches = []
    for figure in figures:
        reference = reference_of(script, figure)
        if not reference.exists():
            mismatches.append(
                f"{figure.name}: no reference in {reference.parent}"
            )
            continue
        if (reason := compare_images(figure, reference)) is not None:
            mismatches.append(f"{figure.name}: {reason}")

    assert not mismatches, f"{script.name}: " + "; ".join(mismatches)


def report_and_update(*, update: bool) -> int:
    """Compare every gallery figure with its reference, and overwrite if asked.

    Parameters
    ----------
    - update (not optional): bool
        Overwrite the references that differ, or are missing. With False
        nothing is written and the differences are only listed.

    Returns
    -------
    - int
        The exit code: 0 when everything matches or every difference was
        written, 1 when differences were found and left alone.

    Examples
    --------
    - Example #1: list what differs, writing nothing

        >>> report_and_update(update=False)
        0

    """
    total = 0
    for script in find_gallery_scripts():
        with tempfile.TemporaryDirectory() as tmp_dir:
            for figure in draw_script(script, Path(tmp_dir)):
                reference = reference_of(script, figure)
                reason = (
                    compare_images(figure, reference)
                    if reference.exists()
                    else "no reference yet"
                )
                if reason is None:
                    print(f"  ok        {script.parent.name}/{figure.name}")
                    continue
                total += 1
                action = "updated  " if update else "differs  "
                print(
                    f"  {action} {script.parent.name}/{figure.name}: {reason}"
                )
                if update:
                    reference.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(figure, reference)

    if total and not update:
        print(
            f"\n{total} figure(s) differ. Re-run with --update to accept them."
        )
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    """Compare or update the gallery references from the command line.

    One of the two flags is required, so that running the file by hand never
    overwrites a reference by accident.

    Parameters
    ----------
    - argv: list[str] | None, default None
        The arguments; None reads them from the command line.

    Returns
    -------
    - int
        The exit code of `report_and_update`, or 1 without a flag.

    Examples
    --------
    - Example #1: write the references of a new script

        >>> main(["--update"])
        0

    """
    parser = argparse.ArgumentParser(
        prog="python Tests/test_gallery.py",
        description="Compare the gallery figures with Tests/Ref_figs/gallery/.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="list what differs")
    mode.add_argument(
        "--update", action="store_true", help="overwrite what differs"
    )
    args = parser.parse_args(argv)
    return report_and_update(update=args.update)


if __name__ == "__main__":
    sys.exit(main())
