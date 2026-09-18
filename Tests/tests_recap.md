# Tests recap

**1724 tests** · in-scope coverage **81.0%** · target 100%

| Status | Files |
|---|---|
| reviewed | 19 |
| almost | 0 |
| to review | 45 |
| to write | 5 |
| out of scope | 5 |

- **reviewed** — every step of the per-file checklist below is done,
  documentation included, and coverage is at 100%.
- **almost** — the checklist is done, but coverage is not yet 100%.
- **to review** — tests exist, not yet checked.
- **to write** — no test file of its own (coverage comes from other files).
- **out of scope** — `amr`, `findlines`, `nabla`, `transform`, and
  `codes/echo_load` (waiting on ECHO test data, not in the repository yet).

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
| `codes/echo_load.py` | — | — | 20% | out of scope |
| `gui/app_state.py` | `gui/test_app_state.py` | 22 | 100% | to review |
| `gui/custom_var.py` | — | — | 19% | to write |
| `gui/custom_var_engine.py` | `gui/test_custom_var_engine.py` | 21 | 75% | to review |
| `gui/globals.py` | `gui/test_globals.py` | 6 | 100% | to review |
| `gui/load_controller.py` | `gui/test_load_controller.py` | 11 | 80% | to review |
| `gui/main.py` | `gui/test_main.py` | 8 | 100% | reviewed |
| `gui/main_window.py` | `gui/test_main_window.py` | 4 | 81% | to review  |
| `gui/panels.py` | — | — | 84% | to write |
| `gui/plot_controller.py` | `gui/test_plot_controller.py` | 17 | 70% | to review |
| `gui/services.py` | `gui/test_services.py` | 30 | 88% | to review |
| `gui/state_accessors.py` | `gui/test_state_accessors.py` | 15 | 100% | to review |
| `image.py` | `test_image.py` | 116 | 100% | reviewed |
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
| `imagemixin.py` | `test_imagemixin.py` | 107 | 100% | reviewed |
| `imagestate.py` | `test_imagestate.py` | 49 | 100% | reviewed |
| `load.py` | `test_load.py` | 69 | 100% | reviewed |
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
| `loadpart.py` | `test_loadpart.py` | 32 | 100% | reviewed |
| `loadstate.py` | `test_loadstate.py` | 83 | 100% | reviewed |
| `template.py` | `test_template.py` | 42 | 100% | reviewed |
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
| `utils/inspector.py` | `utils/test_inspector.py` | 35 | 100% | reviewed |
| `utils/pytools.py` | `utils/test_pytools.py` | 10 | 92% | to review |
| `utils/resolver.py` | `utils/test_resolver.py` | 26 | 100% | reviewed |

## Roadmap

One family at a time, and inside each family from the files others depend on
up to the ones that use them, so every review can lean on the ones before it.

1. **`imagefuncs/`** — the managers `image.py` delegates to.
   `imagetools` → `range` → `figure` → `create_axes` → `set_axis` →
   `legend` → `plot` → `scatter` → `display` → `contour` → `streamplot` →
   `colorbar` → `gridplot` → `zoom` → `interactive` → `volume` →
   `volengine` (last: likely needs the split noted below first).
2. **`loadfuncs/`** — in the order of the load pipeline, where most open
   bugs are. `initload` → `findformat` → `findfiles` → `descriptor` →
   `readdefplini` → `codeselection` → `loadvars` → `offsetdata` →
   `offsetfluid` → `offsetpart` → `readgridfile` → `readgridalone` →
   `readtab` → `storepart` → `read_files` → `write_files` → `baseloadtools`.
   Afterwards: the open `loadfuncs` bugs that were too large to fix during
   the review, then the structural items (`is_particle`, grid shapes,
   `resolve_endianess`).
3. **`toolfuncs/`** (built on `Load`) — `loadtools` → `parttools` →
   `fourier` → `compute_units` → `set_units`; then **`utils/`** —
   `configure` → `pytools` → `examples_cli` → `examples_api`.
4. **`gui/`** (built on both `Load` and `Image`) — `globals` → `app_state` →
   `state_accessors` → `services` → `main_window` → `load_controller` →
   `plot_controller` → `custom_var_engine` → `panels` → `custom_var`.

