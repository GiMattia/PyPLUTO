"""Test of the resolver.py file.

AttrResolver sits behind every attribute read of Load, Image and LoadPart, so
these tests stand between a user and their data. What it promises is narrow
but easy to break silently: the right values come back, a mapped array is
copied into memory the state owns, the mapping is handed back to the system,
and the result is cached so the second access costs nothing.

Most of the tests below check one of those four promises on one kind of value.
The awkward part is that the failures the class exists to prevent -- a mapping
that is never released, a value that is copied when it should not be -- do not
change any number a test can read, so several tests watch what the resolver
*does* (by replacing a helper and recording the calls) rather than only what
it returns.
"""

import mmap
from pathlib import Path

import numpy as np
import numpy.testing as npt
import pytest

from pyPLUTO.utils.resolver import AttrResolver


class _State:
    """A bare object standing in for a Load state.

    The resolver only ever does two things to the state it is given: read
    nothing from it, and cache the materialised value onto it under the
    attribute name. A real LoadState would work just as well here, but an
    empty class makes it obvious that nothing else is involved.

    The two attributes are declared so that the type checkers accept the
    tests reading them back; they are never given a value here, and their
    presence after a resolve is exactly what the caching tests assert.
    """

    a: object
    b: object


# ---- Values that are handed back untouched ----
# Only LoadPart ever holds mapped data, so for Load and Image every attribute
# read falls through these branches. They are the common case, and the one
# where doing anything at all would be a bug.
def test_resolve_plain_value() -> None:
    """Pass an ordinary number through the resolver and get it back.

    Nothing about an int is lazy, so there is nothing to materialise. If this
    fails, the dispatcher has started treating scalars as something that
    needs work, and every `Data.nx1` in user code now goes down a branch
    meant for arrays.
    """
    state = _State()
    assert AttrResolver.resolve(state, "a", 42) == 42


def test_resolve_plain_array() -> None:
    """Pass an array that owns its memory and get the same object back.

    The check is `is`, not equality: the array must not be copied. An array
    with no base is either one that was never mapped or one that has already
    been resolved, and copying it on every access would make each attribute
    read cost the size of the data.
    """
    state = _State()
    arr = np.arange(4)
    assert AttrResolver.resolve(state, "a", arr) is arr


def test_resolve_plain_dict() -> None:
    """Pass a dict whose values are plain arrays and get the same dict back.

    A dict only means "chunked variables" when its values are lists of
    arrays. Here they are arrays already, so the dict is data, not a
    structure to join. Failing this would mean `_chunk_dict` is reached with
    values it cannot iterate over as chunks.
    """
    state = _State()
    val = {"rho": np.arange(3)}
    assert AttrResolver.resolve(state, "a", val) is val


def test_resolve_empty_containers() -> None:
    """Pass an empty list and an empty dict through, unchanged.

    Both branches look at their first element to decide what they are
    holding, so an empty container has nothing to look at. The guards are
    what stop that from raising IndexError or StopIteration on a load whose
    variables have not been filled in yet.
    """
    state = _State()
    assert AttrResolver.resolve(state, "a", []) == []
    assert AttrResolver.resolve(state, "b", {}) == {}


def test_resolve_list_of_non_arrays() -> None:
    """Pass a list of ints through, since a chunk list holds arrays.

    Only the first element decides, because the loader builds these lists
    and they are homogeneous by construction. This test records that the
    decision is made on the type of that element and not on being a list,
    so an ordinary list attribute is never mistaken for chunked data.
    """
    state = _State()
    val = [1, 2, 3]
    assert AttrResolver.resolve(state, "a", val) is val


def test_resolve_keeps_unit_aware_values() -> None:
    """Pass an object that carries a unit through untouched.

    After `to_astropy_units` the state holds Quantities instead of arrays.
    They are already values in their own right, and the resolver recognises
    them by the one attribute every Quantity has. Anything else with a
    `.unit` is left alone too, which is the point of testing it with a stub
    rather than with astropy.
    """

    class _WithUnit:
        """Stand in for anything that carries a unit, Quantity included."""

        unit = "g/cm3"

    state = _State()
    val = _WithUnit()
    assert AttrResolver.resolve(state, "a", val) is val


