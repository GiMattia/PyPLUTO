# Tests recap

**1874 tests** · 54 known bugs as expected failures · in-scope coverage
**81.0%** · target 100%

| Status | Files |
|---|---|
| reviewed | 20 |
| almost | 0 |
| to review | 44 |
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
| `imagefuncs/create_axes.py` | `imagefuncs/test_create_axes.py` | 34 | 100% | reviewed |
| `imagefuncs/display.py` | `imagefuncs/test_display.py` | 1 | 94% | to review |
| `imagefuncs/figure.py` | `imagefuncs/test_figure.py` | 38 | 100% | reviewed |
| `imagefuncs/gridplot.py` | `imagefuncs/test_gridplot.py` | 16 | 97% | to review |
| `imagefuncs/imagetools.py` | `imagefuncs/test_imagetools.py` | 46 | 100% | reviewed |
| `imagefuncs/interactive.py` | `imagefuncs/test_interactive.py` | 8 | 74% | to review |
| `imagefuncs/legend.py` | `imagefuncs/test_legend.py` | 3 | 100% | to review |
| `imagefuncs/plot.py` | `imagefuncs/test_plot.py` | 11 | 100% | to review |
| `imagefuncs/range.py` | `imagefuncs/test_range.py` | 25 | 100% | reviewed |
| `imagefuncs/scatter.py` | `imagefuncs/test_scatter.py` | 10 | 78% | to review |
| `imagefuncs/set_axis.py` | `imagefuncs/test_set_axis.py` | 7 | 80% | to review |
| `imagefuncs/streamplot.py` | `imagefuncs/test_streamplot.py` | 8 | 84% | to review |
| `imagefuncs/volengine.py` | `imagefuncs/test_volengine.py` | 49 | 59% | to review |
| `imagefuncs/volume.py` | `imagefuncs/test_volume.py` | 5 | 91% | to review |
| `imagefuncs/zoom.py` | `imagefuncs/test_zoom.py` | 8 | 87% | to review |
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

Checks still to add, beyond the per-file work:

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
- **Memory tests.** `utils/resolver.py` exists to keep a load as small in
  memory as it can be -- it copies a mapped array once and releases the
  mapping -- and nothing measures that. A test that adds up the `nbytes` of
  the arrays a state holds and compares it with the size of the data on disk
  would have caught the `d_vars` doubling on its own, and would keep the
  next change honest. Counting bytes rather than watching RSS, so it is
  deterministic. Worth writing together with the `d_vars` work, and worth
  extending to the particle path, where the mappings are.
- **pyright at zero.** The project treats pyright as the source of truth,
  and it is at two errors today with nothing to notice. It belongs in CI
  next to the suite, not in a test.
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

**Waiting, though contained in one file** -- found after their file had been
reviewed, or held back deliberately. Each is a small fix with its own
`xfail`, and each needs a decision rather than time.

| Fix | Where | Decision it needs |
|---|---|---|
| `False` read as the index 0, so `sharexaxes=False` raises | `imagefuncs/create_axes.py:468` | none, `is False` before the int test |
| A custom layout overrules an explicit `tight` | `imagefuncs/create_axes.py:167` | whether the user or the layout wins |
| A size given to `create_axes` is not marked as chosen | `imagefuncs/create_axes.py:181` | none, set `set_size` |
| A fontsize given to `create_axes` never reaches the state | `imagefuncs/create_axes.py:158` | none |
| The scan cache is mutated by the decorator | `utils/inspector.py:33` | none, a non-mutating union |
| Sharing by axis index is declared nowhere | `imagekwargs.py:72` | whether the index form stays supported |
| `colors` accepted and ignored | `imagefuncs/contour.py`, `streamplot.py` | alias of `c`, or warn as unknown |
| `LoadPart` accepts `multiple`, which it cannot use | `loadpart.py`, `loadkwargs.py` | refuse it, or drop it from the table |

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
| A default spacing for `fourier`; `d_vars` for a tab load | `toolfuncs/fourier.py`, `loadfuncs/readtab.py` |
| Point the unused-keyword warning at the user's frame | `utils/inspector.py` |

**Later** -- these change the shape of the code, and each wants its own
session with the examples re-checked afterwards.