Before the multiprocessing work: fix the copy/pickle bug of the facades.
After every phase: run `_test_examples.py`, a full coverage run, and update
the totals at the top.

## Other

- `conftest.py` — reviewed (fixtures `qapp`, `window`; typed).
- `_test_examples.py` — the end-to-end check: every script in `Examples/` is
  run in an isolated copy and its figures compared pixel by pixel with
  `Tests/Ref_figs/`. Not collected by pytest (the leading underscore) because
  the field-line examples make a run take over a minute; once `rastra` makes
  those fast it can join the suite. **Run it by hand after every few files,
  and always before a release**:

  ```console
  $ pytest Tests/_test_examples.py              # as a test
  $ python Tests/_test_examples.py --check      # list what differs
  $ python Tests/_test_examples.py --update     # rewrite those references
  ```

  A size that differs by one pixel is matplotlib rounding a tight bounding
  box the other way and is safe to accept; a differing region inside a frame
  is a real plotting change and must be understood first.

## Per-file checklist

A file moves to **reviewed** only when all of this is done, for the source
file *and* its test file. Documentation is part of the review, not a later
pass: a file is finished when a new developer can read it.

1. **Tests** — read every existing test and keep it (fix it if wrong, never
   drop it). pytest only, no `unittest`. One `test_<file>.py` per source file,
   placed as described in *Layout*.
2. **Coverage** — reach a *meaningful* 100%: each test proves a behaviour,
   not just that a line ran. No permanently skipped tests; an empty
   parametrize set gets a non-vacuity guard instead.
3. **Expected values** — hand-written, in the test or in the matching
   `helper_<family>.py`; never derived from the code under test.
   Completeness guards use separate `missing` / `stale` asserts.
4. **Typing** — the test file is fully annotated and clean under the type
   checkers.
5. **Source docstrings** — detailed, in the style of `imagefuncs/figure.py`:
   a summary line, then what the function is for and why it works that way,
   then `Parameters` / `Returns` / `Examples`.
6. **Source comments** — one or two lines at a time, often enough that the
   intent of each step is clear, never a restatement of the code.
7. **Test docstrings** — no `Parameters` / `Returns` structure; say what the
   test does, what the check represents, and therefore what a failure would
   mean. Any leftover `LONG TEST: CHECK` marker is resolved and removed: a
   reviewed file has none.
8. **Findings** — a bug that is easy to fix is fixed during the review,
   guarded by a test that fails without the fix, and recorded in *Fixed
   bugs*. Anything larger goes in *Open bugs* (confirmed, with the
   reproducer) and is fixed later, even when it sits in a file already
   marked reviewed: that file keeps its status. Design smells go in
   *Deferred structural improvements* or *Potential improvements*.
9. **Bookkeeping** — update the file's row and the totals at the top; run
   `_test_examples.py` after every few files.

## Deferred structural improvements

Not bugs, and none of them urgent. Noted here so they are not rediscovered
from scratch each time.