def test_unit_check_comes_before_the_view_check() -> None:
    """Pass a sliced Quantity through, which both branches could claim.

    This is the one case where the order of the checks in `resolve` can be
    observed. A slice of a Quantity is unit-aware *and* a view, so whichever
    check comes first wins: the unit branch returns it untouched, the view
    branch would copy it with `np.array` and hand back a bare array with the
    unit gone.

    A failure here means someone reordered those two `if`s, and every unit
    that a user attached is being quietly stripped on the next attribute
    read. The second assertion is the sharper one: an untouched value must
    also not be cached, since caching is what materialisation leaves behind.
    """
    astropy_units = pytest.importorskip("astropy.units")
    state = _State()
    val = (np.arange(4.0) * astropy_units.g)[1:]

    assert AttrResolver.resolve(state, "a", val) is val
    assert not hasattr(state, "a"), "a unit-aware value must not be cached"


# ---- Lists of chunks ----
# A particle output is written one file per chunk, so a single variable
# arrives as a list of arrays that have to be joined before the user sees it.
def test_resolve_chunk_list() -> None:
    """Join two chunks and check the values, in order, end to end.

    The `isinstance` is not ceremony: `resolve` is typed as returning
    `object`, so this both narrows the type for the checkers and asserts the
    branch produced an array rather than handing the list back.
    """
    state = _State()
    chunks = [np.arange(3.0), np.arange(3.0, 6.0)]
    result = AttrResolver.resolve(state, "a", chunks)
    assert isinstance(result, np.ndarray)
    npt.assert_allclose(result, np.arange(6.0))


def test_resolve_chunk_list_is_cached() -> None:
    """Join one chunk and find the result stored on the state afterwards.

    Caching is what makes the whole class affordable: the joined array has
    no base, so the next access falls through the pass-through branch and
    costs an attribute lookup. Without it every read of a chunked variable
    would join the chunks again.
    """
    state = _State()
    result = AttrResolver.resolve(state, "a", [np.arange(3.0)])
    assert isinstance(result, np.ndarray)
    assert isinstance(state.a, np.ndarray)
    npt.assert_allclose(state.a, result)


def test_resolve_chunk_list_2D() -> None:
    """Join chunks that share a leading axis and check the shape.

    Chunks are pieces of one variable split along the last axis, so joining
    a (2, 3) and a (2, 4) must give (2, 7) and not (4, 3) or a flat array.
    The values are covered elsewhere; what is checked here is which axis the
    join happens on.
    """
    state = _State()
    chunks = [np.ones((2, 3)), np.zeros((2, 4))]
    result = AttrResolver.resolve(state, "a", chunks)
    assert isinstance(result, np.ndarray)
    assert result.shape == (2, 7)


def test_copy_chunks_keeps_order() -> None:
    """Join three chunks of different lengths and check the sequence.

    The chunks are written in file order and must stay in it, so this uses
    uneven lengths: with equal ones a bug in the write position could still
    produce a plausible-looking array.
    """
    chunks = [np.array([1.0, 2.0]), np.array([3.0]), np.array([4.0, 5.0])]
    npt.assert_allclose(
        AttrResolver._copy_chunks(chunks), [1.0, 2.0, 3.0, 4.0, 5.0]
    )


def test_copy_chunks_keeps_dtype() -> None:
    """Join float32 chunks and check the result is still float32.

    The result is pre-allocated, so its dtype is chosen rather than inferred,
    and the obvious wrong choice is the float64 default. Silently promoting
    would double the memory of every particle variable.
    """
    chunks = [np.arange(2, dtype=np.float32)]
    assert AttrResolver._copy_chunks(chunks).dtype == np.float32


