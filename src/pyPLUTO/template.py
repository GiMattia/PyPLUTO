"""Reference template for writing a PyPLUTO manager class.

This module is **not** part of the public API: it is not imported from
`pyPLUTO/__init__.py` and is never instantiated by real code. It exists
purely as a copy-pasteable reference for the architecture used throughout
`imagefuncs/`, `loadfuncs/` and `toolfuncs/` (see `CONTRIBUTING.md`,
section "Project Structure").

Everything below lives in a single file for readability, but in the real
codebase each numbered piece belongs in its **own** module, all shared by
every manager of a given top-level class (`Image`, `Load`, `LoadPart`):

1. State      -> `pyPLUTO/imagestate.py`   / `pyPLUTO/loadstate.py`
2. Kwargs     -> `pyPLUTO/imagekwargs.py`  / `pyPLUTO/loadkwargs.py`
3. Mixin      -> `pyPLUTO/imagemixin.py`   / `pyPLUTO/loadmixin.py`
4. Manager(s) -> `pyPLUTO/imagefuncs/<name>.py` (one file per manager, e.g.
   `imagefuncs/plot.py`, `imagefuncs/gridplot.py`, `imagefuncs/legend.py`)
5. Facade     -> the top-level class itself, e.g. `pyPLUTO/image.py`

A new manager therefore does NOT get its own state/mixin/kwargs module: it
imports the *existing* `ImageState`/`ImageMixin`/`imagekwargs` (or their
`Load` equivalents) from those shared files and only adds its own
`imagefuncs/<name>.py` (step 4) plus a couple of TypedDict/property entries
in the shared files (steps 1-3) and a couple of wrapper lines in the facade
(step 5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict, Unpack

from pyPLUTO.utils.inspector import track_kwargs

# ---------------------------------------------------------------------------
# 1. STATE - normally in its own file, e.g. `pyPLUTO/imagestate.py`.
#
# The single source of truth, shared BY REFERENCE across every manager and
# the top-level class: each manager's `__init__` receives this same
# instance, so mutating `self.state.foo` in one manager is immediately
# visible to every other manager and to the top-level class. Plain
# dataclass, no behavior - compare to the real `ImageState`/`LoadState`.
# ---------------------------------------------------------------------------


@dataclass
class ExampleState:
    """Class that stores the state of the Example top-level class."""

    label: str = ""
    values: list[float] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 2. KWARGS - normally in its own file, e.g. `pyPLUTO/imagekwargs.py`.
#
# One TypedDict per method (or family of related methods), `total=False`
# since every key is optional. A key must NOT duplicate an explicit,
# positional parameter of the method it types (e.g. `factor` below is a
# named parameter of `rescale`, so it is absent here - only kwargs-only
# options belong in the TypedDict). In the real codebase these TypedDicts
# form an inheritance chain, e.g. `PlotKwargs` also carries every key
# accepted by the axis-setup/range/legend calls that `plot()` forwards
# kwargs to, so a method that calls another manager automatically accepts
# (and documents) that manager's keywords too.
# ---------------------------------------------------------------------------


class ExampleKwargs(TypedDict, total=False):
    """Keyword arguments accepted by `ExampleManager.rescale`."""

    label: str | None


# ---------------------------------------------------------------------------
# 3. MIXIN - normally in its own file, e.g. `pyPLUTO/imagemixin.py`.
#
# Property access to the state, inherited by BOTH the top-level class and
# every manager. Keeps `self.foo` ergonomic without duplicating storage:
# there is exactly one `ExampleMixin` in the real codebase (`ImageMixin`),
# not one per manager.
# ---------------------------------------------------------------------------


class ExampleMixin:
    """Mixin class exposing `ExampleState` fields as instance properties."""

    state: ExampleState

    @property
    def label(self) -> str:
        """Get the label attribute of the example state."""
        return self.state.label

    @label.setter
    def label(self, value: str) -> None:
        """Set the label attribute of the example state."""
        self.state.label = value


# ---------------------------------------------------------------------------
# 4. MANAGER - THIS is the part that gets its own new file, e.g.
#    `pyPLUTO/imagefuncs/example.py`.
#
# Implements one cohesive group of operations. Constructed with the shared
# state (and, if it needs to call other managers internally, with instances
# of those managers too - see `PlotManager`, which owns `AxisManager`,
# `ImageToolsManager`, `LegendManager` and `RangeManager`).
# ---------------------------------------------------------------------------


class ExampleManager(ExampleMixin):
    """ExampleManager class.

    It provides the `rescale` method, which multiplies every value stored
    in the state by a constant factor. This docstring should explain what
    the manager is responsible for and which other managers it relies on,
    mirroring `PlotManager`/`GridPlotManager`/`LegendManager`.
    """

    def __init__(self, state: ExampleState) -> None:
        """Initialize the ExampleManager with the given state."""
        self.state = state

    @track_kwargs
    def rescale(
        self,
        factor: float = 1.0,
        _check: bool = True,
        **kwargs: Unpack[ExampleKwargs],
    ) -> list[float]:
        """Rescale every value stored in the state by `factor`.

        Longer description of what the method does, any side effects on
        `self.state`, and pointers to related methods, following the same
        structure as `PlotManager.plot` or `GridPlotManager.showgrid`.

        Parameters
        ----------
        - factor: float, default 1.0
            The multiplicative factor applied to every stored value.
        - label: str, default None
            If given, overwrites `self.state.label`.

        Returns
        -------
        - list[float]

        Examples
        --------
        - Example #1: rescale the stored values by a factor of 2

            >>> state = ExampleState(values=[1.0, 2.0, 3.0])
            >>> mgr = ExampleManager(state)
            >>> mgr.rescale(factor=2.0)
            [2.0, 4.0, 6.0]

        """
        # `track_kwargs` (applied above) inspects this function's source to
        # discover every key read via kwargs['x'] / kwargs.get('x') /
        # kwargs.pop('x'), so that unrecognized keys can be warned about at
        # the outermost call (`_check=True`, the default for methods called
        # directly by users) while calls a manager makes to *other*
        # managers internally pass `_check=False` (see below) to avoid
        # premature/duplicate warnings before the full kwargs set is known.
        if (label := kwargs.get("label")) is not None:
            self.state.label = label

        self.state.values = [v * factor for v in self.state.values]

        # A manager that needs another manager's behavior takes an instance
        # of it in __init__ (e.g. `self.RangeManager = RangeManager(state)`)
        # and calls it here with `_check=False`, e.g.:
        #     self.OtherManager.some_method(ax, _check=False, **kwargs)

        return self.state.values

        # End of the function


# ---------------------------------------------------------------------------
# 5. FACADE - not a new file: a few lines added to the existing top-level
#    class, e.g. `pyPLUTO/image.py`. Shown as reference only (commented out)
#    since it needs the real top-level class to run. The facade method's own
#    docstring is a one-line placeholder; the last line below copies the
#    manager method's full docstring onto it (`rescale.__doc__ = ...`) so
#    that `help(Example().rescale)` / `Example().rescale?` show the complete
#    documentation to users calling it through the top-level class.
# ---------------------------------------------------------------------------

# class Example(ExampleMixin):
#     def __init__(self) -> None:
#         self.state = ExampleState()
#         self.ExManager = ExampleManager(self.state)
#
#     def rescale(
#         self, factor: float = 1.0, _check: bool = True, **kwargs: Any
#     ) -> list[float]:
#         """Rescale method."""
#         return self.ExManager.rescale(factor=factor, _check=_check, **kwargs)
#
#     rescale.__doc__ = ExampleManager.rescale.__doc__

# ---------------------------------------------------------------------------
# Updating the documentation: the Sphinx docs under `Docs/source/` do not
# pick up a new method automatically. For each new public method, add a
# `Docs/source/<method>.rst` page with an `.. automethod::` directive
# pointing at the MANAGER method (not the facade), e.g.:
#     .. automethod:: pyPLUTO.imagefuncs.example.ExampleManager.rescale
# (see `Docs/source/streamplot.rst` for a working example), then list
# `<method>` in the relevant `toctree` (e.g. `Docs/source/imageclass.rst`
# for `Image` methods, `Docs/source/loadclass.rst`/`toolsmethods.rst` for
# `Load`/tool methods). Rebuild locally with `make -C Docs html` to check
# the new page renders and is reachable from the toctree.
# ---------------------------------------------------------------------------
