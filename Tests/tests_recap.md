# Tests recap

**2149 tests** · 54 known bugs as expected failures · in-scope coverage
**83.8%** · target 100%

| Status | Files |
|---|---|
| reviewed | 30 |
| almost | 0 |
| to review | 35 |
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
| `imagefuncs/colorbar.py` | `imagefuncs/test_colorbar.py` | 41 | 100% | reviewed |
| `imagefuncs/contour.py` | `imagefuncs/test_contour.py` | 32 | 100% | reviewed |
| `imagefuncs/create_axes.py` | `imagefuncs/test_create_axes.py` | 47 | 100% | reviewed |
| `imagefuncs/display.py` | `imagefuncs/test_display.py` | 31 | 100% | reviewed |
| `imagefuncs/figure.py` | `imagefuncs/test_figure.py` | 38 | 100% | reviewed |
| `imagefuncs/gridplot.py` | `imagefuncs/test_gridplot.py` | 38 | 100% | reviewed |
| `imagefuncs/imagetools.py` | `imagefuncs/test_imagetools.py` | 46 | 100% | reviewed |
| `imagefuncs/interactive.py` | `imagefuncs/test_interactive.py` | 8 | 74% | to review |
| `imagefuncs/legend.py` | `imagefuncs/test_legend.py` | 19 | 100% | reviewed |
| `imagefuncs/plot.py` | `imagefuncs/test_plot.py` | 38 | 100% | reviewed |
| `imagefuncs/range.py` | `imagefuncs/test_range.py` | 32 | 100% | reviewed |
| `imagefuncs/scatter.py` | `imagefuncs/test_scatter.py` | 37 | 100% | reviewed |
| `imagefuncs/set_axis.py` | `imagefuncs/test_set_axis.py` | 31 | 100% | reviewed |
| `imagefuncs/streamplot.py` | `imagefuncs/test_streamplot.py` | 28 | 100% | reviewed |
| `imagefuncs/ticks.py` | `imagefuncs/test_ticks.py` | 9 | 100% | to review |
| `imagefuncs/volengine.py` | `imagefuncs/test_volengine.py` | 49 | 59% | to review |
| `imagefuncs/volume.py` | `imagefuncs/test_volume.py` | 5 | 91% | to review |
| `imagefuncs/zoom.py` | `imagefuncs/test_zoom.py` | 49 | 100% | reviewed |
| `imagekwargs.py` | `test_imagekwargs.py` | 109 | 100% | reviewed |
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
| `toolfuncs/findlines.py` | `toolfuncs/test_findlines.py` | 1 | 57% | out of scope |
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
   Stopped after `zoom` (2026-09-29), on purpose: `interactive` can become
   something much bigger and better, so it waits for a redesign rather
   than a review; `volume` and `volengine` are to be read together first
   and then decided on -- they are among the first parts planned in Rust.
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

Checks still to add, beyond the per-file work:

- **The managers together, not only alone.** Each file's tests build their
  own manager and call it directly, which is what makes them precise, but a
  user never does that: they call `I.plot(...)`, and one call runs through
  `assign_ax`, `create_axes`, `set_axis`, `RangeManager` and back, all
  sharing one state. Nothing covers the seams -- the order the managers run
  in, what each leaves on the state for the next, and what a second call
  finds there. Every bug of that shape found so far came from reading rather
  than from a test: `text` restarting the keyword tracking, `create_axes`
  resizing a figure the constructor had sized, `set_axis` forcing `ncol`,
  the y-limits measured from all the data. A second pass over `imagefuncs/`
  should add, per manager, a handful of tests that go through the facade and
  assert what the *other* managers see afterwards. Worth doing once the
  files themselves are reviewed, so the seams are the only thing left
  untested.

- **A page per public method.** `Docs/source/` holds one `.rst` per method,
  each an `automethod` pointing at the manager method and listed in a
  toctree (`fourier.rst` -> `toolsmethods.rst`). Nothing checks that a new
  method gets one, or that a page still points at a method that exists. A
  test over `DELEGATION` would cover both directions: every public method
  has a page, and every page names something real. Whether each page is
  *referenced* from a toctree is the second half, and is what decides
  whether it is reachable at all. Checked by hand while writing this:
  `showgrid` and `volume` have no page, the two methods this branch added --
  which is exactly what the guard is for.
- **Memory tests.** A load has to stay as small in memory as it can be: the
  variables are mapped, and a slice reads only what it covers. One test
  measures that today, the allocation of a slice of a loaded variable
  (`test_a_slice_of_a_loaded_variable_reads_only_the_slice`), added when a
  copy on first access was found reading whole files (see *Fixed bugs*). A
  test adding up the `nbytes` a state holds against the size of the data on
  disk would cover the rest, counting bytes rather than watching RSS so it
  is deterministic; worth extending to the particle path.
- **pyright at zero.** The project treats pyright as the source of truth,
  and it is at two errors today with nothing to notice. It belongs in CI
  next to the suite, not in a test.
- **pyright on the tests.** `[tool.pyright]` excludes `Tests/`, and naming
  a test file on the command line does not override it: `pyright
  Tests/x.py` reports "0 errors" having checked nothing. Found in the zoom
  review (2026-09-29), where it hid a real fault -- `zoom(width=...)` is
  rejected by pyright, and the tests calling it looked clean. Until the
  tests are in pyright's scope, check a test file from a copy outside the
  repository, where nothing excludes it. The "checked with pyright" of the
  test files reviewed before this date means ty only.
- **Annotations between facade and manager.** `test_signature_matches_the_manager`
  compares names, order, kinds and defaults, deliberately not annotations,
  and pyright does not catch a mismatch either. Worth finding a way to
  compare them that tolerates a type spelled differently.

At the end of phase 1, `Tests/test_all.py`: the guards that are about the
State/Kwargs/Mixin/Manager/Facade pattern rather than about one file, run once
per family from a table in `helper_all.py`. Seven exist today and only `Image`
has them all -- signature matches the manager, read keywords are declared,
parameters documented, documented keywords exist. Add there the manager
surface: a hand-written table of each manager's public methods, split into
the ones the facade exposes and the internal helpers, which is the one
direction the facade guards do not cover -- a manager growing a public method
nothing reaches.

Before the multiprocessing work: fix the copy/pickle bug of the facades.
After every phase: run `_test_examples.py`, a full coverage run, and update
the totals at the top.

## Fix order

Every bug is recorded and covered by a test, so none is lost; what this
decides is when each is fixed. The rule is how far the fix reaches, not how
severe the bug is or how hard it looks.

A bug that stays inside the file being reviewed is fixed during that review
(step 8 of the checklist). Everything below reaches further, so it waits --
not because it is difficult, but because most files still have no real tests:
a fix reaching into one of them cannot be verified, and a wrong one spreads
quietly instead of failing. `close`/`replace` is the cautionary tale: fixing
`close` on its own broke `replace`, because the two were halves of one
keyword and neither file said so.

The waiting is therefore bounded by the review, not by anyone's memory. Once
a family is covered, its batch can be fixed with the suite watching, which is
why these are grouped by theme rather than listed one by one.

**During the review** -- a bug contained in the file being read is fixed
there, so it never reaches this list. The first batch of them was cleared on
2026-09-18 and 2026-09-19: the undeclared keywords, the `BaseLoadMixin`
imports, the two nested `_check` calls, nine wrong docstrings, the
undocumented keywords, `repeat`, the constant-data padding, and everything
`figure.py` owned.

**Found after the review** -- a bug contained in one file but found after
that file was reviewed, or held back for a decision, is listed in *Open
bugs* with its `xfail`, like every other, and fixed from there.

**Next** -- each reaches into more than one file, so each waits until those
files are covered. Bounded work once they are: a batch per theme, fixed with
the suite watching. The first is the exception that cannot wait, since it
blocks the multiprocessing work.

| Fix | Where |
|---|---|
| Guard `__getattr__` against `state`, then decide what copying a facade means | `load.py`, `loadpart.py`, `image.py` |
| Make `repr`/`str` survive a load that read nothing | `load.py:284`, `loadpart.py:210` |
| `eq=False` on the state dataclasses | `baseloadstate.py`, `loadstate.py` |
| Scope the warning filter to pyPLUTO's own warnings | `utils/configure.py:260` |
| One `resolve_endianess()` for the four sites | `loadfuncs/offsetfluid.py`, `offsetpart.py`, `descriptor.py` |
| Honour `alone=False`; forward the `vars=` shim; build `codedict` lazily | `loadfuncs/findformat.py`, `initload.py`, `codeselection.py` |
| Keep `figsize` in step with the figure when `create_axes` resizes it | `imagefuncs/create_axes.py:185` |
| Track the last axis drawn on, as every docstring promises | `imagefuncs/imagetools.py:383`, every drawing manager |
| A default spacing for `fourier`; `d_vars` for a tab load | `toolfuncs/fourier.py`, `loadfuncs/readtab.py` |
| Point the unused-keyword warning at the user's frame | `utils/inspector.py` |