def test_copy_chunks_releases_every_chunk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Join three chunks and record that each one was released.

    This is the reason the join is written as a loop rather than as
    `np.concatenate`: concatenate cannot hand anything back until it has
    finished, so it leaves every chunk it read resident, while copying one
    at a time allows each to be released immediately. For mapped chunks that
    is the difference between holding the result and holding the result plus
    the whole dataset.

    None of that shows up in a returned value, so `_dontneed` is replaced by
    a function that records the size of what it was asked to release. The
    expected list therefore describes both *that* every chunk was released
    and *when*: one call per chunk, in order.
    """
    released: list[int] = []

    def record(arr: np.ndarray) -> None:
        """Stand in for _dontneed, noting the chunk it was handed."""
        released.append(arr.shape[-1])

    monkeypatch.setattr(AttrResolver, "_dontneed", staticmethod(record))

    chunks = [np.arange(2.0), np.arange(3.0), np.arange(4.0)]
    AttrResolver._copy_chunks(chunks)
    assert released == [2, 3, 4]


# ---- Dictionaries of chunk lists ----
def test_resolve_chunk_dict() -> None:
    """Join the chunk list held under one key of a dictionary.

    A dictionary of chunk lists is a whole output: one entry per variable.
    The result must stay a dictionary with the same keys, holding joined
    arrays instead of lists.
    """
    state = _State()
    val = {"rho": [np.arange(2.0), np.arange(2.0, 4.0)]}
    result = AttrResolver.resolve(state, "a", val)
    assert isinstance(result, dict)
    npt.assert_allclose(result["rho"], np.arange(4.0))


def test_resolve_chunk_dict_is_cached() -> None:
    """Join a one-key dictionary and find it stored on the state.

    The same caching promise as for a chunk list, checked separately because
    it is a separate branch: a dictionary that were joined but never stored
    would be rebuilt on every access to `d_vars`.
    """
    state = _State()
    AttrResolver.resolve(state, "a", {"rho": [np.arange(2.0)]})
    assert isinstance(state.a, dict)
    assert "rho" in state.a


def test_resolve_chunk_dict_joins_every_key() -> None:
    """Join a two-key dictionary and check both entries came out joined.

    Whether a dictionary holds chunk lists is decided by looking at its
    first value only, which is cheap and correct, but it makes an obvious
    mistake possible: materialising the entry that was inspected and leaving
    the rest as lists. A user would then find `d_vars["rho"]` an array and
    `d_vars["prs"]` a list of arrays, with no error anywhere.

    The keys are deliberately given uneven chunk lists so the two entries
    cannot be confused for one another.
    """
    state = _State()
    val = {
        "rho": [np.arange(2.0), np.arange(2.0, 4.0)],
        "prs": [np.arange(3.0)],
    }
    result = AttrResolver.resolve(state, "a", val)
    assert isinstance(result, dict)
    assert sorted(result) == ["prs", "rho"]
    npt.assert_allclose(result["rho"], np.arange(4.0))
    npt.assert_allclose(result["prs"], np.arange(3.0))


# ---- Arrays backed by something else ----
# An array with a base is a window onto memory it does not own: a mapping, or
# a slice of one. These are the arrays that have to be copied before the
# mapping behind them can be released.
def test_resolve_view_is_copied() -> None:
    """Resolve a slice of an array and check the result owns its memory.

    `result.base is None` is the assertion that matters: it is what
    distinguishes a copy from another window onto the same memory. A view
    handed back unchanged would keep the array it came from alive, and for a
    mapped array would keep the file mapped.
    """
    state = _State()
    base = np.arange(6.0)
    view = base[2:]
    result = AttrResolver.resolve(state, "a", view)
    assert isinstance(result, np.ndarray)
    npt.assert_allclose(result, [2.0, 3.0, 4.0, 5.0])
    assert result.base is None


def test_mmap_array_releases_the_mapping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolve a view and record that its pages were released afterwards.

    Copying is only half the job. Without the release the pages stay in the
    page cache for the rest of the session although nothing will read them
    again, which is the cost this class exists to avoid.

    Nothing about the returned array shows whether the release happened, so
    `_dontneed` is replaced by a recorder as in the chunk test above. The
    size checks that it was handed the original window rather than the copy.
    Deleting the release call from the source leaves every other test in
    this file passing, which is why this one exists.
    """
    released: list[int] = []

    def record(arr: np.ndarray) -> None:
        """Stand in for _dontneed, noting the array it was handed."""
        released.append(arr.size)

    monkeypatch.setattr(AttrResolver, "_dontneed", staticmethod(record))

    state = _State()
    AttrResolver.resolve(state, "a", np.arange(6.0)[2:])
    assert released == [4]


def test_resolve_memmap_is_copied_and_cached(tmp_path: Path) -> None:
    """Resolve a real memory-mapped array, end to end.

    Every other test in this section uses a view, which takes the same
    branch and is cheaper to build. This one uses an actual file so that the
    case the class was written for is exercised at least once: LoadPart maps
    its data files, and the first attribute read has to turn a window onto a
    file into an ordinary array.

    The four assertions are the four halves of that: the result is an array
    and no longer a memmap, it owns its memory, it holds the file's values,
    and it was left on the state for next time.
    """
    binary = tmp_path / "data.bin"
    binary.write_bytes(np.arange(8, dtype=np.float64).tobytes())
    mapped = np.memmap(binary, dtype=np.float64, mode="r")

    state = _State()
    result = AttrResolver.resolve(state, "a", mapped)

    assert isinstance(result, np.ndarray)
    assert not isinstance(result, np.memmap)
    assert result.base is None
    npt.assert_allclose(result, np.arange(8.0))
    assert state.a is result

    # Drop the mapping before the temporary file goes away.
    del mapped