| Where | What, and why it is worth doing |
|---|---|
| `load.py`, `image.py`, `loadpart.py` | The facade layer is retyped three times: the delegating method bodies, the `x.__doc__ = Manager.x.__doc__` lines, and the method list inside `__str__`. All of it is derivable from one table — which already exists, as `DELEGATION` in the test helpers. Generate it, or assert it. Both `__str__` staleness bugs and the missing `hasattr` guard in `LoadPart` came from retyping. |
| `baseloadmixin.py`, `loadmixin.py`, `imagemixin.py` | Every state field is written twice: once as a field, once as a property pair. Generating the mixins from the states would remove that, but only at author time: producing the properties at runtime (a class decorator over `dataclasses.fields`, or `__getattr__` forwarding) would make them invisible to pyright and to editor completion, which is the only reason the mixins exist — the facades already forward through `__getattr__` at runtime. So: a script that writes the mixin from the state, run by pre-commit, output committed, with CI checking it is current. The same script could emit the facade methods and `__str__` lists from `DELEGATION`, removing all three sources of drift at once. Note the drift is already *detected* by `test_every_property_is_listed`; generation turns "the test says what to add" into "nothing to add". |
| `utils/inspector.py` | `_check` is declared and threaded by hand through every manager method. The ContextVar already knows whether a call is the outermost one, so the flag could be inferred rather than passed, removing it from every signature. |
| `imagestate.py`, `imagefuncs/create_axes.py` | Eleven parallel per-axis lists (`legpar`, `legpos`, `nline`, `ntext`, `setax`, `setay`, `shade`, `tickspar`, `vlims`, `xscale`, `yscale`) are kept in step only by the loop over `ax_pars` in `create_axes.py`, which is already a per-axis record written as data — the commented-out `# "ax": ax` shows it. Making it an `AxisState` dataclass and holding `axes: list[AxisState]` would remove the misalignment bug class entirely (one append instead of eleven), drop the `copy.copy` that only exists because mutable defaults are shared in a dict literal, make a new per-axis property one line instead of four edits, and type `vlims[nax]` properly. Costs: `ImageMixin` exposes each list as a public property, so they become computed views or it is a breaking change, and every `imagefuncs` manager needs a mechanical rename. Safe to do *after* the documentation pass, guarded by the full suite and the pixel-exact example tests. |
| `loadfuncs/*` | **Two competing answers to "is this a particle load".** Some managers compare `state.class_name` as a string (`findformat.py:80`, `findfiles.py:96,176`, `loadvars.py:207,299`), others use `isinstance(state, LoadState)` (`initload.py:108,118,131`, `offsetdata.py:22,71,86`, `codeselection.py:42`). `class_name` is set in the facade from `self.__class__.__name__`, so it is a stringly-typed second copy of what the state's own type already says. Consequence, confirmed: `class MyLoad(pp.Load): pass` then `MyLoad(path=...)` raises `NameError: Invalid class name.` — the package cannot be subclassed. The file stems `"data"` and `"particles"` are hard-coded alongside each test. Fix: make the state type authoritative — one `is_particle` and one `file_stem` property on `BaseLoadMixin`; the four "invalid class name" raises then disappear. |
| `loadfuncs/readgridfile.py:80`, `readgridalone.py:176`, `offsetfluid.py:298` | The derivation of `nshp`, `nshp_st1..3`, `gridsize`, `gridsize_st1..3` and cell centres from faces is written three times — an if/elif chain, a `GRID_SHAPES` lambda table, and a third hand-written chain inside the vtk header parser — plus a fourth copy of the table kept as a string literal at `readgridfile.py:60`. The face→centre formula `0.5*(xr[:-1]+xr[1:])` appears twice more. Fix: one `set_shapes_from_nx()` and one `centres_from_faces()` on a grid manager, called from all four readers. |
| `imagefuncs/volengine.py` | 838 statements in one module, at 59% coverage. It is several responsibilities that could be split and tested separately; the size is what makes the coverage hard to move. |
| `baseloadstate.py`, `loadstate.py` | A field with no default raises a bare `AttributeError`, so a fresh state reads as half-initialised. A sentinel with a message ("not loaded yet — call Load(...) first") would say what actually happened. |
| `load.py` (`__getattr__`) | A failed attribute read could suggest the closest known name (`difflib` over the fields plus `d_vars` keys): `'rho2' — did you mean 'rho'?`. It runs only on the failure path, so it costs nothing in normal use. |
| `utils/inspector.py` | The whole kwargs scanner is to be rewritten in Rust as the `kwarden` package (already on PyPI). `Tests/utils/test_inspector.py` is in effect its specification: which forms are recognised, the nested-call protocol, the `_check` handling. A Rust parser also pins its own grammar version instead of inheriting the host interpreter's `ast`, which removes the "node shapes change with the Python release" risk noted in `_get_str_from_slice`. |
| `__init__.py`, `utils/configure.py` | `Configure` runs at import with switches nobody can set beforehand (see the open bug). Either read them from environment variables (`PYPLUTO_GREET=0`), or make configuration a call the user can make after import that reconfigures the handlers, or both. Decide together with whatever `set_text` becomes. |
| `load.py` (`__setattr__`) | An unknown name is created silently, so a typo'd assignment fails nowhere. Cannot simply be forbidden: users deliberately attach composite variables (`data.my_composite = rho * T`) and pass the load into their own functions. Needs a design that blesses that case explicitly while still catching typos — to be discussed. |

