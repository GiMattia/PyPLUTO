# Tests recap

**1655 tests** · in-scope coverage **80.0%** · target 100%

| Status | Files |
|---|---|
| reviewed | 15 |
| to review | 48 |
| to write | 7 |
| out of scope | 4 |

- **reviewed** — every test checked, commented and typed.
- **to review** — tests exist, not yet checked.
- **to write** — no test file of its own (coverage comes from other files).
- **out of scope** — `amr`, `findlines`, `nabla`, `transform`.

## Layout

`Tests/` mirrors `src/pyPLUTO/`: `Tests/<folder>/test_<file>.py` for a file in
a subfolder, `Tests/test_<file>.py` for a file in the main folder
(`test_init.py` for `__init__.py`). Test data is reached through the
`data_dir` fixture in `conftest.py`, so the suite runs from any directory.

Expected values shared by several test files live in helper modules at the
top of `Tests/`, named after the class family they describe
(`helper_baseload.py`, `helper_image.py`, ...). They are importable thanks to
`pythonpath = ["Tests"]` in `pyproject.toml`, and are never collected as
tests. Their tables are written by hand: never derived from the code under
test, or a test would compare the code with itself.

## Per file

| Source | Test file | Tests | Coverage | Status |
|---|---|---|---|---|
| `__init__.py` | `test_init.py` | 29 | 100% | reviewed |
| `amr.py` | — | — | 3% | out of scope |
| `baseloadmixin.py` | `test_baseloadmixin.py` | 130 | 100% | reviewed |
| `baseloadstate.py` | `test_baseloadstate.py` | 45 | 100% | reviewed |
| `codes/echo_load.py` | — | — | 20% | to write |
| `gui/app_state.py` | `gui/test_app_state.py` | 22 | 100% | to review |
| `gui/custom_var.py` | — | — | 19% | to write |
| `gui/custom_var_engine.py` | `gui/test_custom_var_engine.py` | 21 | 75% | to review |
| `gui/globals.py` | `gui/test_globals.py` | 6 | 100% | to review |
| `gui/load_controller.py` | `gui/test_load_controller.py` | 11 | 80% | to review |
| `gui/main.py` | — | — | 0% | to write |
| `gui/main_window.py` | `gui/test_main_window.py` | 4 | 81% | to review  |
| `gui/panels.py` | — | — | 84% | to write |
| `gui/plot_controller.py` | `gui/test_plot_controller.py` | 17 | 70% | to review |
| `gui/services.py` | `gui/test_services.py` | 30 | 88% | to review |
| `gui/state_accessors.py` | `gui/test_state_accessors.py` | 15 | 100% | to review |
| `image.py` | `test_image.py` | 90 | 100% | to review  |
| `imagefuncs/colorbar.py` | `imagefuncs/test_colorbar.py` | 11 | 72% | to review |
| `imagefuncs/contour.py` | `imagefuncs/test_contour.py` | 10 | 85% | to review |
| `imagefuncs/create_axes.py` | `imagefuncs/test_create_axes.py` | 14 | 100% | to review |
| `imagefuncs/display.py` | `imagefuncs/test_display.py` | 1 | 94% | to review |
| `imagefuncs/figure.py` | `imagefuncs/test_figure.py` | 20 | 99% | to review |
| `imagefuncs/gridplot.py` | `imagefuncs/test_gridplot.py` | 16 | 97% | to review |
| `imagefuncs/imagetools.py` | `imagefuncs/test_imagetools.py` | 16 | 77% | to review |
| `imagefuncs/interactive.py` | `imagefuncs/test_interactive.py` | 8 | 74% | to review |
| `imagefuncs/legend.py` | `imagefuncs/test_legend.py` | 3 | 100% | to review |
| `imagefuncs/plot.py` | `imagefuncs/test_plot.py` | 11 | 100% | to review |
| `imagefuncs/range.py` | `imagefuncs/test_range.py` | 9 | 91% | to review |
| `imagefuncs/scatter.py` | `imagefuncs/test_scatter.py` | 10 | 78% | to review |
| `imagefuncs/set_axis.py` | `imagefuncs/test_set_axis.py` | 7 | 80% | to review |
| `imagefuncs/streamplot.py` | `imagefuncs/test_streamplot.py` | 8 | 84% | to review |
| `imagefuncs/volengine.py` | `imagefuncs/test_volengine.py` | 49 | 59% | to review |
| `imagefuncs/volume.py` | `imagefuncs/test_volume.py` | 5 | 91% | to review |
| `imagefuncs/zoom.py` | `imagefuncs/test_zoom.py` | 8 | 87% | to review |
| `imagekwargs.py` | `test_imagekwargs.py` | 65 | 100% | reviewed |
| `imagemixin.py` | `test_imagemixin.py` | 108 | 100% | reviewed |
| `imagestate.py` | `test_imagestate.py` | 49 | 100% | reviewed |
| `load.py` | `test_load.py` | 68 | 100% | reviewed |
| `loadfuncs/baseloadtools.py` | — | — | 89% | to write |
| `loadfuncs/codeselection.py` | `loadfuncs/test_codeselection.py` | 6 | 88% | to review |
| `loadfuncs/descriptor.py` | `loadfuncs/test_descriptor.py` | 4 | 100% | to review |
| `loadfuncs/findfiles.py` | `loadfuncs/test_findfiles.py` | 4 | 75% | to review |
| `loadfuncs/findformat.py` | `loadfuncs/test_findformat.py` | 18 | 96% | to review |
| `loadfuncs/initload.py` | `loadfuncs/test_initload.py` | 10 | 89% | to review |
| `loadfuncs/loadvars.py` | `loadfuncs/test_loadvars.py` | 15 | 65% | to review |
| `loadfuncs/offsetdata.py` | — | — | 100% | to write |
| `loadfuncs/offsetfluid.py` | `loadfuncs/test_offsetfluid.py` | 9 | 61% | to review |
| `loadfuncs/offsetpart.py` | `loadfuncs/test_offsetpart.py` | 3 | 79% | to review |
| `loadfuncs/read_files.py` | `loadfuncs/test_read_files.py` | 12 | 92% | to review |
| `loadfuncs/readdefplini.py` | `loadfuncs/test_readdefplini.py` | 15 | 97% | to review |
| `loadfuncs/readgridalone.py` | `loadfuncs/test_readgridalone.py` | 2 | 60% | to review |
| `loadfuncs/readgridfile.py` | `loadfuncs/test_readgridfile.py` | 1 | 65% | to review |
| `loadfuncs/readtab.py` | — | — | 92% | to write |
| `loadfuncs/storepart.py` | `loadfuncs/test_storepart.py` | 3 | 63% | to review |
| `loadfuncs/write_files.py` | `loadfuncs/test_write_files.py` | 11 | 99% | to review |
| `loadkwargs.py` | `test_loadkwargs.py` | 50 | 100% | reviewed |
| `loadmixin.py` | `test_loadmixin.py` | 282 | 100% | reviewed |
| `loadpart.py` | `test_loadpart.py` | 31 | 100% | reviewed |
| `loadstate.py` | `test_loadstate.py` | 83 | 100% | reviewed |
| `template.py` | `test_template.py` | 39 | 100% | reviewed |
| `toolfuncs/compute_units.py` | `toolfuncs/test_compute_units.py` | 14 | 88% | to review |
| `toolfuncs/findlines.py` | — | — | 12% | out of scope |
| `toolfuncs/fourier.py` | `toolfuncs/test_fourier.py` | 9 | 92% | to review |
| `toolfuncs/loadtools.py` | `toolfuncs/test_loadtools.py` | 11 | 96% | to review |
| `toolfuncs/nabla.py` | — | — | 4% | out of scope |
| `toolfuncs/parttools.py` | `toolfuncs/test_parttools.py` | 11 | 94% | to review |
| `toolfuncs/set_units.py` | `toolfuncs/test_set_units.py` | 13 | 82% | to review |
| `toolfuncs/transform.py` | — | — | 12% | out of scope |
| `utils/configure.py` | `utils/test_configure.py` | 16 | 100% | to review |
| `utils/examples_api.py` | `utils/test_examples_api.py` | 14 | 51% | to review |
| `utils/examples_cli.py` | `utils/test_examples_cli.py` | 12 | 87% | to review |
| `utils/inspector.py` | `utils/test_inspector.py` | 15 | 100% | to review |
| `utils/pytools.py` | `utils/test_pytools.py` | 10 | 92% | to review |
| `utils/resolver.py` | `utils/test_resolver.py` | 16 | 100% | to review |

