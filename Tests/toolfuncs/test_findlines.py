"""Test of the findlines.py file.

The file is not reviewed yet: this is the one behaviour that has been fixed
and must stay fixed, so that the rest can be written around it later.

A field line is integrated until it leaves the domain, and where it stops is
what the figure shows. The domain ends at the edge of the outermost cells,
half a cell beyond their centers, which is also where a map of it is drawn
to, so a line that stops short leaves a gap at the wall and one that runs
past it pushes the frame of that map open.
"""

import numpy as np
import pytest

from pyPLUTO.loadstate import LoadState
from pyPLUTO.toolfuncs.findlines import FindLinesManager

# Ten cells a tenth of a unit wide, centered on 0.05 to 0.95: the domain is
# then exactly 0 to 1 in both directions.
centers = np.linspace(0.05, 0.95, 10)


def _manager() -> FindLinesManager:
    """Build a manager on a square grid of ten cells a side."""
    state = LoadState()
    state.x1 = centers
    state.x2 = centers
    state.nx1 = centers.size
    state.nx2 = centers.size
    return FindLinesManager(state)


def test_a_field_line_ends_on_the_border() -> None:
    """Follow a uniform horizontal field from the middle of the domain.

    The line has nowhere to go but across, so it must start at one wall and
    end at the other, exactly: the borders are 0 and 1, half a cell beyond
    the first and the last center.

    The integrator finds the border by looking for a zero of the event
    function, so that function has to measure the distance to it. Given a
    flag instead -- inside or outside -- the crossing is only noticed once a
    step has landed beyond the wall, and the line is drawn to wherever that
    step happened to end, up to a whole step outside the domain.
    """
    manager = _manager()
    bx1 = np.ones((10, 10))
    bx2 = np.zeros((10, 10))

    lines = manager.find_fieldlines(
        bx1, bx2, x1=centers, x2=centers, x0=[0.5], y0=[0.5], closed=False
    )

    xline, yline = lines[0]
    assert float(np.min(xline)) == pytest.approx(0.0, abs=1e-9)
    assert float(np.max(xline)) == pytest.approx(1.0, abs=1e-9)
    assert np.allclose(yline, 0.5)
