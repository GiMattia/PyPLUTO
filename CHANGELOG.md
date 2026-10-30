# Changelog

All notable changes to this project will be documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.3.0]

### Added (preliminary)
- Volume rendering: `MPLVolumeRenderer` and the `Image.volume` method (`imagefuncs/volengine.py`, `imagefuncs/volume.py`), with new example scripts and tests
- GUI: slider-based playback controls for stepping/replaying outputs (`⏮ ◀ ▶ ⏸ ⏩ ⏭`), lock lines, and color pinning
- `GridPlotManager.showgrid`: new method drawing the cell interfaces of a 2D grid; supports `CARTESIAN`, `POLAR`, `CYLINDRICAL`, and `SPHERICAL` geometries, and draws all lines of each direction with a single `PlotManager.plot` call (instead of one call per line) for a large speedup on dense grids
- `PlotManager.plot`: documented support for 2D `x`/`y` input to draw multiple lines sharing one style in a single call (the primitive `showgrid`'s fast path relies on)
- `src/pyPLUTO/template.py`: reference template documenting the State/Kwargs/Mixin/Manager/Facade architecture used to add a new class
- `pp.PyPLUTOWarning`, the base of PyPLUTO's warnings, so they can be filtered apart from the others
- `axalpha`: the opacity of a whole panel, accepted by `set_axis` and every drawing method. It fades the background, spines, ticks, labels, title, grid, legend, texts and everything drawn on the axis, own alpha included, and is kept per axis (`Image.axalpha`), so what is drawn there later takes it too unless given its own `alpha`. In `zoom` it fades the inset only
- Settings: `greet`, `text`, `colors`, `warnings` and `errors`, set in a `pypluto.toml` (in `~/.config/pypluto/` or in the current folder), with the `PYPLUTO_*` environment variables, or with `pp.configure(...)`, also in a `with` block. `pp.configure()` gives back the settings in use
- `pp.PyPLUTOError`, the base of the errors PyPLUTO raises on purpose; a wrong setting raises one
- Errors and warnings named by what went wrong, each also its closest built-in, in `pyPLUTO.utils.pperrors` (attribute, axis, config, copy, data, internal, missing-feature and option errors) and `pyPLUTO.utils.ppwarnings` (behavior, config, conflict, dependency, deprecation, keyword and option warnings). An internal error, a bug in PyPLUTO, is always shown in full and ends asking to report it; a missing feature ends saying where to ask for it

### Changed (preliminary)
- Updated golden reference images and the example test harness for a newer matplotlib version
- Colormaps: `find_cmap` no longer looks only in `pastamarkers`. A name matplotlib does not know is searched for in the optional packages listed in `imagefuncs.imagetools.CMAP_PROVIDERS` (`cblind`, `pastamarkers`, `seaborn`), in order, each imported only when needed and skipped when not installed; a user can add their own package to the dictionary. A `_r` suffix is honoured by the package's own reversed colormap when it has one, and reversed here otherwise. An unknown name still warns and falls back to `plasma`. `cmasher` and `cmocean` are not searched, since importing them raises matplotlib deprecation warnings; importing either in the script makes its `cmr.`/`cmo.` names resolve through matplotlib. New `cmaps` extra in `pyproject.toml` installs the three searched packages
- `Load`/`LoadPart`: the form of what a load gives back follows the form of `nout`, not the number of outputs found. A single output (`5`, `'last'`, `-1`) gives plain values: each variable an array, `ntime` a float, `nout` an int. A collection (a list, or `'all'`) gives one entry per output: each variable a dict keyed by output, `ntime` and `nout` arrays. This changes two cases, which used to give plain values: a list of one output (`Load([5])`), and `'all'` on a folder holding a single output. Code written for several outputs now works on them unchanged; code that relied on the plain values there should index the output (`D.rho[5]`) or ask for it as a number.
- Axis sharing: one pair of keywords, `sharex`/`sharey`, read by `create_axes` and by every drawing method. They take `True`, `'all'`, `'row'` and `'col'` (the last two in `create_axes` only), an index or an `Axes`. In a drawing method `sharex=True` used to raise a `TypeError`, and in `create_axes` `sharexaxes=False`, the documented default, raised an `IndexError`. `sharexaxes`/`shareyaxes` still work, with a `DeprecationWarning`
- `Image`: `close` and `replace` are one keyword, `replace`, which empties the window and builds a new figure. It defaults to replacing, except when a figure is given with `fig`, which is then left alone and used. `close` still works, as deprecated
- `display`: a map is framed on the cell edges instead of the cell centres, so the outermost half cell of the domain is no longer cut off. Coordinates given as edges are used as they are, and `gouraud` shading covers the same domain. Three example figures change by that half cell
- `contour`/`streamplot`: the `colors` keyword, which did nothing, is removed and warns as unknown; use `c`
- `colorbar` returns the `Colorbar` it draws, instead of `None`
- `legpos` in `plot` and `scatter`, with nothing labeled on the axis, draws no legend and warns, instead of an empty frame with matplotlib's warning. The position is remembered, so the first labeled drawing brings the legend
- Layout keywords (`ncol`, `nrow`, `left`, `right`, `top`, `bottom`, `wspace`, `hspace`, `wratio`, `hratio`) given to a drawing method without `ax` create new axes, as `create_axes` does, also on a figure that already has some, with a warning; before, they were ignored there and reported as unused. The drawing goes on the last new axis
- `alpha` is the opacity of one drawing only (the lines of `plot`, the map, the contours, the streamlines and their arrows, the points), and defaults to `None` instead of a fixed 1.0, so a drawing without it takes the panel's `axalpha`. `plot` now reads it too
- `plot` returns the lines it draws, instead of `None`
- Dependencies: `marimo` is no longer installed (it was unused); `numexpr` is installed only with the `gui` extra, the only part that uses it
- `text`: the same three values for each object and for the package. `pp.set_text(False | None | True)` sets the package (only warnings / the ordinary information / also the debug details), and `text=` on `Image`, `Load` and `LoadPart` decides for that object alone, `None` following the package. The value given is kept as `classlog`, so `Load(...).text` is now `Load(...).classlog`
- `find_fieldlines`: `text` is deprecated and has no effect; the details of each line follow the text of the load, or `pp.set_text(True)`
- `text` also takes `"default"` and `"verbose"` (`True` is `"verbose"`); on `Image`, `Load` and `LoadPart`, leaving it out follows the package
- Only PyPLUTO's own errors and warnings are colored by default; the others keep Python's format
- A PyPLUTO error is shown without the frames inside PyPLUTO; `errors="full"` gives the whole traceback
- `pp.colorerr`, `pp.colorwarn` and `pp.greet` are removed: they were read before they could be set. Use the settings instead
- Ticks labels go only on known ticks: those given in the same call or, on an axis of the figure, in an earlier one (new `TicksManager`, `imagefuncs/ticks.py`). Labels without ticks, or in a number different from the ticks, are ignored with a warning; ticks given alone get automatic labels again. Labels can be numbers, written as matplotlib writes a value (`3e4` as 3×10⁴). `minorticks="off"` stays until `"on"` is given
- Requires matplotlib 3.9 or later
- Development: uv is required and pixi is optional. The pixi lock check is skipped where pixi is not installed and always runs in CI; `dev-sync.sh` stops without uv; the contributing guide has a first-time setup and no longer offers pip

### Fixed
- `Load`/`LoadPart`: `ntime` was declared as an `int`; it is the simulation time, a float. `ntime` and `nout` are now typed from the call, as the variables already were: `Load(5).ntime` is a `float` and `Load([0, 1]).ntime` an array of floats for the type checkers, and `nout` an `int` or an array of integers. Indexing them is accepted only where it works.
- GUI: Qt canvas now uses `FigureCanvasQTAgg` from `matplotlib.backends.backend_qtagg` instead of an incorrect `backend_qt`/`backend_template` import; added a GUI canvas regression test
- `Tests/test_gui_canvas.py`: read source files as UTF-8 explicitly, fixing a `UnicodeDecodeError` on the Windows CI runner (default `cp1252` locale encoding could not decode the playback-control glyphs in `main_window.py`)
- `set_axis`: the `tight` keyword now updates `self.state.tight` before deciding whether to reinforce `tight_layout()`
- `Image.showgrid`/`GridPlotManager.showgrid`: `geom` no longer overrides a `Load`'s actual geometry with a hardcoded `"CARTESIAN"` default when `data` is given; fixed a `Data`/`data` keyword-name mismatch in the `Image` facade that bypassed the explicit `data` parameter
- `Image.text`: its own documented keywords (`textsize`, `horalign`, `veralign`, `bbox`, `xycoords`) no longer raise a spurious "Unused kwargs" warning, and a misspelled keyword is now reported against `text` instead of `assign_ax`
- `Image.text`: the `horalign` keyword is declared in `TextKwargs`, which spelled it `horlign`, so type checkers rejected a keyword that worked and was documented
- `find_cmap` no longer returns non-colormap attributes of a colormap package (`find_cmap("count")` returned a method of the `pastamarkers.salsa` named tuple)
- `Image.showgrid`: a misspelled keyword is now reported, the method being the only tracked one without the internal `_check` flag
- `Image.interactive`: the `ax` keyword is declared on the facade, so type checkers accept it and `help()` shows it; `_check` no longer sits where the manager has `limfix`, which made a third positional argument switch off the keyword check
- `AxisManager.set_axis`: `ax` now defaults to `None`, as its docstring and the facade already said
- `Load`, `LoadPart`, `Image`: `copy`, `deepcopy` and `pickle` raised a `RecursionError`; they now raise a `TypeError` explaining that a pyPLUTO object is not copied, and for loads how to analyse outputs in parallel (pass the output numbers to the workers and load inside each)
- The "Unused kwargs" warning points at the user's own line instead of a file inside pyPLUTO
- `plot`/`scatter`: the legend keywords given with `legpos`, also `legpos=None`, are no longer reported as unused when no legend is drawn; without `legpos` they still are (new `switch_keys` option of `track_kwargs`)
- `plot`/`legend`: with ty checking for Python 3.13 or later, a single colour such as `c="r"` or `c=I.color[i]` was rejected, since ty drops `str` from a union holding numpy's `ArrayLike`. `c` is declared as a colour, a sequence of colours, a sequence of RGB lists, an array or `None`
- Drawing methods no longer declare the keywords only `Image` reads (`withblack`, `withwhite`, `style`, `nwin`, `numcolors`, `LaTeX`, `fontweight`, `suptitlesize`, `replace`): type checkers accepted `plot(withblack=True)`, which then warned as unused
- `set_axis`: the `alpha` keyword faded nothing, since it was set on the Axes artist, which draws nothing. It is removed (and reported as unused); `axalpha` takes its place
- Importing pyPLUTO no longer overrides the warning filters: only pyPLUTO's own warnings are shown every time, so `-W ignore` and earlier `filterwarnings` calls work again, and other packages' deprecations stay hidden as Python intends (matplotlib's Qt backend printed one per toolbar icon)
- Errors: the colored report of an uncaught error shows its type and any error chained to it, as Python's own report does, instead of only the frames and the message. `set_text()` can be called without arguments, giving the ordinary information, and importing pyPLUTO no longer adds a filter hiding a deprecation from `astroid`, a package pyPLUTO does not use
- The greeting can be turned off, with `greet = false` in `pypluto.toml` or `PYPLUTO_GREET=false`
- `text=False` on one object no longer silences every other: each `Image`, `Load` and `LoadPart` used to set the level of the whole package, so the last one built decided for all. The "No definitions.h is read!" and "No pluto.ini is read!" messages now follow `text` too, and `find_fieldlines` details no longer depend on an earlier `Load(text=True)`
- Without `ax`, every method uses the last axis considered, as documented, instead of matplotlib's current axis: `display(ax=1)`, `display(ax=0)`, `colorbar()` now puts the bar beside the first panel. After `create_axes`, and after a drawing on an empty figure, that is the last axis created. The axis is readable as `Image.lastax`
- `plot`: `ncol`/`nrow` on an empty figure create the whole grid asked for, instead of one axis; a 2D plot can have one colour per line (`c=["r", "b", "g"]`), cycled with a warning when the count does not match; a single 2D array no longer crashes; `c=None` takes the palette and an RGB array as `c` no longer raises
- Ranges and ticks: the y-limits come from the points inside the x-limits, so a hand-given `xrange` is respected; a log range keeps its widest value when negative and no longer starts at 0. A single string as `xtickslabels`/`ytickslabels`/`ctickslabels` is declared; fixed ticks on a log scale keep their labels, and removing them removes the minor ticks too. The ticks and labels given, and `minorticks`, are given back after a scale, which used to reset them
- `scatter`: no longer freezes the axis for what is drawn after it; `label` reaches the legend; the default colour comes from the palette; a colour per point is no longer read as data; unfilled markers no longer warn; integer markers are no longer redrawn as circles
- `legend`: custom labels honour `mscale` and take the palette instead of black; each legend is attached once, not twice
- `create_axes`: a fontsize and a size given to it reach the state, and so does the size computed from the grid; a `tight` overruled by a custom layout now warns
- `zoom`: the inset copies everything drawn on the axis (lines, scatter, contours, streamlines over a map), not only a map or plain curves; `top`/`right` given with a size or alone place the inset where asked; the tight layout of the figure is switched off only for an inset with its own colorbar; `width`, `height` and `label` are declared
- `colorbar`: works after `contour`, `streamplot` or lines, taking the last collection coloured by data; a second colorbar no longer crashes; contour lines get a continuous bar instead of blocks; `ctickslabels` works with an array of `cticks`, and ticks follow the same rules as `xticks`
- `contour`/`streamplot`/`display`: `transpose` works on rectangular fields (and `transpose=1` on `display`); `c` together with `cmap` warns and drops the colormap instead of crashing; `streamplot` colours the lines by the magnitude when given `cmap` or `cpos`, takes the palette otherwise, applies `alpha`, accepts lists and no longer copies the field
- `Image(fig=...)`: the figure given is no longer closed, the keywords given with it are applied, `nwin` with it warns, and its tight layout is kept
- Field lines (`find_fieldlines`) end exactly on the domain border instead of past it
- Smaller fixes: `assign_ax` refuses an index out of range with a `ValueError`; a wrong `xycoords` and an unknown `cscale` are reported; `legpad`, `zoomcolor`, `zoomlines`, the `"both"` value of `grid` and a sequence for `chnk` are declared; `reshape_cartesian` and `oplotbox` no longer warn about keywords they use; the GUI no longer leaves its figure in pyplot; `repr()` of a fresh state no longer crashes; docstrings and `__str__` listings that named wrong or missing keywords are corrected

---

## [1.2.6] — 2026-10-03

### Fixed
- Loading: the first access to a variable copied the whole variable into memory, so slicing a large output read the entire file (a slice of a 1024³ variable took 16 s and 13 GiB instead of 0.09 s and 0.15 GiB). Present since 1.2.0. Variables are now handed back as memory-mapped views, so a slice reads only the part of the file it covers. The files are mapped copy-on-write, so a variable can still be modified in memory without touching the file.

---

## [1.2.5] — 2026-09-23

### Fixed
- AMR boxes: in CARTESIAN geometry `oplotbox` passed the level colour to `plot` as `color`, which that method does not read, so every box took the next colour of the palette instead of the colour of its level. A single colour for the whole overplot can now be given with `c`, which used to clash with the per-level one.

---

## [1.2.4] — 2026-07-06

### Changed
- Bumped `matplotlib` from 3.10.9 to 3.11.0

### Fixed
- Units: removed `UnitManager._units_from_defh`, which read `UNIT_*` scales directly out of the parsed `definitions.h` dict; this source was never validated against real `definitions.h` files (only injected as a plain dict in tests) and sat ahead of the physics-module defaults in the priority chain, so a malformed or stale `UNIT_*` macro in `definitions.h` could silently override reliable log-derived units. Priority is now user-defined → log → physics module → classical MHD. `defh` itself (the parsed `definitions.h` dict) is untouched and still used elsewhere (e.g. `PHYSICS` lookup for physics-module defaults)
- Particles: added the `time` info, read from the particle file header into `ntimelist` (`loadfuncs/offsetpart.py`)

---

## [1.2.3] — 2026-06-11

### Fixed
- `set_axis`: the `tight` keyword now updates `self.state.tight` before deciding whether to reinforce `tight_layout()`, fixing interactive re-runs that passed `tight=False`

### Changed
- Documentation build configuration and installation instructions updated

---

## [1.2.2] — 2026-06-09

### Fixed
- GUI: Qt canvas now uses `FigureCanvasQTAgg` from `matplotlib.backends.backend_qtagg` instead of an incorrect `backend_qt`/`backend_template` import

### Added
- GUI canvas regression test

---

## [1.2.1] — 2026-06-08

### Changed
- Updated citation info in `README.md` to point to the published JOSS paper instead of the arXiv preprint

---

## [1.2.0] — 2026-06-06

### Added
- `@track_kwargs` decorator applied to all public `**kwargs` methods; warns on unknown kwargs at call sites
- `_check: bool = True` explicit parameter on every `**kwargs` function; internal calls pass `_check=False`
- `from __future__ import annotations` in all package modules
- Units support (first implementation)
- Multiple-output chunk loading
- `set_text(text)` public function to control logging verbosity at any point in a session
- `__repr__` on `Load`, `LoadPart`, and `Image`

### Changed
- Complete refactoring of `Load` and `LoadPart` into manager subclasses
- GUI refactored to controller/service pattern
- Removed `pandas`/`dask` and `gridout` dependencies
- Replaced all library-level `print()` calls with `logging.getLogger(__name__)`; the package logger is wired to stdout automatically at import time
- `text` parameter semantics unified across `Load`, `LoadPart`, and `Image`: `None` (default) → standard INFO output, `False` → silent, `True` → full DEBUG logging
- `_kwargs_state` global mutable dict replaced with `contextvars.ContextVar` for thread- and async-safe kwargs tracking
- `track_kwargs` precomputes signature metadata at decoration time instead of per call
- `_check` hidden from public introspection (`help()`, IDE autocomplete, `@overload` stubs)
- Version single source of truth moved to `pyproject.toml`; `__version__` reads from `importlib.metadata` at runtime

### Fixed
- Custom variables bug in GUI
- Small bug in particles + `self.state` handling
- `LoadPart`: requesting a non-existent `chnk` now emits a `UserWarning` listing available chunks instead of silently producing an empty object that raises `AttributeError` on attribute access; for multi-output loads, only outputs that contain the requested chunk are loaded

---

## [1.1.5] — 2026-04-29

### Added
- Python 3.11 support
- Windows golden test environment via `uv`

### Changed
- Renamed `format` parameter to `datatype` throughout the loading API
- Moved all CI/CD workflows from `pip` to `uv`

### Fixed
- GUI bug fixes (general)

---

## [1.1.4] — 2026-04-19

### Changed
- Automated dependency updates via Dependabot for GitHub Actions
- CI: pinned all GitHub Actions to immutable commit hashes
- Updated `setuptools` requirement to `>=82.0.1`
- Added `uv.lock` upgrade automation

---

## [1.1.3] — 2026-04-19

### Changed
- Updated `CONTRIBUTING.md`
- Added `uv` and `pixi` installation badges to README
- Switched lock-file check to `uv`

---

## [1.1.2] — 2026-04-18

### Added
- Full `Load` class refactoring into dedicated manager classes
- `LoadPart` improvements and refactoring
- 1D, 2D, and 3D automated test suites
- ECHO code loader (`EchoLoadManager`)
- Support for `idefix.ini` alongside `pluto.ini` via `inifix`
- `inifix` as a hard dependency
- Windows compatibility fix for tab-file reading
- Parallel test execution via `pytest-xdist`

### Fixed
- `.T` transpose bug in HDF5 file loading
- Type annotation error in ECHO loader
- Warning formatting for `pluto.ini`

---

## [1.1.1] — 2025-09-16

### Fixed
- Minor corrections following JOSS paper proofs review
- Version string updated in `configure.py`

---

## [1.1] — 2025-07-22

### Added
- `Configure` class for package initialisation (session detection, coloured warnings/errors)
- `coverage_tests.py` and automated coverage badge via GitHub Actions
- `mypy` strict check integration
- Documentation table and docstring completeness check

### Changed
- Full refactoring of `Image` and related managers (`ImageTools`, `Range`, `Figure`)
- Switched error colouring from `black` to `ruff` + `ty` in pre-commit hooks
- Removed Windows Server 2019 from CI matrix

### Fixed
- Typo in `configure.py`

---

## [1.0.0] — 2025-01-17

Initial public release.

### Features
- `Load` class: fluid data loading for PLUTO/gPLUTO binary, HDF5, and tab formats
- `LoadPart` class: particle data loading
- `Image` class: full 1D/2D plotting pipeline (display, contour, plot, scatter, streamplot, zoom, colorbar, legend)
- Field-line integration (`find_fieldlines`) and contour extraction (`find_contour`)
- Fourier transform, nabla operators, coordinate transforms
- AMR box overplotting (`oplotbox`)
- GUI (PySide6-based) for interactive data exploration
- Sphinx documentation with worked examples
- CI on Linux, macOS, Windows across Python 3.11–3.13

[Unreleased]: https://github.com/GiMattia/pyPLUTO/compare/v1.2.6...HEAD
[1.2.6]: https://github.com/GiMattia/pyPLUTO/compare/v1.2.5...v1.2.6
[1.2.5]: https://github.com/GiMattia/pyPLUTO/compare/v1.2.4...v1.2.5
[1.2.4]: https://github.com/GiMattia/pyPLUTO/compare/v1.2.3...v1.2.4
[1.2.3]: https://github.com/GiMattia/pyPLUTO/compare/v1.2.2...v1.2.3
[1.2.2]: https://github.com/GiMattia/pyPLUTO/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/GiMattia/pyPLUTO/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.5...v1.2.0
[1.1.5]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.4...v1.1.5
[1.1.4]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.3...v1.1.4
[1.1.3]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.2...v1.1.3
[1.1.2]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/GiMattia/pyPLUTO/compare/v1.1...v1.1.1
[1.1]: https://github.com/GiMattia/pyPLUTO/compare/v1.0.0...v1.1
[1.0.0]: https://github.com/GiMattia/pyPLUTO/releases/tag/v1.0.0