## Other

- `conftest.py` — reviewed (fixtures `qapp`, `window`; typed).

## Open bugs

| Where | What |
|---|---|
| `toolfuncs/fourier.py:98` | `fourier(f)` without `dx` raises `KeyError`. |
| `loadfuncs/readtab.py` | `datatype="tab"` leaves `d_vars` empty, so the GUI lists no variables. |
| `imagefuncs/colorbar.py` | Docstring says no colorbar without `cpos`, but the default is `"right"`. |
| `imagekwargs.py` | 260 declared kwargs are undocumented in the method docstrings. ~11 per method are the figure-level ones inherited from `ImageKwargs` (documented on `Image.__init__` instead), but `showgrid` (62 of 68) and `volume` (64 of 87) document almost none of theirs. |

## Fixed bugs

| Where | What |
|---|---|
| `template.py` | The `Example` facade annotated `**kwargs: Any`, with `Any` never imported: it only worked because `from __future__ import annotations` keeps annotations as strings. It now unpacks `ExampleKwargs`, like every real facade. |
| `loadpart.py` | `LoadPart(nout=None)` crashed with `AttributeError: no attribute 'nout'`, although the docstring documents it. `Load` guards the same log line with `hasattr`; `LoadPart` never got the guard. |
| `loadpart.py` | `__str__` advertised only `select` and `spectrum`, not `to_astropy_units` and `to_code_units`. |
| `test_imagekwargs.py` | `test_no_conflicting_key_types` walked `__mro__`, which for a TypedDict is always `(cls, dict, object)`, so it could never fail. Both kwargs test files now walk `__orig_bases__` through a `_chain()` helper. |
| `gui/main_window.py` | `self.code` never assigned. |
| `gui/plot_controller.py` | GUI figure left in pyplot as figure 1; after the window was garbage-collected, `pp.Image()` crashed with `QAction already deleted`. Figure now released in `create_new_figure`; `conftest.py` also runs `plt.close("all")` after each window. |
| `baseloadstate.py` | `repr()` of a fresh state crashed on the unset load-only fields (`repr=False` on all 14 of them). |
| `loadstate.py` | `repr()` of a fresh `LoadState` crashed on its own load-only fields, first `dx1` (`repr=False` on all 20 of them). |
| `image.py` | `__str__` missed `animate`, `showgrid`, `volume` and advertised `tg` (really `tight`) and `fontweight` (never stored). `fontweight` now lives on `ImageState` with an `ImageMixin` property, like `fontsize`. |