| Fix | Why it waits |
|---|---|
| Empty `d_vars` once the load finishes | Touches every loadfuncs writer, the resolver, `__str__` and the GUI variable list; settles the memory doubling, the divergence and the `__setattr__` question at once |
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
| `imagekwargs.py`, `utils/inspector.py` | **Keyword aliases**, e.g. `c` / `color` / `colour`, `cmap` / `colormap`. Idea of 2026-09-18, not yet designed. One table maps every alias to its canonical name, and `track_kwargs` rewrites the keys before the function body reads them, so managers keep reading one name and the scanner keeps counting one key. Three things to decide: whether the TypedDicts declare every alias (needed for the checkers to accept them, and it doubles the tables unless they are generated from the alias table), what happens when two aliases of the same keyword arrive together (warn and take one, or refuse), and how the docstrings list them, since a page per alias would be noise. It also settles the `colors` bug: as an alias of `c` it would simply apply, instead of being swallowed by a presence test. |
| `utils/inspector.py` | The whole kwargs scanner is to be rewritten in Rust as the `kwarden` package (already on PyPI). `Tests/utils/test_inspector.py` is in effect its specification: which forms are recognised, the nested-call protocol, the `_check` handling. A Rust parser also pins its own grammar version instead of inheriting the host interpreter's `ast`, which removes the "node shapes change with the Python release" risk noted in `_get_str_from_slice`. |
| `__init__.py`, `utils/configure.py` | `Configure` runs at import with switches nobody can set beforehand (see the open bug). Either read them from environment variables (`PYPLUTO_GREET=0`), or make configuration a call the user can make after import that reconfigures the handlers, or both. Decide together with whatever `set_text` becomes. |
| `baseloadstate.py`, `utils/resolver.py`, `loadfuncs/*` | **`d_vars` should be emptied once the load finishes** (decided 2026-09-18). Today it keeps the arrays for the whole session, next to the copies the resolver materialises onto the state, so every variable of a plain `Load` exists twice in memory and the two diverge: `D.rho[0,0] = -999` leaves `d_vars["rho"]` at `0.138`, `D.rho = D.rho * 2` never reaches it, and `D.myvar = arr` never appears in it, so the GUI does not list it. Everything downstream reads only the *keys* (`load.py:322`, `gui/custom_var_engine.py:94`, `gui/services.py`, `gui/load_controller.py`), while `storepart.py`, `offsetfluid.py`, `readtab.py` and `codes/echo_load.py` write the values during the load. So: keep the names, drop the data once loading is done, and the memory doubling and the divergence both disappear. This also decides the `__setattr__`/`__delattr__` question below. |
| `load.py` (`__setattr__`) | An unknown name is created silently, so a typo'd assignment fails nowhere. Cannot simply be forbidden: users deliberately attach composite variables (`data.my_composite = rho * T`) and pass the load into their own functions. Needs a design that blesses that case explicitly while still catching typos — to be discussed. |

## Open bugs