## Open bugs

| Where | What |
|---|---|
| `load.py`, `loadpart.py`, `image.py` (`__getattr__`, `__setattr__`) | **The facades cannot be copied or unpickled, so they cannot be sent to a `multiprocessing` worker.** `__getattr__` reads `self.state`; on an instance that has no state yet, that read calls `__getattr__("state")` again, forever. `copy` and `pickle` both build the new instance without running `__init__` and then look up `__setstate__`, which takes exactly that path. Confirmed: `copy.copy` and `copy.deepcopy` raise `RecursionError` on `Load`, `LoadPart` and `Image`; `pickle.dumps` of `Load` and `Image` succeeds but `pickle.loads` raises `RecursionError`; any attribute read or write on `Image.__new__(Image)` does the same. `LoadPart` also fails `deepcopy`/`pickle` for a second reason, `cannot pickle 'mmap.mmap' object` (see the `mmaps` bug below). Nothing tests copy or pickle. The `not hasattr(self, "state")` clause in `__setattr__` belongs to the same bug: its docstring says it "makes the first line of `__init__` possible", but `name == "state"` already handles that line, and if the clause ever ran it would recurse too. Same wrong docstring in all three; `loadpart.py:262` also still says "the Load class". `template.py` has no attribute hooks, so it neither shows the pattern nor the fix. Fix: `if name == "state": raise AttributeError(name)` at the top of each `__getattr__`, then decide what copying a facade means (share or duplicate the state, reopen or drop the mmaps) before multiprocessing work starts. |
| `loadfuncs/offsetfluid.py:256`, `loadfuncs/offsetpart.py:156` | **Passing the correct `endian` explicitly corrupts the data.** For a standalone vtk load, `offset_vtk` uses `">" if state.endian is None else d_info["endianess"][exout]` — so when the user *does* pass `endian`, it keeps whatever is in that array, which `findfiles.py:94` allocated with `np.empty(dtype="U20")`, i.e. `""`. `binformat` becomes `f4` (native) instead of `>f4`. Confirmed: `Load(path="Tests/Test_load/single_file/vtk", datatype="vtk", alone=True, endian="big")` gives `rho.flat[0] = -1.49e+19`; without `endian=` the same call gives `0.138`. The `if ... is None: raise ValueError("Wrong endianess")` guards at `offsetfluid.py:261`, `offsetpart.py:80,161` are unreachable — `np.empty("U20")` yields `""`, never `None`. The rule is written four times and the copies disagree (`descriptor.py:85`, `offsetpart.py:77` propagate `state.endian` correctly). Fix: one `resolve_endianess()` helper, called from all four sites. |
| `loadfuncs/findformat.py:125` | **`alone=False` is silently ignored.** `check_format` builds `funcf` (lines 125–135) to gate which probes run given `alone`, then the loop at 138 hard-codes both probes and never reads `funcf`. `alone=True` happens to work via `type_out = []` at line 121, but `alone=False` does not: `check_typelon` still runs, finds the standalone files and sets `state.alone = True`. Confirmed on a folder holding only `data.0000.vtk`: `Load(..., alone=False).state.alone` is `True`. The user gets a standalone load with `timelist` full of NaN instead of the `FileNotFoundError` at line 157. |
| `loadfuncs/initload.py:121` | **The deprecated `vars=` keyword is warned about, then discarded.** The shim warns but never assigns to `var`, which stays `True`. Confirmed: `Load(path=..., vars="rho")` warns, then loads `['prs','rho','vx1','vx2','vx3']`. It is also in the wrong layer — `var` was already bound as a positional parameter before the manager ran. The sibling `nfile_lp` shim (`loadpart.py:168`) sits in the facade and does forward its value. |
| `loadfuncs/codeselection.py:69` | **Any non-default `code` on `LoadPart` raises `AttributeError`.** `self.echomanager` is only created `if isinstance(state, LoadState)` (line 42), but the `codedict` literal at line 69 references `self.echomanager.load_echo` eagerly, before the membership test. So it is evaluated on every call. Confirmed: `LoadPart(..., code="echo")` and even `LoadPart(..., code="nosuchcode")` both raise `AttributeError: 'CodeManager' object has no attribute 'echomanager'` — the intended `NotImplementedError` is unreachable for `LoadPart` entirely. |
| `toolfuncs/fourier.py:98` | `fourier(f)` without `dx` raises `KeyError`. |
| `loadfuncs/readtab.py` | `datatype="tab"` leaves `d_vars` empty, so the GUI lists no variables. |
| `imagefuncs/colorbar.py` | Docstring says no colorbar without `cpos`, but the default is `"right"`. |
| `imagekwargs.py` | 260 declared kwargs are undocumented in the method docstrings. ~11 per method are the figure-level ones inherited from `ImageKwargs` (documented on `Image.__init__` instead), but `showgrid` (62 of 68) and `volume` (64 of 87) document almost none of theirs. |
| `utils/inspector.py` | The "Unused kwargs" warning points at the facade, not at the user's line: `I.plot(x, y, nosuchkw=1)` reports `image.py:441`. `stacklevel=2` counts from the wrapper, but the outermost tracked call is the manager method the facade invokes, so the user's own frame is one further up. Fix: walk the stack to the first frame outside the package (`skip_file_prefixes` needs 3.12; the project supports 3.11). |
| `load.py`, `loadpart.py` | Docstring examples use keywords that warn or do not exist: `vars=` (deprecated, `load.py:163,174`, `loadpart.py:93`), `nfile_lp=` (deprecated, `loadpart.py:108`) and `data=` (not a keyword at all, `load.py:168,174` — it is `datatype`). A user copying Example #9 gets an "Unused kwargs: {'data'}" warning from the documentation itself. |
| `loadpart.py` | Class docstring says "only one output can be loaded at a time". False: `nout="all"` loads several, and `test_text_logs_every_output_as_plain_ints` relies on it. |
| `__init__.py`, `utils/configure.py` | `greet`, `colorerr` and `colorwarn` are read once, while `__init__.py` runs, and no environment variable is consulted. A user therefore cannot turn the greeting off: the switch exists but nothing can reach it before import. |
| `baseloadstate.py`, `loadfuncs/loadvars.py:301` | `mmaps` is appended to and never closed anywhere. The file handles live for the whole process, including after `AttrResolver` has copied the data out and the mapping is dead weight. |
| `loadpart.py:164` | `self.cached_vars = set()` is assigned and never read. |
| `_test_examples.py:313` | The `mkdtemp` folder that keeps differing images is never removed, so each `--check` with differences leaves a directory behind in `/tmp`. |