def test_resolve_is_idempotent() -> None:
    """Resolve a value, resolve the result again, and get the same object.

    This is the property that makes caching work rather than merely save
    time. The materialised array has no base, so the second call falls
    through the pass-through branch instead of copying again. If it did not,
    caching would only move the cost rather than remove it, since every
    access would copy the cached array afresh.
    """
    state = _State()
    first = AttrResolver.resolve(state, "a", [np.arange(3.0)])
    assert AttrResolver.resolve(state, "a", first) is first


# ---- Finding and releasing the mapping ----
# Releasing pages means asking the mapping behind an array, which has to be
# found first, and the array at hand is usually a slice rather than the map.
def test_get_mmap_finds_the_mapping(tmp_path: Path) -> None:
    """Find the mapping behind a memmap, and behind a slice of one.

    The two cases differ by one link: the base of the memmap is the mapping
    itself, while the base of a slice is the memmap array and the mapping is
    behind that. Both have to be found, which is why the lookup is a loop.
    """
    binary = tmp_path / "data.bin"
    binary.write_bytes(np.arange(8, dtype=np.float64).tobytes())

    mapped = np.memmap(binary, dtype=np.float64, mode="r")
    assert isinstance(AttrResolver._get_mmap(mapped), mmap.mmap)
    assert isinstance(AttrResolver._get_mmap(mapped[2:]), mmap.mmap)
    del mapped


def test_get_mmap_follows_a_chain_of_views(tmp_path: Path) -> None:
    """Find the mapping behind a slice that was sliced twice more.

    numpy collapses repeated slicing -- the base of a slice of a slice is
    the array that owns the memory, not the view in between -- so this is
    not a longer chain than the test above, and it is not meant to be. What
    it pins is that slicing an already-resolved attribute again cannot hide
    the mapping from the lookup, whatever a caller does to the array first.
    """
    binary = tmp_path / "data.bin"
    binary.write_bytes(np.arange(8, dtype=np.float64).tobytes())

    mapped = np.memmap(binary, dtype=np.float64, mode="r")
    assert isinstance(AttrResolver._get_mmap(mapped[2:][1:][:2]), mmap.mmap)
    del mapped


def test_get_mmap_without_mapping() -> None:
    """Look behind an ordinary array and find nothing.

    An array that owns its memory has no base at all, so the loop never runs
    and there is nothing to release. This is the answer for every array in a
    fluid Load, none of which is mapped.
    """
    assert AttrResolver._get_mmap(np.arange(4)) is None


def test_get_mmap_ignores_a_base_that_is_not_a_mapping() -> None:
    """Look behind an array built on a buffer and find nothing.

    This array does have a base, so it gets past the first condition, but
    the base is a bytes object with no pages to hand back. The caller goes
    straight on to call `madvise` on whatever is returned, so returning
    anything that is not a mapping would be an AttributeError on a plain
    attribute read.

    Removing the type check from the source leaves every other test here
    passing, because they all use arrays whose chain ends on None.
    """
    arr = np.frombuffer(np.arange(4, dtype=np.float64).tobytes())
    assert arr.base is not None
    assert AttrResolver._get_mmap(arr) is None


def test_dontneed_on_plain_array() -> None:
    """Ask for the pages of an unmapped array to be released, and do nothing.

    Releasing is attempted on every array that is copied, most of which are
    not mapped, so the quiet no-op is the common path rather than an edge
    case.
    """
    assert AttrResolver._dontneed(np.arange(4)) is None


def test_dontneed_survives_a_refusal(monkeypatch: pytest.MonkeyPatch) -> None:
    """Release pages through a mapping that refuses, and carry on anyway.

    `madvise` is advice to the kernel, not an instruction: it is rejected on
    some platforms and filesystems, and missing altogether on some builds of
    Python. Losing the hint costs memory, while raising would abort a user
    who was doing nothing more than reading an attribute, so the refusal is
    swallowed.

    The refusal is staged by replacing the lookup with one that returns a
    mapping whose `madvise` raises, since provoking a genuine rejection
    would depend on the machine the tests happen to run on.
    """

    class _Refusing:
        """Stand in for a mapping whose madvise is not allowed."""

        def madvise(self, *_args: object) -> None:
            """Refuse the hint the way an unsupported platform would."""
            raise OSError(22, "Invalid argument")

    monkeypatch.setattr(
        AttrResolver, "_get_mmap", staticmethod(lambda _arr: _Refusing())
    )
    assert AttrResolver._dontneed(np.arange(4)) is None
