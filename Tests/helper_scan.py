"""The sources scanned for generic errors and warnings.

test_pperrors.py and test_ppwarnings.py read every source file of pyPLUTO and
report each raise and warning that does not use a category of its own. The
files below are left out: they are parked, or are to be rewritten, and each
comes back into the scan when that happens.
"""

import ast
from collections.abc import Iterator
from pathlib import Path

import pyPLUTO

# The folder of the package
PACKAGE = Path(pyPLUTO.__file__).parent

# Parked (interactive, volume, gridplot) or to be rewritten
EXCLUDED = {
    "amr.py",
    "findlines.py",
    "gridplot.py",
    "interactive.py",
    "nabla.py",
    "transform.py",
    "volengine.py",
    "volume.py",
}


def scanned_sources() -> Iterator[tuple[str, ast.Module]]:
    """Give each scanned file, by its path inside the package, parsed."""
    for path in sorted(PACKAGE.rglob("*.py")):
        if path.name not in EXCLUDED:
            source = path.read_text(encoding="utf-8")
            yield path.relative_to(PACKAGE).as_posix(), ast.parse(source)