## Potential improvements

Smaller than a redesign, larger than a bug. Each is one file and an
afternoon, and none is urgent.

| Where | What, and why |
|---|---|
| `loadfuncs/read_files.py:128`, `loadfuncs/write_files.py:153` | The dispatch tables never dispatch. `read_file` builds `readers` then uses it only for a membership test: line 143 hard-codes `datatype in {"h5","dat"}` and everything else falls through to `_read_h5`, so `_read_vtk`, `_read_tab` and `_read_bin` are unreachable and their `NotImplementedError` is never seen. `write_files.py` mirrors it, and its two fallback blocks (162–173, 175–189) are byte-identical. Fix: populate the dict with implemented readers only, `reader = readers.get(datatype)`, one fallback. |
| `loadfuncs/readtab.py:103`, `loadfuncs/offsetfluid.py:427` | `load_vars` is written as a plain attribute of throw-away manager instances, while `gui/services.py:44` and `gui/load_controller.py:180` look for it on the facade with `getattr(Data, "load_vars", ...)`. Confirmed: after a `tab` load, `hasattr(D, "load_vars")` is `False`, so the GUI always takes the fallback. Fix: make it a real state field written by `LoadVariables`, or drop it and let the GUI use `d_vars.keys()`, which already knows. |
| `loadfuncs/initload.py:238-253` | `check_path` raises `TypeError(error)` where `error` is itself a `TypeError`, so the message renders as an exception repr; and lines 250–253 test `isinstance(self.state.pathdir, Path)` immediately after line 248 assigned `Path(path)`, which cannot fail. Tidy alongside the "normalise `pathdir` to `Path`" item above. |
| `loadfuncs/loadvars.py:92,156` | The five-line open → `mmap.mmap` → `_track_mm` sequence is duplicated, including the same two commented-out `sys.version_info >= (3,13)` lines. Only the second copy is wrapped in a `try`, so a missing `single_file` data file raises a raw `OSError` while a missing `multiple_files` one gets the friendly "Skipping variable" warning. One `_open_mmap()` helper. |
| `loadfuncs/readgridalone.py`, `loadfuncs/readgridfile.py` | Old implementations kept as bare triple-quoted *statements* rather than comments — confirmed at `readgridalone.py:60,85,106,138,196` and `readgridfile.py:60,141,193`. They are expressions evaluated and discarded at runtime; ruff's B018 deliberately skips string literals, which is why nothing flags them. Roughly 80 lines duplicating live code in the same files. Delete; git history has them. |
| `loadfuncs/initload.py:128` | A full manager tree is rebuilt once per output: each `LoadVariables` builds an `OffsetData`, which builds `GridFileManager`, `OffsetFluid` (with its own `GridManager`) and `ReadtabManager`. `nout="all"` on a 5-output folder builds five of them. The `state.infogrid` flag exists only to make the repeated grid reads idempotent — it would not be needed if the grid were read once. Fix: construct `LoadVariables` once, call it per output. |
| `baseloadstate.py` | `lennout` and `lennoutlist` are redundant with `len(noutlist)` and `len(outlist)`: two copies of one fact, kept in step by hand in `findfiles.py` and `descriptor.py`. Properties on the mixin would remove the drift. |
| `baseloadstate.py` | `nshp: int \| tuple[int, ...]` forces an `isinstance` at every use (the tests hit it). Always a tuple, of length one for particles, would be simpler. |
| `baseloadstate.py` | `pathdir: str \| Path` — normalise to `Path` once in `initload` and drop the union everywhere downstream. |
| `baseloadstate.py` | `matching_files: list[str] \| None = None` while every other container defaults to empty. One convention: empty means "none found". |
| `baseloadstate.py` | `d_info: dict[str, Any]` holds a known set of keys (`endianess`, `varslist`, ...). A TypedDict would let the checkers see them. |
| `load.py:263-264`, `loadpart.py:189-190` | `self.unit_attached.clear()` clears a set that was empty two lines earlier (dead line, duplicated), and the facade calls the private `UnitManager._make_units_dict()`. Both go away with facade generation, or the manager can expose a public method now. |
| `loadkwargs.py` | `vars` and `nfile_lp` are deprecated at runtime but still in the TypedDicts, so editors autocomplete keywords that warn when used. Drop them from the tables, or annotate with `typing.deprecated` (3.13) / a comment. |
| `load.py`, `loadpart.py` | `__repr__` shows `nout=np.int64(0)`. Formatting a scalar with `int()` in the repr only (not in the state, which stays numpy) would print `nout=0`. |
| `baseloadmixin.py:36` | `# pylint: disable=too-many-public-methods` — pylint is not used; ruff is. Dead directive. |
| `utils/resolver.py`, `loadkwargs.py` | Unparametrised containers: `_chunk_dict(val: dict) -> dict`, `FourierKwargs.dx: ... \| list \| ...`. Cheap to make precise. |
| `image.py` | `oplotbox` is the one public method that is not a facade. An `AMRManager` would make it uniform, and lets it join the generated facade later. |
| `image.py` | `__getattr__` routes through `AttrResolver` although an Image holds no mapped data. Kept for symmetry today; decide whether that symmetry is worth the indirection. |
| `utils/inspector.py` | Every decorated function is read and parsed at import time (`inspect.getsource` + `ast.parse`, cached by text). Measure `import pyPLUTO`; if the scan is a visible share, do it lazily on first call. Moot once `kwarden` lands. |
| `utils/resolver.py` | On Windows `mmap.madvise` does not exist, so `_dontneed` is a silent no-op and mapped pages are never released. Not fixable from Python; worth a line in the docs so the memory growth is not reported as a bug. |
| `_test_examples.py` | Fourteen subprocesses run one after another (73 s). Each is fully isolated in its own `tmp_path`, so `pytest-xdist` would run them in parallel with no change to the file. |
| `pyproject.toml` | `Tests/` is excluded from pyright (170 errors today). Add files to its scope one by one as they are reviewed, the way ty already covers them, so a reviewed test file stays clean under both checkers. |
| process | Mutation testing found two holes in `resolver.py` at 100% coverage that no line-coverage tool could see. A periodic `mutmut` run over the reviewed files, or the ad-hoc mutate-and-revert loop used here, is worth institutionalising. |

