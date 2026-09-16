"""Run the examples and ensure that the images are the same pixel by pixel.

This is the end-to-end check of PyPLUTO: every script in ``Examples/`` is run
in an isolated copy of that folder, and each image it writes is compared with
the reference in ``Tests/Ref_figs/``. Nothing is mocked and nothing is
inspected from the inside, so a change that quietly moves an axis, drops a
label or alters a colormap is caught here and almost nowhere else.

Why the leading underscore
--------------------------
pytest collects ``test_*.py``, so this module is deliberately *not* part of
the normal suite: the field-line examples make a full run take over a minute.
Until that cost comes down (the planned ``rastra`` package), it is run by
hand::

    pytest Tests/_test_examples.py

It should be run after every few files of work, and always before a release,
since it is the only test that looks at the figures a user actually gets.

Updating the reference figures
------------------------------
Matplotlib occasionally changes its layout arithmetic, and a new version can
shift an image by a single pixel with nothing wrong in PyPLUTO. When that
happens the references have to be regenerated::

    python Tests/_test_examples.py --check    # report what differs
    python Tests/_test_examples.py --update   # overwrite those references

Running the module with no arguments only warns: overwriting the references
is the one irreversible thing this file can do, so it never happens by
accident, and in particular not to somebody who typed ``python`` where they
meant ``pytest``.

Before regenerating, check that the difference really is a rendering change:
a size that is off by one pixel is layout rounding, while a changed region in
the middle of a frame is a genuine plotting change and must be understood
rather than blessed.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

import pytest
from PIL import Image, ImageChops, ImageSequence

ROOT_DIR = Path(__file__).parent.parent.resolve()
EXAMPLES_DIR = (ROOT_DIR / "Examples").resolve()
REFERENCE_DIR = (Path(__file__).parent / "Ref_figs").resolve()
OUTPUT_PATTERNS = ("*.png", "*.gif")


def find_example_scripts() -> list[Path]:
    """Return every example script, sorted by name.

    Kept apart from `list_example_scripts` so that the script mode below can
    enumerate the examples without depending on pytest.
    """
    return sorted(EXAMPLES_DIR.glob("*.py"))


def list_example_scripts() -> list[Path]:
    """Return a list of Python scripts in ../Examples.

    The same list as `find_example_scripts`, but skipping the whole test
    instead of running zero of them if the folder is missing, which is what
    happens when the suite runs from an installed package rather than a
    checkout.

    Returns
    -------
    - list[Path]
        The example scripts, sorted by name.

    Examples
    --------
    - Example #1: one test per example

        >>> @pytest.mark.parametrize("script", list_example_scripts())

    """
    scripts = find_example_scripts()
    if not scripts:
        pytest.skip("No example scripts found in ../Examples")
    return scripts


def run_example_in_sandbox(
    script: Path, tmp_path: Path, *, quiet: bool = False
) -> Path:
    """Copy Examples directory into a private sandbox and run the script there.

    The script remains unmodified and still writes inside an Examples directory.
    Pre-existing output files (PNGs, GIFs) are removed after the copy so that
    only images produced by this script's run are left to compare.

    The script runs in a separate interpreter rather than being imported, for
    two reasons: an example is written to be run, not imported, and a fresh
    process cannot inherit matplotlib state, a stale pyplot figure or an
    already-imported PyPLUTO from a previous example. `check=True` turns a
    failing example into an error here, so a broken script is reported as a
    failure rather than as a missing image.

    Parameters
    ----------
    - script (not optional): Path
        The example to run, named inside the real Examples folder.
    - tmp_path (not optional): Path
        A directory of its own for this run. Under pytest this is the fixture
        of the same name, which gives each test a fresh one.
    - quiet: bool, default False
        Discard the output of the example instead of letting it through.

    Returns
    -------
    - Path
        The sandboxed Examples folder, now holding the generated images.

    Examples
    --------
    - Example #1: run one example and collect what it drew

        >>> sandbox = run_example_in_sandbox(script, tmp_path)

    """
    # The copy keeps the "Examples" name, because the scripts write their
    # output relative to the folder they live in.
    sandbox_root = tmp_path / "project"
    sandbox_examples = sandbox_root / "Examples"

    shutil.copytree(EXAMPLES_DIR, sandbox_examples)

    # Delete the images that came with the copy, so whatever is found
    # afterwards was certainly drawn by this run.
    for pattern in OUTPUT_PATTERNS:
        for stale_file in sandbox_examples.glob(pattern):
            stale_file.unlink()

    sandbox_script = sandbox_examples / script.name

    # The output of the example is kept under pytest, where it lands in the
    # captured log of a failing test, and swallowed in script mode, where a
    # dozen examples would otherwise bury the summary.
    subprocess.run(
        [sys.executable, str(sandbox_script)],
        check=True,
        cwd=sandbox_examples,
        stdout=subprocess.DEVNULL if quiet else None,
        stderr=subprocess.DEVNULL if quiet else None,
    )

    return sandbox_examples


def compare_images(gen_path: Path, ref_path: Path) -> str | None:
    """Return None if two images are pixel-identical, else a diff description.

    Handles both static images and multi-frame ones (e.g. GIFs) by comparing
    frame by frame. Frames are compared as rendered RGBA pixels rather than
    raw encoding, since GIF palette layout can differ frame-to-frame despite
    the same visual content.

    The description says where the images part company, because that is what
    tells a rendering change from a real one: a size that differs by a pixel
    is matplotlib rounding a tight bounding box the other way, while a
    differing region reported in the middle of a frame is a genuine change in
    what was drawn.

    Parameters
    ----------
    - gen_path (not optional): Path
        The image the example just drew.
    - ref_path (not optional): Path
        The reference it is measured against.

    Returns
    -------
    - str | None
        None when the two are identical, otherwise a description of the first
        difference found.

    Examples
    --------
    - Example #1: compare one generated figure with its reference

        >>> compare_images(generated, reference)
        "frame 0 size differs (generated (2004, 1407) vs reference ...)"

    """
    with Image.open(gen_path) as gen_img, Image.open(ref_path) as ref_img:
        # A PNG yields one frame and a GIF several, so both are handled by
        # iterating in the same way.
        gen_frames = list(ImageSequence.Iterator(gen_img))
        ref_frames = list(ImageSequence.Iterator(ref_img))

        if len(gen_frames) != len(ref_frames):
            return (
                f"frame count differs (generated {len(gen_frames)} "
                f"vs reference {len(ref_frames)})"
            )

        for i, (gen_frame, ref_frame) in enumerate(
            zip(gen_frames, ref_frames, strict=True)
        ):
            # Compare what the frames look like, not how they are stored: a
            # GIF may reorder its palette between frames without any visible
            # change, and RGBA is the same picture either way.
            genframe = gen_frame.convert("RGBA")
            refframe = ref_frame.convert("RGBA")
            if genframe.size != refframe.size:
                return (
                    f"frame {i} size differs (generated {genframe.size} "
                    f"vs reference {refframe.size})"
                )
            # difference() gives a frame that is black wherever the two agree,
            # so getbbox() -- the box around everything non-black -- is None
            # for identical frames and otherwise says where they diverge.
            diff = ImageChops.difference(genframe, refframe)
            bbox = diff.getbbox()
            if bbox is not None:
                return f"frame {i} pixels differ within region {bbox}"

    return None


@pytest.mark.parametrize("script", list_example_scripts())
def test_example(script: Path, tmp_path: Path) -> None:
    """Run and compare the script-generated images.

    Run one example script in an isolated copy of Examples/ and compare its
    generated images with the reference ones, matched by filename.

    One test per example, through parametrize, so a failure names the script
    that broke instead of stopping at the first of fourteen. What it proves
    is the strongest thing in the suite: the figure a user gets from this
    release is the figure they got from the last one, pixel for pixel.

    A failure is therefore either a genuine change in what PyPLUTO draws, or
    a new matplotlib rounding its layout differently. The message says which:
    see the module docstring for how to tell them apart, and what to do about
    the second.
    """
    sandbox_examples = run_example_in_sandbox(script, tmp_path)

    # An example that drew nothing has failed even if it exited cleanly, so
    # this is checked before any comparison.
    gen_images = sorted(
        f for pattern in OUTPUT_PATTERNS for f in sandbox_examples.glob(pattern)
    )
    assert gen_images, f"No images generated by {script.name}"

    # Collected rather than asserted one by one, so a script that draws
    # several figures reports every bad one in a single failure.
    mismatches = []
    for gen_img in gen_images:
        ref_img = REFERENCE_DIR / gen_img.name
        if not ref_img.exists():
            mismatches.append(
                f"{gen_img.name}: no reference image in {REFERENCE_DIR}"
            )
            continue
        reason = compare_images(gen_img, ref_img)
        if reason is not None:
            mismatches.append(f"{gen_img.name}: {reason}")

    assert not mismatches, f"{script.name}: " + "; ".join(mismatches)


# ---------------------------------------------------------------------------
# Script mode: compare every example against its reference, and optionally
# overwrite the references that differ. Kept out of the pytest test above so
# that running the file can never be confused with running the suite.
# ---------------------------------------------------------------------------


def collect_differences(script: Path) -> list[tuple[Path, Path, str]]:
    """Run one example and return the images that do not match the reference.

    Each entry is the generated image, the reference it belongs to, and why
    they differ, so the caller can report it and, if asked, copy the first
    over the second. A reference that does not exist yet counts as a
    difference: a new example then simply gets its figures recorded.
    """
    differences: list[tuple[Path, Path, str]] = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        sandbox = run_example_in_sandbox(script, Path(tmp_dir), quiet=True)
        generated = sorted(
            image
            for pattern in OUTPUT_PATTERNS
            for image in sandbox.glob(pattern)
        )

        for image in generated:
            reference = REFERENCE_DIR / image.name
            if not reference.exists():
                differences.append((image, reference, "no reference yet"))
                continue
            reason = compare_images(image, reference)
            if reason is not None:
                differences.append((image, reference, reason))

        # The sandbox disappears with the temporary directory, so anything
        # that has to outlive this block is copied out before returning.
        if differences:
            kept = Path(tempfile.mkdtemp(prefix="pypluto_refs_"))
            differences = [
                (Path(shutil.copy2(image, kept / image.name)), ref, reason)
                for image, ref, reason in differences
            ]

    return differences


def report_and_update(*, update: bool) -> int:
    """Compare every example with its reference, and overwrite when asked.

    Parameters
    ----------
    - update (not optional): bool
        Overwrite the references that differ. With False nothing is written
        and the differences are only listed.

    Returns
    -------
    - int
        The process exit code: 0 when everything matches or every difference
        was written, 1 when differences were found and left alone.
    """
    # No examples at all is a broken checkout rather than a clean result, so
    # it exits non-zero instead of announcing that everything matches.
    scripts = find_example_scripts()
    if not scripts:
        print(f"No example scripts found in {EXAMPLES_DIR}")
        return 1

    total = 0
    for script in scripts:
        # Every example is run, including after a difference is found: the
        # point of --check is the full list, not the first problem.
        differences = collect_differences(script)
        if not differences:
            print(f"  ok        {script.name}")
            continue

        total += len(differences)
        for image, reference, reason in differences:
            # One line per differing image, always printed, so --update says
            # what it changed rather than doing it silently.
            action = "updated  " if update else "differs  "
            print(f"  {action} {script.name}: {reference.name}: {reason}")
            if update:
                # mkdir covers the first run of a fresh checkout, where the
                # reference folder does not exist yet. copy2 keeps the file
                # metadata, so only the pixels show up in the diff.
                REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
                shutil.copy2(image, reference)

    if total == 0:
        print("\nEvery example matches its reference figure.")
        return 0

    if update:
        # Writing the references was the job, so this is a success even
        # though images differed; the reminder is because the check that
        # matters now is a human reading the diff.
        print(f"\n{total} reference image(s) rewritten in {REFERENCE_DIR}.")
        print("Check the diff before committing: a one pixel size change is")
        print("layout rounding, anything else is a real plotting change.")
        return 0

    # --check found differences and wrote nothing: a non-zero exit so the
    # command can be used in a script or a git hook.
    print(f"\n{total} image(s) differ. Re-run with --update to accept them.")
    return 1


def main(argv: list[str] | None = None) -> int:
    """Run the comparison from the command line.

    With no argument nothing is compared and nothing is written: the module
    only warns and prints its usage, since somebody running it by hand is
    more likely to have meant pytest than to have meant overwriting every
    reference figure in the repository.

    Parameters
    ----------
    - argv: list[str] | None, default None
        The arguments to parse. None means read them from the command line,
        which is what happens when the module is run; a list is passed by a
        caller that wants to drive it directly.

    Returns
    -------
    - int
        The exit code: 0 on success, 1 when differences were left alone or
        when there was nothing to do.

    Examples
    --------
    - Example #1: list what differs, writing nothing

        >>> main(["--check"])

    """
    parser = argparse.ArgumentParser(
        prog="python Tests/_test_examples.py",
        description=(
            "Compare the figures produced by Examples/ with the references "
            "in Tests/Ref_figs/. To run this as a test instead, use "
            "'pytest Tests/_test_examples.py'."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report the images that differ, without writing anything",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="overwrite the reference images that differ",
    )
    args = parser.parse_args(argv)

    # Neither flag given: warn and stop. This is the safety catch, and the
    # reason both modes are flags rather than one being the default -- the
    # likeliest way to reach this file by hand is typing python where pytest
    # was meant, and that must not rewrite anything.
    if not (args.check or args.update):
        warnings.warn(
            "Nothing to do: this script does not run the test suite. Use "
            "'pytest Tests/_test_examples.py' to run the comparison as a "
            "test, '--check' to list the images that differ, or '--update' "
            "to overwrite the reference figures.",
            UserWarning,
            stacklevel=2,
        )
        parser.print_help()
        return 1

    # --check and --update differ only in whether anything is written, so one
    # function does both. Passing --update alone implies the comparison.
    return report_and_update(update=args.update)


if __name__ == "__main__":
    # Reached only when the file is run as a script; pytest imports it, which
    # sets __name__ to the module name and leaves this alone.
    sys.exit(main())