| Where | What |
|---|---|
| `load.py`, `loadpart.py`, `image.py` (`__getattr__`, `__setattr__`) | **The facades cannot be copied or unpickled, so they cannot be sent to a `multiprocessing` worker.** `__getattr__` reads `self.state`; on an instance that has no state yet, that read calls `__getattr__("state")` again, forever. `copy` and `pickle` both build the new instance without running `__init__` and then look up `__setstate__`, which takes exactly that path. Confirmed: `copy.copy` and `copy.deepcopy` raise `RecursionError` on `Load`, `LoadPart` and `Image`; `pickle.dumps` of `Load` and `Image` succeeds but `pickle.loads` raises `RecursionError`; any attribute read or write on `Image.__new__(Image)` does the same. `LoadPart` also fails `deepcopy`/`pickle` for a second reason, `cannot pickle 'mmap.mmap' object` (see the `mmaps` bug below). Nothing tests copy or pickle. The `not hasattr(self, "state")` clause in `__setattr__` belongs to the same bug: its docstring says it "makes the first line of `__init__` possible", but `name == "state"` already handles that line, and if the clause ever ran it would recurse too. Same wrong docstring in all three; `loadpart.py:262` also still says "the Load class". `template.py` has no attribute hooks, so it neither shows the pattern nor the fix. Fix: `if name == "state": raise AttributeError(name)` at the top of each `__getattr__`, then decide what copying a facade means (share or duplicate the state, reopen or drop the mmaps) before multiprocessing work starts. |
| `loadfuncs/offsetfluid.py:256`, `loadfuncs/offsetpart.py:156` | **Passing the correct `endian` explicitly corrupts the data.** For a standalone vtk load, `offset_vtk` uses `">" if state.endian is None else d_info["endianess"][exout]` — so when the user *does* pass `endian`, it keeps whatever is in that array, which `findfiles.py:94` allocated with `np.empty(dtype="U20")`, i.e. `""`. `binformat` becomes `f4` (native) instead of `>f4`. Confirmed: `Load(path="Tests/Test_load/single_file/vtk", datatype="vtk", alone=True, endian="big")` gives `rho.flat[0] = -1.49e+19`; without `endian=` the same call gives `0.138`. The `if ... is None: raise ValueError("Wrong endianess")` guards at `offsetfluid.py:261`, `offsetpart.py:80,161` are unreachable — `np.empty("U20")` yields `""`, never `None`. The rule is written four times and the copies disagree (`descriptor.py:85`, `offsetpart.py:77` propagate `state.endian` correctly). Fix: one `resolve_endianess()` helper, called from all four sites. |
| `loadfuncs/findformat.py:125` | **`alone=False` is silently ignored.** `check_format` builds `funcf` (lines 125–135) to gate which probes run given `alone`, then the loop at 138 hard-codes both probes and never reads `funcf`. `alone=True` happens to work via `type_out = []` at line 121, but `alone=False` does not: `check_typelon` still runs, finds the standalone files and sets `state.alone = True`. Confirmed on a folder holding only `data.0000.vtk`: `Load(..., alone=False).state.alone` is `True`. The user gets a standalone load with `timelist` full of NaN instead of the `FileNotFoundError` at line 157. |
| `loadfuncs/initload.py:121` | **The deprecated `vars=` keyword is warned about, then discarded.** The shim warns but never assigns to `var`, which stays `True`. Confirmed: `Load(path=..., vars="rho")` warns, then loads `['prs','rho','vx1','vx2','vx3']`. It is also in the wrong layer — `var` was already bound as a positional parameter before the manager ran. The sibling `nfile_lp` shim (`loadpart.py:168`) sits in the facade and does forward its value. |
| `loadfuncs/codeselection.py:69` | **Any non-default `code` on `LoadPart` raises `AttributeError`.** `self.echomanager` is only created `if isinstance(state, LoadState)` (line 42), but the `codedict` literal at line 69 references `self.echomanager.load_echo` eagerly, before the membership test. So it is evaluated on every call. Confirmed: `LoadPart(..., code="echo")` and even `LoadPart(..., code="nosuchcode")` both raise `AttributeError: 'CodeManager' object has no attribute 'echomanager'` — the intended `NotImplementedError` is unreachable for `LoadPart` entirely. |
| `imagefuncs/create_axes.py:468` | **`sharexaxes=False` raises `IndexError`.** `False` is an `int` in Python, so `isinstance(share, int)` is true and the flag is read as the index 0; on a fresh set of axes the list is still empty, so looking up `ax[0]` fails. Confirmed: `I.create_axes(ncol=2, sharexaxes=False)` raises, and `False` is the documented default. The `is True` case is checked first, so only the False one falls through. |
| `imagefuncs/create_axes.py:167` | **A custom layout overrides an explicit `tight`.** Any border keyword writes `kwargs["tight"] = False` before the keyword is read, so `create_axes(ncol=2, left=0.2, tight=True)` silently comes out False. Defaulting to False there is right -- matplotlib cannot lay out axes it did not place -- but it should not overrule the user. |
| `imagefuncs/create_axes.py:181` | **A size given to `create_axes` is forgotten.** It sets `state.figsize` without setting `set_size`, the flag that marks a size as chosen rather than computed, so the next `create_axes()` recomputes it: `create_axes(figsize=[10,4])` then `create_axes()` leaves the figure at 6x5 while the state still says `[10, 4]`. |
| `imagefuncs/create_axes.py:158` | **A fontsize given to `create_axes` never reaches the state.** It is written into matplotlib's `rcParams` only, so `image.fontsize` keeps reporting 17 while the figure is drawn at 13, and everything reading the state -- the legend, the text box -- uses the stale value. The old test passed `fontsize=17`, the value already there, so it could not fail. |
| `imagekwargs.py:72` | `sharexaxes` and `shareyaxes` accept an axis index, which is how a set of axes is tied to one created earlier, while `CreateAxesKwargs` declares `bool \| str \| Axes`: the call works and every checker refuses it. Same family as the `grid="both"` gap. |
| `utils/inspector.py:33` | **The scan cache is written into.** `_find_kwargs_keys_from_source` is `@functools.cache`d and returns a mutable set; `track_kwargs` then does `used_keys \|= extra_keys`, mutating the cached object, so scanning an untouched source reports keys that do not appear in it -- `create_axes` scans as reading `left`, `right`, `top`... which are nowhere in its body. Any caller of `find_kwargs_keys` receives a set others can mutate, and two functions with identical source text share one entry. A non-mutating union fixes it, and returning a `frozenset` stops it recurring. Found while asking whether `extra_keys` are checked like other keywords: at runtime they are, but our guards only see them because of this. |
| `utils/configure.py:260` | **Importing pyPLUTO resets the user's warning filters.** `Configure` calls `warnings.simplefilter("always")`, which clears the whole filter list, so `python -W ignore` and any `filterwarnings("ignore")` made beforehand stop working for the rest of the process. Confirmed in a subprocess. A filter scoped to `module="pyPLUTO"` would do the same job without touching anyone else's. |
| `load.py:284`, `loadpart.py:210` | **`repr()` crashes on a load that read nothing.** `Load(nout=None)` is documented as "do not load", and `repr(D)` then raises `AttributeError: no attribute 'nout'`; `str(D)` raises on `geom`. A repr is what a debugger and the prompt call by themselves, so it must never raise. |
| `baseloadstate.py:24`, `loadstate.py:17` | **Two states cannot be compared.** The generated `__eq__` reads the load-only fields: `LoadState() == LoadState()` raises `AttributeError`, and two real states raise `ValueError` on the array comparison. `eq=False` would at least give identity. |
| `imagefuncs/range.py:213` | **Constant data breaks the padding.** The zero-width case pads from `ymax * 0.1`: a constant negative value gives a negative padding and an inverted axis (`ylim = (-4.95, -5.05)`), and a constant zero gives `(0.0, 0.0)` plus a `log10(0)` RuntimeWarning. `abs(ymax) * 0.1 or 1.0` fixes both. |
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
| `imagefuncs/colorbar.py` | Docstring says no colorbar without `cpos`, but the default is `"right"`. |
| `imagekwargs.py` | 259 declared kwargs are undocumented in the method docstrings. 15 per method are the figure-level ones inherited from `ImageKwargs`, documented on `Image.__init__` instead; after those, what is left is `sharexaxes`/`shareyaxes` in every method but `create_axes` (which documents them), `showgrid` (49 of 68), `volume` (51 of 87) and `scatter` (`transpose`, `x1`, `x2`). `test_every_parameter_is_documented` covers the parameters, which are all documented today; the keywords need a guard of the same shape once these are written. |
| `imagefuncs/contour.py:294`, `streamplot.py:310` | **`colors` is accepted and silently ignored.** It is read only as a presence test, to warn when it is given together with `cmap`; the colour applied comes from `c`. Confirmed: `I.contour(var, colors="red")` leaves the colormap at `viridis` and warns about nothing, while `c="red"` works. The presence test is also what stops the tracker reporting it as unused. Either make it an alias of `c` (see the alias idea in *Deferred structural improvements*) or let it warn like any unknown keyword, and compare `c` with `cmap` in the conflict check. |
| `imagefuncs/range.py:132,156` | **The y-limits are computed from all the data, not from the visible window.** Both computing cases filter with `np.where(np.logical_and(x >= x.min(), x <= x.max()))`, which is true for every point, so the mask selects the whole array (confirmed: 11 of 11). The comment says "find the limits of the x-axis", so the intent was the current x-limits: a point far outside the window still sets the y-range. Fixing it changes the limits of existing plots, so it needs the example figures rechecked. `test_set_yrange_measures_all_the_data` documents today's behaviour. |
| `imagefuncs/range.py:227` | **A negative range on a log scale loses its lower limit.** `ymax = max(abs(ymin), abs(ymax))` reads `ymin` after the line above reassigned it, so the original value cannot be seen: `range_offset(-100, 10, "log")` gives `(5.0, 21.0)` instead of a range reaching 100. Only on the warned path. `test_range_offset_negative_log_loses_the_lower_limit` pins it. |
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