## Fixed bugs

| Where | What |
|---|---|
| `image.py` | `Image.interactive` did not declare `ax`, which `InteractiveManager.interactive` takes: it worked at runtime through `**kwargs`, but pyright rejected `I.interactive(var, ax=1)` and `help()` did not show it. Its `_check` also sat where the manager has `limfix`, so `I.interactive(x, y, False)` switched off the kwargs check instead of `limfix`. The facade now matches the manager's signature; `test_signature_matches_the_manager` compares all facade signatures with their managers. |
| `imagefuncs/set_axis.py` | `AxisManager.set_axis` required `ax`, although its docstring and the facade give it the default `None`. Default added. |
| `imagefuncs/gridplot.py`, `image.py` | `showgrid` never warned about unused keywords: `track_kwargs` only checks a function that declares `_check`, and `showgrid` was the one public tracked method without it, so `I.showgrid(..., nosuchkw=1)` was silently ignored. `_check` added to the manager and the facade. |
| `utils/inspector.py` | The kwargs scan missed `"key" in kwargs`, so a method acting on the presence of a keyword rather than its value reported it unused. `Image.contour(colors=...)` and `Image.streamplot(colors=...)` worked but warned. `setdefault` was missed too, which nothing depended on but `volume(proj=...)` came close to. |
| `template.py` | The `Example` facade annotated `**kwargs: Any`, with `Any` never imported: it only worked because `from __future__ import annotations` keeps annotations as strings. It now unpacks `ExampleKwargs`, like every real facade. |
| `loadpart.py` | `LoadPart(nout=None)` crashed with `AttributeError: no attribute 'nout'`, although the docstring documents it. `Load` guards the same log line with `hasattr`; `LoadPart` never got the guard. |
| `loadpart.py` | `__str__` advertised only `select` and `spectrum`, not `to_astropy_units` and `to_code_units`. |
| `load.py` | `__str__` advertised a `format` property that does not exist; the field is `datatype`. Caught by `test_str_properties_show_their_field`, which now checks every property line of `Load` and `LoadPart` (the name exists, and the printed value is that field), with `test_str_properties_exist` doing the name half for `Image`. |
| `test_imagekwargs.py` | `test_no_conflicting_key_types` walked `__mro__`, which for a TypedDict is always `(cls, dict, object)`, so it could never fail. Both kwargs test files now walk `__orig_bases__` through a `_chain()` helper. |
| `gui/main_window.py` | `self.code` never assigned. |
| `gui/plot_controller.py` | GUI figure left in pyplot as figure 1; after the window was garbage-collected, `pp.Image()` crashed with `QAction already deleted`. Figure now released in `create_new_figure`; `conftest.py` also runs `plt.close("all")` after each window. |
| `baseloadstate.py` | `repr()` of a fresh state crashed on the unset load-only fields (`repr=False` on all 14 of them). |
| `loadstate.py` | `repr()` of a fresh `LoadState` crashed on its own load-only fields, first `dx1` (`repr=False` on all 20 of them). |
| `image.py` | `__str__` missed `animate`, `showgrid`, `volume` and advertised `tg` (really `tight`) and `fontweight` (never stored). `fontweight` now lives on `ImageState` with an `ImageMixin` property, like `fontsize`. |