**Later** -- these change the shape of the code, and each wants its own
session with the examples re-checked afterwards.

| Fix | Why it waits |
|---|---|
| Empty `d_vars` once the load finishes | Touches every loadfuncs writer, `__str__` and the GUI variable list; settles the divergence on rebinding and the `__setattr__` question at once (the memory doubling went with the resolver's copy) |
| Move the figure-level keywords out of `CreateAxesKwargs` | Re-shapes the whole TypedDict hierarchy, which every method's annotation depends on |
| A kwargs table for `interactive` that matches what it forwards | Same hierarchy, and needs the union decided first |
| Close the memory maps | Only makes sense together with `d_vars` |
| Configuration readable before import | Needs the `set_text`/`Configure` design settled |
| Split `volengine.py` | 838 statements at 59%; the split is what makes the coverage reachable |
| Document the 259 declared keywords | Bulk work, one manager at a time as each is reviewed |

## Repo-wide bug scan

A scan run by a fresh model over the whole package, one batch per run. It is
independent of the file-by-file review: the review goes deep on one file, the
scan goes wide and finds what reading in order would reach only months later.
Everything it produces is verified again here before it is recorded.

**How to run it.** One batch per run, in any order, as many times as wanted:
the same batch run twice is not wasted, since step 2 of the prompt makes the
model skip what is already recorded. The budget rules are what keep a run from
burning tokens on a repo-wide read -- an earlier attempt without them spent
1.8M tokens to produce one report.

**The prompt.** Replace `<FILES>` with one batch from the table below.

```text
You are auditing one batch of files in the PyPLUTO repository for bugs.
Read-only: change nothing, fix nothing, write no files.

Environment
- Repo /home/gian/PyPLUTO, branch 3D. Run code as:
  cd /home/gian/PyPLUTO && python -W ignore -c "..."
- Test data under Tests/Test_load/: single_file, multiple_outputs,
  multiple_files, particles_cr, 1D, 2D, 3D.
- Entry points: pp.Load(path=..., text=False), pp.LoadPart(path=...,
  text=False), pp.Image(text=False). For the GUI, set MPLBACKEND=Agg and
  QT_QPA_PLATFORM=offscreen.

Batch: <FILES>

Rules
1. Read each file of the batch once, completely. Outside the batch, open at
   most five files, and only to check a caller or a callee.
2. Before reporting anything, check it is not already known: grep
   Tests/tests_recap.md for the file name and read the rows that match, and
   grep Tests/test_with_issues.py. Anything already there is out of scope.
3. Verify every candidate by running it. One attempt each; if it does not
   reproduce, report it under "unverified" and move on.
4. Stop at eight verified findings or forty tool calls, whichever comes
   first. A partial report is useful, an exhausted budget is not.
5. Do not run the test suite, do not run coverage, do not read Tests/ except
   for the two greps in rule 2.

What counts as a bug, most interesting first
- a wrong result, or one that silently differs from what was asked for
- a keyword accepted and then ignored, or overridden by something else
- an error of the wrong type, or a message naming the wrong function
- a docstring that disagrees with the code: a name, a default, a type, or
  behaviour it promises and does not have
- a declared type that contradicts what the code accepts at runtime
- state that goes stale: two places holding the same fact, one not updated
- a resource never released, or global state changed at import

Not bugs: style, naming, performance, refactoring ideas, missing features,
anything already recorded, anything you could not reproduce.

Output: one block per finding and nothing else.
FILE: path:line
WHAT: one sentence
REPRO: the exact code you ran
GOT: what it printed
WANT: one sentence
Keep the whole answer under 80 lines.
```

**Batches.** Grouped so each is roughly 800-1600 lines and internally
related, which is what lets the model check a caller without leaving its
batch.

| # | Files |
|---|---|
| 1 | `load.py`, `loadpart.py`, `loadstate.py`, `baseloadstate.py` |
| 2 | `loadmixin.py`, `baseloadmixin.py`, `imagemixin.py`, `imagestate.py` |
| 3 | `imagekwargs.py`, `loadkwargs.py`, `template.py`, `__init__.py` |
| 4 | `loadfuncs/`: `initload.py`, `findformat.py`, `findfiles.py`, `descriptor.py`, `codeselection.py` |
| 5 | `loadfuncs/`: `loadvars.py`, `offsetdata.py`, `offsetfluid.py`, `baseloadtools.py` |
| 6 | `loadfuncs/`: `readgridfile.py`, `readgridalone.py`, `readdefplini.py`, `readtab.py`, `read_files.py`, `write_files.py` |
| 7 | `loadfuncs/offsetpart.py`, `loadfuncs/storepart.py`, `codes/echo_load.py` |
| 8 | `image.py`, `imagefuncs/figure.py`, `imagefuncs/create_axes.py` |
| 9 | `imagefuncs/`: `plot.py`, `scatter.py`, `legend.py`, `display.py` |
| 10 | `imagefuncs/`: `contour.py`, `streamplot.py`, `gridplot.py`, `colorbar.py` |
| 11 | `imagefuncs/`: `set_axis.py`, `zoom.py`, `range.py` |
| 12 | `imagefuncs/`: `interactive.py`, `volume.py`, `imagetools.py` |
| 13 | `imagefuncs/volengine.py` |
| 14 | `toolfuncs/transform.py`, `toolfuncs/nabla.py` |
| 15 | `toolfuncs/`: `compute_units.py`, `set_units.py`, `loadtools.py`, `parttools.py`, `fourier.py`, `findlines.py` |
| 16 | `utils/`: `inspector.py`, `resolver.py`, `configure.py`, `pytools.py`, `examples_api.py`, `examples_cli.py` |
| 17 | `gui/`: `main_window.py`, `plot_controller.py`, `main.py` |
| 18 | `gui/`: `custom_var_engine.py`, `custom_var.py`, `load_controller.py`, `services.py`, `state_accessors.py`, `panels.py`, `app_state.py`, `globals.py` |
| 19 | `amr.py` |

**What to do with a report.** Reproduce each finding here before recording
it; the audits of 2026-09-18 had a handful that needed reframing, and one
that turned out to be deliberate. Then: a row in *Open bugs*, an `xfail` test
in `test_with_issues.py`, or -- if it is a design choice -- a row in
*Potential improvements* instead.

## Other

- `test_with_issues.py` — the executable half of *Open bugs*: one test per
  bug, each asserting the behaviour the code should have and marked
  `xfail(strict=True)`. Every run reports how many bugs are open, and a fix
  makes its test pass, which strict mode turns into a failure telling you to
  drop the marker and move the test into the file it belongs to. Nothing in
  it passes: 50 expected failures today, down from 64 as the *Now* list was
  worked through. Where a fault is partly cleared,
  the done part is guarded elsewhere -- `create_axes` documents every
  keyword it declares, so it is listed in `DOCUMENTED_KWARGS` and checked by
  `test_imagekwargs.py`, while its thirteen siblings stay here.
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
8. **Findings** — what decides whether a bug is fixed now is **how far it
   reaches**, not how hard it looks.

   A bug contained in the file being reviewed is fixed there and then,
   guarded by a test that fails without the fix, and recorded in *Fixed
   bugs*. The file is under the microscope anyway, its tests are being
   rewritten, and nothing else can be disturbed.

   A bug that reaches beyond it goes in *Open bugs* (confirmed, with the
   reproducer) **and gets a test in `test_with_issues.py`**, asserting the
   behaviour the code should have, marked `xfail(strict=True)`. It is fixed
   later, even when it sits in a file already marked reviewed: that file
   keeps its status. The reason to wait is that most files have no real
   tests yet, so a fix reaching into one cannot be verified, and a wrong
   one spreads instead of showing up. Once everything is covered, the same
   fix is safe and the suite says so.

   Design smells go in *Deferred structural improvements* or *Potential
   improvements*.

   Never write a test that asserts what a bug currently does. It passes, so
   no run ever mentions the bug, and it fails on whoever fixes it -- which
   invites them to restore the fault. The bug belongs in
   `test_with_issues.py` as an expected failure.

   When a bug is fixed, its test is **kept**: drop the `xfail` marker and
   move it into the test file of the source file it belongs to, where it
   stays as the regression test for that fix. Nothing written here is ever
   deleted, only relocated, and `test_with_issues.py` shrinks as the suite
   grows.
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
| `imagekwargs.py`, `utils/inspector.py` | **Keyword aliases**, e.g. `c` / `color` / `colour`, `cmap` / `colormap`. Idea of 2026-09-18, not yet designed. One table maps every alias to its canonical name, and `track_kwargs` rewrites the keys before the function body reads them, so managers keep reading one name and the scanner keeps counting one key. Three things to decide: whether the TypedDicts declare every alias (needed for the checkers to accept them, and it doubles the tables unless they are generated from the alias table), what happens when two aliases of the same keyword arrive together (warn and take one, or refuse), and how the docstrings list them, since a page per alias would be noise. The `colors` bug it was meant to settle is gone: `colors` was removed from `contour` (2026-09-25) and `streamplot` (2026-09-28) and warns as unknown, so an alias table would bring it back only by choice. |
| `utils/inspector.py` | The whole kwargs scanner is to be rewritten in Rust as the `kwarden` package (already on PyPI). `Tests/utils/test_inspector.py` is in effect its specification: which forms are recognised, the nested-call protocol, the `_check` handling. A Rust parser also pins its own grammar version instead of inheriting the host interpreter's `ast`, which removes the "node shapes change with the Python release" risk noted in `_get_str_from_slice`. |
| `__init__.py`, `utils/configure.py` | `Configure` runs at import with switches nobody can set beforehand (see the open bug). Either read them from environment variables (`PYPLUTO_GREET=0`), or make configuration a call the user can make after import that reconfigures the handlers, or both. Decide together with whatever `set_text` becomes. |
| `baseloadstate.py`, `utils/resolver.py`, `loadfuncs/*` | **`d_vars` should be emptied once the load finishes** (decided 2026-09-18). Since the resolver stopped copying (2026-10-03) the state's variable and `d_vars` hold the same mapped array, so the memory doubling is gone and an in-place write is seen by both; but the two still diverge on rebinding: `D.rho = D.rho * 2` never reaches `d_vars`, and `D.myvar = arr` never appears in it, so the GUI does not list it. Everything downstream reads only the *keys* (`load.py:322`, `gui/custom_var_engine.py:94`, `gui/services.py`, `gui/load_controller.py`), while `storepart.py`, `offsetfluid.py`, `readtab.py` and `codes/echo_load.py` write the values during the load. So: keep the names, drop the data once loading is done, and the memory doubling and the divergence both disappear. This also decides the `__setattr__`/`__delattr__` question below. |
| `gui/*`, `loadfuncs/readgridalone.py`, `readgridfile.py`, `toolfuncs/transform.py`, `imagefuncs/display.py`, `gridplot.py` | **One definition for the dimension constants** (noted 2026-09-29). Ruff refuses magic numbers in comparisons, so thirteen functions in ten files each define their own -- `twod = 2`, `twodim = 2`, `threed = 3`, three spellings -- a few lines before an `ndim ==` test. One small shared module (e.g. `ONED`, `TWOD`, `THREED`) would replace them all; where it lives is to be decided. |
| `imagefuncs/set_axis.py:307`, every drawing manager | **`axalpha`, the opacity of a whole panel** (decided 2026-09-29, replacing the `alpha` of `set_axis`, which fades nothing -- see *Open bugs*). It applies to everything on the axis -- background, spines, ticks and labels, title, grid, and every line, map, contour, streamline, scatter, grid, text and legend drawn on it -- and it holds for what is drawn later too: stored per axis in the state, applied by `set_axis` to what exists and by every drawing method to what it adds. An artist's own `alpha` wins over it (not multiplied). The colorbar is an axis of its own and keeps its opacity unless given one. Artists drawn with matplotlib directly set their own alpha there. `alpha` stays the opacity of each drawing, so `display(alpha=...)` no longer reaches the panel. A feature across every manager, done after the contained image bugs. |
| every manager, `utils/inspector.py` | **Explicit keywords for the internal methods (`extra_kwargs`)** (noted 2026-09-29). Methods that are not image methods -- `place_inset_loc`, `zoomcopy`, `copyartist`, the helpers a manager calls on itself -- take the whole `**kwargs` of the public call, so what they read is invisible to the table of that call: `place_inset_loc` read `width`/`height`, which `ZoomKwargs` never declared, and the undeclared-keyword guard could not see it, since it scans only the public method. An internal method should receive the keywords it uses, named, and not `**kwargs`. |
| `imagefuncs/gridplot.py`, `load.py` | **`showgrid` by direction (option B), as the default** (decided 2026-09-29). Since the gridplot review `showgrid` takes coordinates only -- 1D drawn straight, a curved grid as its 2D projection (`x1rc`/`x2rc`, `x1rp`/`x2rp`, `x1rt`/`x2rt`) -- and converts nothing. The plan is to make the default a call by direction -- `showgrid(data=D, plane=("x1", "x3"))` -- which picks the right projection from `Load` for every geometry, plane and code, with the coordinates kept as the backup for anything else. A thin layer: it chooses the arrays and passes them in, so every combination the projections cover works through the path that is tested today. It waits for the cylindrical item below. |
| `load.py`, `loadfuncs/readgridfile.py:220`, `imagefuncs/gridplot.py` | **gPLUTO's `CYLINDRICAL` is (r, phi, z)** (noted 2026-09-29). gPLUTO has no `POLAR`: its `CYLINDRICAL` is what classic PLUTO calls `POLAR`, while classic PLUTO's `CYLINDRICAL` is the axisymmetric (R, z). `readgridfile.py:220` projects `CYLINDRICAL` as polar, which is right for gPLUTO and wrong for PLUTO; the meaning should follow `state.code`, keeping classic PLUTO outputs readable. Every plane of both geometries should get its projection -- (r, phi), (r, z), (phi, z) for cylindrical, the same for spherical -- and option B above builds on them. |
| `imagefuncs/set_axis.py`, every drawing manager | **Fewer tight layouts, and a faster `set_axis`** (noted 2026-09-29, for pyPLUTO 2). Profiling `showgrid` showed the layout is most of the cost of a plot: `set_axis` makes one at its end, and most managers make another after it, often redundant -- the grid dropped its own and loses nothing (same axis box). `set_axis` itself is the largest fixed overhead of every call. Worth an audit of every `tight_layout()` call, and a lighter `set_axis`; pyPLUTO 2, with parts in Rust, is to aim for speed throughout. |
| `load.py` (`__setattr__`) | An unknown name is created silently, so a typo'd assignment fails nowhere. Cannot simply be forbidden: users deliberately attach composite variables (`data.my_composite = rho * T`) and pass the load into their own functions. Needs a design that blesses that case explicitly while still catching typos — to be discussed. |

## Open bugs

| Where | What |
|---|---|
| `load.py`, `loadpart.py`, `image.py` (`__getattr__`, `__setattr__`) | **The facades cannot be copied or unpickled, so they cannot be sent to a `multiprocessing` worker.** `__getattr__` reads `self.state`; on an instance that has no state yet, that read calls `__getattr__("state")` again, forever. `copy` and `pickle` both build the new instance without running `__init__` and then look up `__setstate__`, which takes exactly that path. Confirmed: `copy.copy` and `copy.deepcopy` raise `RecursionError` on `Load`, `LoadPart` and `Image`; `pickle.dumps` of `Load` and `Image` succeeds but `pickle.loads` raises `RecursionError`; any attribute read or write on `Image.__new__(Image)` does the same. `LoadPart` also fails `deepcopy`/`pickle` for a second reason, `cannot pickle 'mmap.mmap' object` (see the `mmaps` bug below). Nothing tests copy or pickle. The `not hasattr(self, "state")` clause in `__setattr__` belongs to the same bug: its docstring says it "makes the first line of `__init__` possible", but `name == "state"` already handles that line, and if the clause ever ran it would recurse too. Same wrong docstring in all three; `loadpart.py:262` also still says "the Load class". `template.py` has no attribute hooks, so it neither shows the pattern nor the fix. Fix: `if name == "state": raise AttributeError(name)` at the top of each `__getattr__`, then decide what copying a facade means (share or duplicate the state, reopen or drop the mmaps) before multiprocessing work starts. |
| `loadfuncs/offsetfluid.py:256`, `loadfuncs/offsetpart.py:156` | **Passing the correct `endian` explicitly corrupts the data.** For a standalone vtk load, `offset_vtk` uses `">" if state.endian is None else d_info["endianess"][exout]` — so when the user *does* pass `endian`, it keeps whatever is in that array, which `findfiles.py:94` allocated with `np.empty(dtype="U20")`, i.e. `""`. `binformat` becomes `f4` (native) instead of `>f4`. Confirmed: `Load(path="Tests/Test_load/single_file/vtk", datatype="vtk", alone=True, endian="big")` gives `rho.flat[0] = -1.49e+19`; without `endian=` the same call gives `0.138`. The `if ... is None: raise ValueError("Wrong endianess")` guards at `offsetfluid.py:261`, `offsetpart.py:80,161` are unreachable — `np.empty("U20")` yields `""`, never `None`. The rule is written four times and the copies disagree (`descriptor.py:85`, `offsetpart.py:77` propagate `state.endian` correctly). Fix: one `resolve_endianess()` helper, called from all four sites. |
| `loadfuncs/findformat.py:125` | **`alone=False` is silently ignored.** `check_format` builds `funcf` (lines 125–135) to gate which probes run given `alone`, then the loop at 138 hard-codes both probes and never reads `funcf`. `alone=True` happens to work via `type_out = []` at line 121, but `alone=False` does not: `check_typelon` still runs, finds the standalone files and sets `state.alone = True`. Confirmed on a folder holding only `data.0000.vtk`: `Load(..., alone=False).state.alone` is `True`. The user gets a standalone load with `timelist` full of NaN instead of the `FileNotFoundError` at line 157. |
| `loadfuncs/initload.py:121` | **The deprecated `vars=` keyword is warned about, then discarded.** The shim warns but never assigns to `var`, which stays `True`. Confirmed: `Load(path=..., vars="rho")` warns, then loads `['prs','rho','vx1','vx2','vx3']`. It is also in the wrong layer — `var` was already bound as a positional parameter before the manager ran. The sibling `nfile_lp` shim (`loadpart.py:168`) sits in the facade and does forward its value. |
| `loadfuncs/codeselection.py:69` | **Any non-default `code` on `LoadPart` raises `AttributeError`.** `self.echomanager` is only created `if isinstance(state, LoadState)` (line 42), but the `codedict` literal at line 69 references `self.echomanager.load_echo` eagerly, before the membership test. So it is evaluated on every call. Confirmed: `LoadPart(..., code="echo")` and even `LoadPart(..., code="nosuchcode")` both raise `AttributeError: 'CodeManager' object has no attribute 'echomanager'` — the intended `NotImplementedError` is unreachable for `LoadPart` entirely. |
| `imagefuncs/set_axis.py:307` | **`alpha` fades nothing.** It calls `ax.set_alpha()`, which stores the value on the Axes artist; the background patch and the lines keep their own alpha, so the figure is unchanged. Whatever the keyword is meant to fade has to be told. |
| `imagekwargs.py:139` | `xtickslabels`/`ytickslabels` accept a single string -- `TicksManager.find_labels` has a branch for it, and it labels the first tick -- while `SetAxisKwargs` declares `list[str] \| bool \| None`, so the call works and every checker refuses it. Same family as the `grid="both"` and `sharexaxes` index gaps. |
| `Tests/test_imagekwargs.py:141` | **The conflicting-types guard cannot see the same type declared by two tables.** On Python 3.14 the annotations are `ForwardRef` objects, and two of them are equal only when they come from the same class: `float` declared in `SetLocKwargs` and in `CreateAxesKwargs` is reported as "two types". It holds today because no key is declared twice with the same type; comparing `__forward_arg__`, or the resolved hints of each table, would make it reliable. Found when `ZoomKwargs` briefly inherited `SetLocKwargs`. |
| `imagefuncs/imagetools.py:383` | **"The last considered axis" is not tracked.** Every drawing method and `colorbar` promise that without `ax` the last considered axis is used, while `assign_ax(None)` takes matplotlib's current axis -- the last one *created* -- when it is an image axis, and the last image axis otherwise. So `display(ax=1)`, `display(ax=0)`, `colorbar()` puts the bar beside the second panel, describing its map. It needs a state field every manager updates. |
| `utils/inspector.py:33` | **The scan cache is written into.** `_find_kwargs_keys_from_source` is `@functools.cache`d and returns a mutable set; `track_kwargs` then does `used_keys \|= extra_keys`, mutating the cached object, so scanning an untouched source reports keys that do not appear in it -- `create_axes` scans as reading `left`, `right`, `top`... which are nowhere in its body. Any caller of `find_kwargs_keys` receives a set others can mutate, and two functions with identical source text share one entry. A non-mutating union fixes it, and returning a `frozenset` stops it recurring. Found while asking whether `extra_keys` are checked like other keywords: at runtime they are, but our guards only see them because of this. |
| `utils/configure.py:260` | **Importing pyPLUTO resets the user's warning filters.** `Configure` calls `warnings.simplefilter("always")`, which clears the whole filter list, so `python -W ignore` and any `filterwarnings("ignore")` made beforehand stop working for the rest of the process. Confirmed in a subprocess. A filter scoped to `module="pyPLUTO"` would do the same job without touching anyone else's. |
| `load.py:284`, `loadpart.py:210` | **`repr()` crashes on a load that read nothing.** `Load(nout=None)` is documented as "do not load", and `repr(D)` then raises `AttributeError: no attribute 'nout'`; `str(D)` raises on `geom`. A repr is what a debugger and the prompt call by themselves, so it must never raise. |
| `baseloadstate.py:24`, `loadstate.py:17` | **Two states cannot be compared.** The generated `__eq__` reads the load-only fields: `LoadState() == LoadState()` raises `AttributeError`, and two real states raise `ValueError` on the array comparison. `eq=False` would at least give identity. |
| `imagestate.py`, `imagefuncs/create_axes.py:185` | **`figsize` reports a size the figure does not have.** `create_axes` resizes the figure without updating the state, so after `create_axes(ncol=2)` the property and the repr still say `[8.0, 5.0]` while the figure is `[8.49, 5.0]`. |
| `imagekwargs.py:61` | **Figure-only keywords type-check on every drawing method and are then unused.** `CreateAxesKwargs` inherits `ImageKwargs`, so `plot(withblack=True)`, `style`, `nwin`, `numcolors` and six more are accepted by the checkers and reported as unused at runtime -- the mirror of a keyword read but not declared. |
| `imagekwargs.py:144` | `SetAxisKwargs.grid` declares `Literal["x","y"] \| bool`, while `set_axis.py:326` also handles `"both"`: the value works and the checkers reject it. |
| `image.py:402`, `imagefuncs/interactive.py:65` | `interactive` is typed with `DisplayKwargs`, but its 1-D branch forwards to `PlotManager.plot`, so `ls`, `lw`, `label` and the other line keywords work at runtime and are statically rejected. |
| `load.py:88` | The class documents a keyword `full3d` with default True; the keyword is `full3D` and defaults to False, so the documented spelling warns as unused and sets nothing. |
| `load.py:532`, advertised at `load.py:337` | `repeat` is listed in `__str__` among the public methods and carries a docstring, but raises `NotImplementedError: Function repeat not implemented yet`. |
| `load.py:79`, `loadfuncs/readdefplini.py:38` | `defh="mydefs.h"` is ignored: the reader always looks for `definitions.h` in the folder, so a named file is never read and a missing one says nothing. |
| `toolfuncs/transform.py:403`, `amr.py:507` | Two more `_check` protocol violations, the same fault fixed in `imagetools.text`: `reshape_cartesian(var, transpose=True)` warns that `transpose` is unused, blaming `reshape_uniform`. |
| `imagefuncs/imagetools.py:191` | `text` documents `xycoords='figure fraction'`, while the lookup knows `fraction`, `points` and `figure`, so the documented spelling raises a bare `KeyError`. |
| `loadpart.py`, `loadkwargs.py:46` | **`LoadPart` accepts `multiple`, which it cannot use.** Particle output is split by chunk, not by variable, so the keyword means nothing here; it is declared in `LoadPartKwargs`, accepted, and silently ignored -- not even reported as unused, so nothing tells the user the request had no effect. It should be refused, or dropped from the table. |
| `loadfuncs/loadvars.py:103` | `chnk` is silently ignored for non-chunked particle output: `chnk=99` loads normally instead of warning. The docstring now says chunks exist only for multi-file output, but a request that cannot be honoured should still say so. |
| `toolfuncs/fourier.py:98` | `fourier(f)` without `dx` raises `KeyError`. |
| `loadfuncs/readtab.py` | `datatype="tab"` leaves `d_vars` empty, so the GUI lists no variables. |
| `imagekwargs.py` | 259 declared kwargs are undocumented in the method docstrings. 15 per method are the figure-level ones inherited from `ImageKwargs`, documented on `Image.__init__` instead; after those, what is left is `sharexaxes`/`shareyaxes` in every method but `create_axes` (which documents them), `showgrid` (49 of 68), `volume` (51 of 87) and `scatter` (`transpose`, `x1`, `x2`). `test_every_parameter_is_documented` covers the parameters, which are all documented today; the keywords need a guard of the same shape once these are written. |
| `imagefuncs/range.py:132,156` | **The y-limits are computed from all the data, not from the visible window.** Both computing cases filter with `np.where(np.logical_and(x >= x.min(), x <= x.max()))`, which is true for every point, so the mask selects the whole array (confirmed: 11 of 11). The comment says "find the limits of the x-axis", so the intent was the current x-limits: a point far outside the window still sets the y-range. Fixing it changes the limits of existing plots, so it needs the example figures rechecked. `test_set_yrange_measures_all_the_data` documents today's behaviour. |
| `imagefuncs/interactive.py:170` | **The `lint` keyword is documented but does not exist**: "If True, enables linear interpolation between frames in the interactive plot", read nowhere and declared nowhere, so `I.interactive(var, lint=True)` warns "Unused kwargs" -- the documentation produces the warning. Either implement it or drop the entry; listed in `GHOST_KWARGS` in `helper_image.py` meanwhile, and checked by `test_documented_keywords_exist`. |
| `imagefuncs/set_axis.py:614` | **`sharex=True` raises `TypeError`.** `share_axes` passes the value straight to `ax.sharex()`, which takes an axis, while the docstring documents `bool | str | Matplotlib axis`. Confirmed: `I.plot(x, y, ncol=2, sharex=True)` raises `'other' must be an instance of ... not a bool`. The working keyword is `sharexaxes`, read by `create_axes`. |
| `imagefuncs/imagetools.py:369` | **`assign_ax` silently overrides `ncol` and `nrow`.** Both are forced to 1 before `create_axes` is called, and they count as consumed, so nothing warns. Confirmed: `I.plot(x, y, ncol=2)` on an empty figure gives one axis. `set_axis.py:253` sets the same two keys immediately before calling. |
| `imagefuncs/imagetools.py:390` | **An out-of-range axis index raises `IndexError`**, not the `ValueError` the docstring implies; an empty list does the same at `ax[0]`. Confirmed for `assign_ax(5)`. `test_assign_ax_index_out_of_range` documents today's behaviour and will fail when it changes. |
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
| `imagefuncs/display.py:355` | `map_extent` -- the edges of a map from its cell centers -- probably belongs in `RangeManager`, which is where limits live. It has one caller today, so it sits in `DisplayManager`, and the move should happen when a second caller appears and the signature is settled by use. Neither `contour` nor `streamplot` turned out to be one: both draw on the points themselves, and the axis already ends on the outermost of them. |
| `imagefuncs/zoom.py:462` | The arrows of streamlines are not copied into an inset. matplotlib draws them as separate `FancyArrowPatch`es, whose geometry has no public getter, so `copyartist` leaves them out, as it does texts and legends: a zoom of streamlines shows the lines without their heads. Copying them means rebuilding each arrow from its path, or asking matplotlib for a public accessor. |
| `imagefuncs/streamplot.py:379` | A stretched or non-Cartesian grid cannot be drawn: matplotlib's streamplot wants evenly spaced `x1`/`x2`, and raises `'x' values must be equally spaced` otherwise. The docstring points to `Data.reshape_cartesian`, which the torus example already calls first. Regridding on the fly -- onto a uniform grid of the same extent and resolution -- would make it work on any PLUTO output, at the cost of one interpolation per call. |
| `imagefuncs/plot.py:347` | A legend built by hand is thrown away by the next line. `legpos` is kept on the axis, so `I.legend(label=["custom"])` followed by any `I.plot` on that axis is rebuilt from the drawn lines and the custom entries are gone. The stickiness is what makes a legend follow the curves as they are added, so this is a choice to make, not a slip: either a hand-built legend clears `legpos`, or it is kept as a second artist. |
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
| `gui/plot_controller.py:281` | The GUI offers matplotlib colormaps only, by design: it applies them with `artist.set_cmap` rather than through `find_cmap`. An "external cmap" option would let a GUI user reach the colormap packages as well, and would then route through `find_cmap` for the lookup and the warning. |
| `imagefuncs/imagetools.py` | cmasher and cmocean are left out of `CMAP_PROVIDERS` because importing them raises matplotlib deprecation warnings (114 and 88, from passing `N` to `ListedColormap`, removed in matplotlib 3.13). Both register their colormaps with matplotlib, so the procedure today is `import cmasher as cmr` in the script and then `cmap="cmr.rainforest"`, which resolves with no import from us. Put them back in `CMAP_PROVIDERS` and in the `cmaps` extra once upstream stops passing `N`; an issue on each is worth opening. |
| `imagefuncs/imagetools.py`, `interactive.py`, `utils/pytools.py` | The `script_relative` path logic (`Path(name)`, `is_absolute`, `inspect.stack()[n].filename`) is written three times, each with its own frame index, so each works only at one call depth. One helper would do. |
| `imagefuncs/imagetools.py:40` | Every `ImageToolsManager` builds a `CreateAxesManager`, and thirteen managers build an `ImageToolsManager`, so one `Image` holds fourteen of them. Harmless, since they share the state, but pure duplication. |
| `_test_examples.py` | Fourteen subprocesses run one after another (73 s). Each is fully isolated in its own `tmp_path`, so `pytest-xdist` would run them in parallel with no change to the file. |
| `pyproject.toml` | `Tests/` is excluded from pyright (170 errors today). Add files to its scope one by one as they are reviewed, the way ty already covers them, so a reviewed test file stays clean under both checkers. |
| process | Mutation testing found two holes in `resolver.py` at 100% coverage that no line-coverage tool could see. A periodic `mutmut` run over the reviewed files, or the ad-hoc mutate-and-revert loop used here, is worth institutionalising. |

## Fixed bugs

| Where | What |
|---|---|
| `imagefuncs/ticks.py` (new), `imagefuncs/set_axis.py` | **Labels on automatic ticks warned twice, and moved with the data.** Given labels with no ticks, `set_ticks` warned that labels should be fixed only with the ticks, applied them anyway, and matplotlib warned in turn about a `FixedFormatter` without a `FixedLocator`. Simply fixing the ticks at that moment was not enough: `plot`, `display` and the others call `set_axis` *before* their ranges, so `plot(x, y, xtickslabels=...)` would have pinned the ticks of the empty 0-1 axis. The ticks now have their own manager, `TicksManager` in `ticks.py`, built like `RangeManager`: each axis carries a case in `setxticks`/`setyticks` -- 0 automatic, 1 fixed by the user (a list, or `None`), 2 present and free to change, 3 being fixed now -- and labels on automatic ticks are case 2. Their ticks are pinned to the automatic ones of the current limits, and every drawing method calls `update_ticks` once its ranges are set (`contour` and `streamplot` once drawn, since matplotlib picks their limits), which pins them again for the new limits. `xtickspin`/`ytickspin` keep the labels with the locator and formatter the pin replaced, to find the ticks of new limits on any scale and to give the axis back when the labels are removed (to case 0) or the ticks are fixed (to case 1). Labels given alone on ticks the user already fixed now go on those ticks, where they used to be taken for labels on automatic ticks. No warning in any of these. `set_ticks` and `set_tickslabels` moved out of `AxisManager` with it, which closes the *Potential improvements* note that they had outgrown it: `ColorbarManager` builds a `TicksManager` instead of an `AxisManager` (decided 2026-10-08). `test_labels_on_automatic_ticks_warn`, which pinned the first warning, was replaced by the case tests in `Tests/imagefuncs/test_ticks.py`. |
| `imagefuncs/plot.py:383` | **A legend asked for without a label was empty, and matplotlib warned in our place.** `legpos` built the legend whatever was on the axis, so a plot with no `label` got an empty frame plus matplotlib's *"No artists with labels found to put in legend"*, phrased for someone calling matplotlib. Now no legend is drawn while no line on the axis has a label (`get_legend_handles_labels`, matplotlib's own selection), and we warn instead: *"legpos is set but no line has a label: no legend is drawn."* The position is still remembered, so the first labelled line brings the legend (decided 2026-10-08). Guarded by `test_a_legend_without_any_label_is_not_drawn` and `test_a_label_after_legpos_brings_the_legend`. |
| `imagefuncs/plot.py:352` | **A 2D plot could not have a colour per line.** `PlotKwargs.c` declares a sequence of colours, so `c=["r","b","g"]` type-checked, but the whole array went to a single `ax.plot`, which takes one colour and raised. A `c` that is not a single colour (`is_color_like`, matplotlib's own test) is now read as one per line, whatever holds it -- a list, a tuple, a string of one-letter colours like `"rgb"`, an array of RGB rows -- and set on the lines once they are drawn. A count that does not match the lines warns and is cycled through, as the legend does with its lists (decided 2026-10-08). Guarded by `test_one_colour_per_line_of_a_2d_plot` and `test_too_few_colours_are_cycled_with_a_warning`. |
| `toolfuncs/findlines.py:221` | **Field lines were drawn outside the domain.** The event that stops the integration was a flag -- 1 inside, 0 outside -- while `solve_ivp` finds an event by looking for a *zero* of the function, so the crossing was only noticed once a step had already landed beyond the wall and the line was drawn to wherever that step ended: ±1.00091 for a domain of ±1.0 in the KH example. It is a signed distance to the nearest border now, with `direction = -1`, so the line ends exactly on it, and the 1% margin that used to put the last point outside (`0.51` of a cell) is gone. Guarded by the new `Tests/toolfuncs/test_findlines.py`, the only test of a file that is otherwise out of scope. |
| `utils/resolver.py`, `loadfuncs/loadvars.py:95`, `:159` | **The first access to a variable read the whole file** (reported by a user on a 2048^3 run, 2026-10-03; in every release since 1.2.0). The resolver copied every mapped variable into memory on its first access, so a slice of one plane read and copied the entire variable: for the reporter, `D.prs[512:1024, 1024, 0:512]` took 1 min 48 s against 194 ms in 1.1.5, and needed some 64 GiB of RAM. The copy is gone -- a mapped variable is handed out as it is -- and the files are mapped copy-on-write (`ACCESS_COPY`) instead of read-only, so writing to a variable still works, in memory, never touching the file. On a synthetic 1024^3 output the same slice went from 15.9 s and 12.9 GiB to 0.09 s and 0.15 GiB. Joining a chunked particle output is unchanged. Guarded by `test_a_slice_of_a_loaded_variable_reads_only_the_slice`, which measures the allocation of a slice. |
| `imagefuncs/range.py:283` | **A log range lost its widest value when negative, and started at 0 when zero.** The fold to absolute values reassigned `ymin` first and computed `ymax` from it, so `range_offset(-100, 10, "log")` gave `(5, 21)` instead of a range reaching 100; both are folded together now, `(5, 111)`. And a range starting at 0 kept 0 as its lower limit, which a log axis cannot show and matplotlib ignores: with no positive value to start from, the range now starts a decade below its top -- `(0, 5)` gives `(0.25, 5.5)` -- or at 0.1 when every value is 0. The stale *Open bugs* row for the constant-data padding (`range.py:213`, fixed earlier) was removed with it. |
| `imagefuncs/set_axis.py:291` | **The ticks on the far sides were set with the string `"off"`.** `tick_params(right="off", top="off")` was written to remove them, but matplotlib stores the string and reads it as true, so every plot had ticks on all four sides by accident. That four-sided look is the one kept (decided 2026-09-29), now with a real `True`, so it no longer depends on how matplotlib reads a string; no figure changes. |
| `imagefuncs/legend.py:237`, `:243` | **A legend built from custom labels ignored `mscale` and was black.** `markerscale` was passed only in the branch that legends the lines drawn, so `legend(label=["a"], marker="o", ms=5.0, mscale=5.0)` left the handle at 5 instead of 25; and `kwargs.get("c", ["k"])` defaulted every hand-built handle to black, while the docstring promised the image's palette. The marker scale is read before the two branches now, and the handles take the palette in order, as the lines do. |
| `imagefuncs/legend.py:229` | **Every legend was attached twice.** `ax.legend(...)` already attaches the legend it builds, and an `add_artist` after it attached the same object again, so each legend was listed twice among the axis's children and drawn twice; two legends made three entries. The `add_artist` was there for two legends on one axis, where a second `ax.legend()` replaces the first -- which needs the *previous* legend pinned before the new one is built, and that is what happens now; a legend asked for by `plot` still replaces the current one. Each axis keeps its own, so legends on different subplots do not interfere. The test helper `_legends` counts every entry now, not distinct objects, so a duplicate fails the legend tests themselves. |
| `imagefuncs/create_axes.py:163`, `:193` | **A fontsize and a size given to `create_axes` were half applied.** The fontsize went into matplotlib's `rcParams` only, so `image.fontsize` kept reporting 17 while the figure was drawn at 13, and the legend, the text box and the labels, which read the state, used the stale one. The size set `state.figsize` without `set_size`, the flag marking a size as chosen, so the next `create_axes()` recomputed it and the figure went back to 6x5. Both reach the state now. |
| `imagefuncs/create_axes.py:170`, `:260` | **A custom layout silently overruled an explicit `tight`.** Any border keyword wrote `kwargs["tight"] = False` before the keyword was read, so `create_axes(ncol=2, left=0.2, tight=True)` came out not tight without a word. The two cannot both hold -- a tight layout moves the axes the borders placed -- so the layout still wins (decided 2026-09-29), and a tight asked for with it now warns. The check lives in `set_custom_axes` (the old `_set_custom_axes`, renamed), which keeps `create_axes` under ruff's branch count. The xfail asserting that tight should win was replaced by a test of the decision. |
| `imagefuncs/create_axes.py:229`, `:449`, `imagekwargs.py:72` | **Sharing: `False` raised, an index worked only across calls and was declared nowhere, and a string never worked.** `False` is an `int`, so `sharexaxes=False` -- the documented default -- was read as the index 0 and raised `IndexError`; an axis was shared at creation, so an index pointing at an axis of the same call did not exist yet; `CreateAxesKwargs` declared `bool \| str \| Axes`, refusing the index form that worked, and every string reached matplotlib, which refused it. The axes now share once they all exist, through `find_share_target` (the old `_check_shareaxis`, renamed): True or 'all' with the first axis of the call, 'row' and 'col' within each row or column as in `subplots`, an index with any axis of the image, an Axes with itself, False and None with nothing, any other string with a clear `ValueError`. The type is `bool \| int \| Literal["all", "row", "col"] \| Axes \| None`, and the commented-out copy of the old logic is gone. |
| `imagefuncs/set_axis.py:427` | **Fixed ticks on a log scale lost their labels.** The formatter of a log scale labels powers of ten only, so `yticks=[0.5, 1]` drew 0.5 with an empty label, and `cticks` did the same on a log colorbar. Fixed ticks with automatic labels on a log scale get a `LogFormatterSciNotation` told to label every tick (`labelOnlyBase=False`, no thresholds): 0.5 and 3 read `5×10⁻¹` and `3×10⁰`, in the notation of the decades, which keep their usual labels. |
| `imagefuncs/set_axis.py:393` | **Removing the ticks of a log scale kept its minor ones.** `set_ticks` with `None` emptied the major ticks only, while a log scale places its own minor ticks at every multiple of each decade, with no major to follow: `plot(..., yscale="log", yticks=None)` still showed 40 of them, and `cticks=None` a log colorbar's. The minor locator is switched off with the major ticks now; a linear axis is unchanged, its minor ticks having nothing to sit between. The same review split `set_ticks` in two, the labels going to `set_tickslabels`, which clears ruff's branch count. |
| `imagefuncs/zoom.py:359` | **A zoom copied only a map or plain curves, and lost what was drawn over the map.** The inset was rebuilt by re-running `display` from the first collection -- reshaping its array, reading `vlims`, guessing the scale from `str(norm)` -- or `plot` per line, so a scatter, contour lines, streamlines or a grid raised `The zoom can be applied only to a QuadMesh object`, and field lines or contours over a map were silently dropped. Every line and collection is now copied in drawing order (`zoomcopy`, `copyartist`): the geometry rebuilt per kind, the style taken over by `update_from`, and only the parent's data transform and clipping pointed at the inset -- a scatter keeps its markers in points. A copied mesh keeps the antialiasing and rasterizing of the original, which a bare `QuadMesh` does not, and the inset hides its axis index. The map keywords without `var` restyle the copy; `var` replaces the map on its grid (`zoomdisplay`), a gouraud map's border included, with the overlays copied on top. Every example figure still matches its reference. |
| `imagefuncs/zoom.py:679` | **The inset ended where it was not asked to.** With `top` and `height` both given, `height` won and `top` was ignored, while the warning said "Using top and height" and the docstring gave `top` priority; a `top` given alone kept the default bottom, so `top=0.5` made a negative height that matplotlib refused; `bottom=0.0` counted as not given. The end now wins in every case -- alone it moves the start, with a start it sets the size, with a size the start is taken back from the two -- and presence is tested with `is not None`. The same for `right`/`width`. |
| `imagefuncs/zoom.py:316` | **A zoom switched off the tight layout of the whole figure, for good.** It is needed only for an inset with its own colorbar, whose axis `tight_layout` cannot handle; now it happens only then, and every other zoom keeps the layout of the figure. |
| `imagekwargs.py:280`, `imagefuncs/zoom.py:583` | **`width` and `height` were documented and undeclared, `label` declared nowhere.** `ZoomKwargs` lacked the two keywords `place_inset_loc` reads, so pyright rejected `zoom(width=0.4)`; `label` was documented and warned as unused. `x1`/`x2` given alone with `var` failed on the other being completed from the map's grid; they go together now, with a clear error otherwise. `zoom` is in `DOCUMENTED_KWARGS`. |
| `imagefuncs/gridplot.py:313` | **The grid froze the axis, and cut off what was drawn before it.** It faked `kwargs["xrange"]`, which `plot` recorded as fixed by the user (`setax = 1`): a line drawn after the grid was cut off at its extent, and so was one drawn before, since the grid shrank the frame to itself. The frame goes through `RangeManager` case 4 now, like `scatter` and `display`: the grid's extent exactly, and free to grow; a given `xrange`/`yrange` still fixes it. |
| `imagefuncs/gridplot.py:99` | **Thinning shortened the other family and dropped the border.** `x1[::everyx]` thinned the points before the lines were built, so with `everyy=2` the lines at constant x1 stopped short of the top of the domain, and the last face, the border, was dropped whenever the count did not fall on it. Thinning picks whole lines now (`_every`), keeps the first and the last, and every line crosses the domain. |
| `imagefuncs/gridplot.py:327` | **A label made one legend entry per line, and a large grid was slow.** Each family went through `plot`, one `Line2D` per line, all carrying the label; building 2050 artists and four tight layouts made a 1025 x 1025 grid take 620 ms (call and draw). Each family is one `LineCollection` now, with the label on the first -- one entry -- and a straight line is drawn from its two ends, which covers every line of a 1D grid and the rays of a curved mesh (`_straighten`; a closed circle, with no chord, is kept whole). 1025 x 1025 takes 96 ms, `Disk_Planet` 77 ms instead of 348, its polar mesh 131 instead of 354. `showgrid` returns the two collections. |
| `imagefuncs/gridplot.py:291` | **`geom` converted the grid, and not always rightly.** `_to_cartesian` turned `x1`/`x2` into circles and rays for `POLAR`, `CYLINDRICAL` and `SPHERICAL`, took the geometry from `data.geom`, and so could not draw the raw (r, theta) grid of a loaded run; it also drew `CYLINDRICAL` as polar, which is wrong for classic PLUTO (see *Deferred structural improvements*). Both are gone: coordinates are drawn as given, a curved grid is passed as its 2D projection, and its lines then sit exactly on the cells of a map drawn on the same mesh. `geom` now warns as unknown. |
| `imagefuncs/colorbar.py:220` | **`colorbar()` only worked on a map drawn first.** Without `pcm` it took the first collection of the axis and raised `First collection is not a QuadMesh` for anything else: after `contour`, after `streamplot(cmap=...)`, even after lines with a map drawn over them; an empty axis gave a bare `IndexError`. It now takes the last collection colored by data -- `get_array()` set -- skipping contour lines drawn in one color, which keep their levels and would otherwise take the bar from the map under them; with nothing to describe, a `ValueError` says so. |
| `imagefuncs/colorbar.py:321` | **A second `colorbar()` crashed.** `_find_ax` took `fig.gca()`, which after the first colorbar is that colorbar's axis, and looked it up among the image axes: `list.index(x): x not in list`. It passes `None` to `assign_ax`, which falls back to the last image axis. The two figure checks inside `_find_ax` could never fail and are gone. |
| `imagefuncs/colorbar.py:236` | **Contour lines got a colorbar of blocks.** matplotlib builds a contour colorbar with one block per level band, 7 colors for 6 levels; it is now built from a `ScalarMappable` with the same norm and colormap, 256 steps like every other colorbar, on the same limits. |
| `imagefuncs/colorbar.py:273` | **`ctickslabels` crashed on an array of `cticks`, and a bar without ticks needed `[]`.** The labels went through `cticks or ...`, which an array refuses, and `cticks=None` meant automatic. Ticks and labels now go through `AxisManager.set_ticks`, the code behind `xticks`/`xtickslabels`, with the same rules: True automatic, None removed, a list fixed. |
| `imagefuncs/colorbar.py:279` | **`colorbar` returned `None`.** It returns the `Colorbar` now, in the manager and in the facade, as every drawing method returns what it drew. The docstring was rewritten: what the bar describes and where it goes, `cpad` in inches, `extendrect` rectangular rather than triangular, all four types of `pcm`, and `sharexaxes`/`shareyaxes`, which were documented as `sharex`/`sharey` -- keywords `colorbar` does not accept, so the documented call warned as unused. The `isinstance(cax, Axes)` check, only there for the type checker, is a typed local now. |
| `imagefuncs/streamplot.py:316` | **`transpose=True` crashed on any rectangular field, and lists crashed always.** The default `x1`/`x2` were built before the transposition, from the wrong shape, so matplotlib raised `'u' and 'v' must match the shape of the (x, y) grid`; and the first row was read as `var1[:, 0]` before any conversion, which a list refuses. The components are converted first and transposed before the coordinates are built, as in `contour`, and the annotations are `ArrayLike` in the manager and in the facade. |
| `imagefuncs/streamplot.py:334` | **Every streamplot copied the field twice.** Both components were copied into new float arrays so that NaN could be written where the magnitude falls outside `vmin`/`vmax`. They are views now, and the hidden cells a boolean mask on them, which matplotlib treats exactly as NaN (the example figures are pixel-identical); no mask is built at all when neither limit is given, and the magnitude takes one allocation (`np.hypot`) instead of three. The user's arrays are never written into, as before. |
| `imagefuncs/streamplot.py:351` | **The colormap did nothing, and the colorbar described nothing.** The lines were never colored by data, since `c` is a color, yet `cpos` drew a colorbar of the field magnitude next to single-colored lines. Giving `cmap` or `cpos` now colors the lines by the magnitude, through the same scale the colorbar shows. Without either, and without `c`, the lines took matplotlib's own blue: they take the next palette color now and advance `nline`, as `plot` and `scatter` do. |
| `imagefuncs/streamplot.py:359` | **`colors` did nothing, and the `c`/`cmap` warning never fired.** Same fault as in `contour`: the check looked for `colors`, and was the only read of it. It compares `c` with `cmap` now, and `colors` is removed and warns as unknown. `UNDECLARED_KWARGS` is empty as a result. |
| `imagefuncs/streamplot.py:401` | **`alpha` was documented, accepted and never applied**, since matplotlib's `streamplot` takes no opacity. It is set on the lines and on each arrow afterwards: the arrows are separate patches on the axis, and the `arrows` collection matplotlib returns is never drawn, so setting it there changes nothing. `lw` now defaults to 1.3, as documented and as in `contour`; the figure check runs before `assign_ax`; the docstring explains the orientation, the three ways the lines are colored, and what `vmin`/`vmax` hide. |
| `imagefuncs/contour.py:286` | **`transpose=True` crashed on any rectangular variable.** The default `x1`/`x2` were built from the shape before the transposition, so `contour(var, transpose=True)` on a 6 x 4 array raised matplotlib's `TypeError: Length of x (6) must match number of columns in z (4)`. The old tests used a square array, which hid it. The variable is transposed first now, as in `display`. |
| `imagefuncs/contour.py:316` | **`c` together with `cmap` crashed, and `colors` did nothing.** The conflict check looked for `colors` instead of `c`, so it never fired and matplotlib raised `Either colors or cmap must be None`; the same check was the only read of `colors`, which is why it was accepted without effect or warning. The check compares `c` with `cmap`, warns and drops the colormap, and `colors` -- long deprecated -- is removed and now warns as unknown. |
| `imagefuncs/contour.py:275` | **The figure check was dead code**, sitting after `assign_ax`, which raises the same error first; it now runs before, as in `display`. The docstring said the method returns `None`, that `c` loops over the palette and that `cmap` defaults to `hot`: it returns the `QuadContourSet`, without `c` the colormap colors the lines, and the default is `viridis` -- kept on purpose, different from the `plasma` of `display` so lines over a map stand out. |
| `imagefuncs/display.py:300` | **A map was framed on the cell centers, half a cell short of the domain.** `pcolormesh` paints each cell half a width around its center, so the outermost half cell of the domain was cut off by the axis, and anything sitting in it -- a field line ending on the border, a particle at the wall -- fell outside a map it belongs to. `map_extent` now returns the edges, and coordinates given as edges (one more than there are cells) are used as they are. `gouraud` interpolates between the centers and would leave that half cell unpainted, so the map is given a vertex on each border holding the value of the cell it belongs to: every shading now covers the same domain. Three example figures change, all of them by the missing half cell. |
| `imagefuncs/display.py:288` | **`transpose=1` did nothing.** The keyword was compared with `is True`, so only the literal flag worked and every other true value -- a number, a numpy bool -- was silently ignored. |
| `imagefuncs/display.py:278` | **The figure check was dead code**, and two docstring examples were wrong: `I.display(x1, x2, var)` (they are keywords, so the call raises) and `cbar='right'` (no such keyword, it warns as unused). |
| `imagefuncs/scatter.py:296`, `imagefuncs/range.py:110` | **One scatter froze the axis for everything drawn after it.** Instead of the `RangeManager` it builds and never used, `scatter` faked an explicit range -- `kwargs["xrange"] = [x.min(), x.max()]` -- which `set_axis` recorded as *fixed by the user* (`setax = setay = 1`). A second scatter was then drawn outside the frame and invisible, and so was any `plot` that followed. It now goes through the manager, so the limits grow with what is added. `RangeManager` gained one case for it, 4 `strictrange`: the limits are the ones given, with none of the padding a curve gets, and the axis is left free to grow -- a point is a position, not a line to be followed. Like case 3 it is asked for by the caller rather than read off the axis, and it stands aside when the user has fixed the limits. |
| `imagefuncs/scatter.py:379` | **`label` was documented and never passed.** The scatter did not give matplotlib the label, so `scatter(label="particles", legpos="best")` built an empty legend and matplotlib warned *"No artists with labels found"* -- the keyword is in the docstring and was read by nothing. |
| `imagefuncs/scatter.py:306` | **The default color was matplotlib's, not the palette's.** `c` is either a variable to color by or a color, and when missing it was left to matplotlib, which drew its own first blue: outside the palette the docstring promises, and outside the scheme every line follows. It now takes the next palette color and advances `nline`, exactly as `plot` does. |
| `imagefuncs/scatter.py:308` | **A color per point was read as data.** Only a bare `str` was excluded from the `nanmin`/`nanmax` that compute `vmin`/`vmax`, so `c=["r", "b", ...]` -- one color per point, which matplotlib accepts -- reached `nanmin` as strings and raised `UFuncTypeError`. Numbers are data now (the `NUMERIC_KINDS` dtype kinds), anything else is colors. |
| `imagefuncs/scatter.py:377` | **Every unfilled marker warned.** `edgecolors` defaulted to `"none"`, so `scatter(marker="x")` made matplotlib warn that it was ignoring an edge color for a marker with no inside. The default is now `None`, which is what the docstring said in the first place. |
| `imagefuncs/scatter.py:352` | **An integer marker was silently redrawn as a circle.** matplotlib keeps 0 to 11 for the carets and the ticks, and `MarkerType` declares them, but the narrowing block accepted only `str`, `Path` and `MarkerStyle` and sent everything else to the default `"o"`. |
| `imagefuncs/scatter.py:294` | **The figure check was dead code.** It ran after `assign_ax`, which raises the same `ValueError` first; it is now before it, as in `plot`. |
| `imagefuncs/plot.py:290` | **A single 2D array crashed.** `I.plot(arr2d)` built the x-axis with `np.arange(y.size)`, one point per *element* instead of one per *row*, and died in `range.py` with `IndexError: index 11 is out of bounds` -- naming neither the array nor the call. `y.shape[0]` draws the lines; for a 1D array the two are the same number, so nothing else changed. |
| `imagefuncs/plot.py:326` | **The colour was weighed for emptiness.** The block read `c` twice and the second read was a truthiness test, so `c=None` -- how a caller forwards "the user did not choose" -- reached matplotlib and drew its C0 blue, outside the palette, while still consuming a palette step; and `c=np.array([0.1,0.2,0.3])`, an RGB triple the type declares and matplotlib accepts as a tuple, raised *"The truth value of an array with more than one element is ambiguous"* in our own line. It now reads `c` once and compares it to `None`. |
| `image.py` | `Image.interactive` did not declare `ax`, which `InteractiveManager.interactive` takes: it worked at runtime through `**kwargs`, but pyright rejected `I.interactive(var, ax=1)` and `help()` did not show it. Its `_check` also sat where the manager has `limfix`, so `I.interactive(x, y, False)` switched off the kwargs check instead of `limfix`. The facade now matches the manager's signature; `test_signature_matches_the_manager` compares all facade signatures with their managers. |
| `imagefuncs/set_axis.py` | `AxisManager.set_axis` required `ax`, although its docstring and the facade give it the default `None`. Default added. |
| `toolfuncs/compute_units.py`, `set_units.py` | Both imported `BaseLoadMixin` from `pyPLUTO.loadmixin`, which only re-exports it, so pyright reported `reportPrivateImportUsage` twice and the package was no longer clean under it. Now imported from `pyPLUTO.baseloadmixin`, and each file's test checks its own import. |
| `toolfuncs/transform.py:403`, `amr.py:507,553` | Two more `_check` protocol violations, the same fault as in `imagetools.text`: `reshape_cartesian(var, transpose=True)` warned that `transpose` was unused, blaming `reshape_uniform`, and `oplotbox` re-warned once per box. Regression test in the new `Tests/toolfuncs/test_transform.py`. |
| `imagefuncs/figure.py`, `imagekwargs.py`, `image.py` | **`close` and `replace` were two halves of one keyword**, each useless alone: `close` emptied the window, `replace` only decided whether `create_figure` built a new figure, and `replace=True` with `close=False` returned the *same* figure. They are one keyword now, `replace`, which empties the window and builds the figure; it defaults to replacing, except when a figure is given with `fig`, which is then the one used. `close` warns as deprecated and is read as `replace`. |
| `imagefuncs/figure.py:106` | `Image(fig=f)` cleared and closed the figure it was given, then kept using the closed object: `close` ran whether or not a figure had been passed. A figure handed in is now left alone unless `replace=True`. |
| `imagefuncs/figure.py:127` | An attached figure overwrote the keywords given with it, so `Image(fig=f, figsize=[12,3], fontsize=30)` silently kept the figure's own `[4,4]` and fontsize 10. What was asked for explicitly is applied again afterwards, and a `figsize` resizes the attached figure. |
| `imagefuncs/figure.py:116` | `nwin` given together with `fig` was silently dropped, since a figure cannot be renumbered. It now warns, and only when the two disagree. |
| `imagefuncs/figure.py:398` | **Attaching to a figure switched the tight layout off.** `state.tight` was read from `fig.get_tight_layout()`, which reports matplotlib's layout *engine*; pyPLUTO calls `tight_layout()` once and installs no engine, so it answered False for every figure pyPLUTO ever made. Only a True is inherited now. The same confusion made three tests vacuous, `test_tight_keyword_reaches_matplotlib` among them: they asserted `get_tight_layout() is False`, which holds whatever is passed. The axes box is what moves, and is what they check now. |
| `load.py`, `loadpart.py`, `imagefuncs/imagetools.py`, `colorbar.py`, `set_axis.py`, `interactive.py` | The docstrings that named something false: `full3d` for `full3D` with the opposite default, `defh` promising to read a path it ignores, `xycoords` documenting a spelling that raised `KeyError`, `cpos` saying `None` where the code uses `'right'`, `sharex`/`sharey` promising `bool | str`, the `lint` keyword that exists nowhere, and LoadPart claiming one output at a time. Also documented at last: `units`, `skip_units`, `user_units` on both classes, and `alone`, `code` on LoadPart. |
| `load.py:337` | `repeat` was advertised in `__str__` while raising `NotImplementedError`. It is no longer listed; `UNIMPLEMENTED` in `helper_load.py` keeps it covered by every delegation test, and `test_str_hides_what_is_not_implemented` fails the day it is written. |
| `imagefuncs/range.py:213` | Constant data broke the padding: a negative constant inverted the axis and a constant zero gave an empty window with a `log10(0)` warning. The padding is now taken from the absolute value, falling back to 1.0. Existing plots are unaffected -- every example figure still matches. |
| `imagekwargs.py`, `loadkwargs.py` | Keywords that worked while no table declared them, so the checkers refused them: `legpad`, `zoomcolor`, `zoomlines`, the `"both"` value of `grid`, and a sequence for `chnk`. `test_grid_declares_every_value_it_accepts` and `test_chnk_declares_the_sequence_it_accepts` guard the two that the key-level guard cannot see. |
| `imagefuncs/imagetools.py` | An unknown `cscale` was silently drawn on a linear scale. It now warns and falls back, with `linear`, `lin`, `norm` and `None` accepted as the deliberate spellings -- `norm` being the one the managers pass internally. |
| `imagefuncs/imagetools.py` | `text` called `assign_ax` without `_check=False`, so the nested call restarted the keyword tracking and reported the keywords `text` itself consumes: `I.text("hi", textsize=20)` warned about `textsize`, which its own docstring documents, and a real typo was blamed on `assign_ax`. `text` was the only method whose keyword checking was dead. |
| `imagefuncs/imagetools.py` | `find_cmap` accepted any attribute of the salsa named tuple, so `find_cmap("count")` returned its `count` method and handed it to matplotlib as a colormap. Provider results are now kept only if they really are colormaps. |
| `imagefuncs/imagetools.py` | The colormap lookup was hard-coded to pastamarkers. It now searches the packages in `CMAP_PROVIDERS` (cblind, pastamarkers, seaborn) in order, each optional and imported only when matplotlib does not know the name, with `_r` reversed by hand for packages that ship no reversed version, and a fallback to matplotlib's registry for packages such as cblind that register on import instead of exposing attributes. A user can add their own package to the dictionary, and `pyproject.toml` gained a `cmaps` extra. |
| `imagekwargs.py` | `TextKwargs` declared `horlign` while `text` reads `horalign`: the keyword worked and was documented, but the type checkers rejected it. `test_declared_keys_cover_what_the_manager_reads` now compares what every manager reads with what its table declares. |
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
