"""Test of the resolver.py file."""

import mmap

import numpy as np
import numpy.testing as npt

from pyPLUTO.utils.resolver import AttrResolver


class _State:
    """A bare object standing in for a Load state."""


# A plain value is handed back untouched
def test_resolve_plain_value():
    state = _State()
    assert AttrResolver.resolve(state, "a", 42) == 42


# A plain array is handed back untouched
def test_resolve_plain_array():
    state = _State()
    arr = np.arange(4)
    assert AttrResolver.resolve(state, "a", arr) is arr


# A list of chunks is joined into a single array
def test_resolve_chunk_list():
    state = _State()
    chunks = [np.arange(3.0), np.arange(3.0, 6.0)]
    npt.assert_allclose(
        AttrResolver.resolve(state, "a", chunks), np.arange(6.0)
    )


# The joined array is cached on the state, so it is built only once
def test_resolve_chunk_list_is_cached():
    state = _State()
    result = AttrResolver.resolve(state, "a", [np.arange(3.0)])
    npt.assert_allclose(state.a, result)


# The chunks are joined along the last axis
def test_resolve_chunk_list_2D():
    state = _State()
    chunks = [np.ones((2, 3)), np.zeros((2, 4))]
    assert AttrResolver.resolve(state, "a", chunks).shape == (2, 7)


# A dictionary of chunk lists is joined entry by entry
def test_resolve_chunk_dict():
    state = _State()
    val = {"rho": [np.arange(2.0), np.arange(2.0, 4.0)]}
    result = AttrResolver.resolve(state, "a", val)
    npt.assert_allclose(result["rho"], np.arange(4.0))


# The joined dictionary is cached on the state too
def test_resolve_chunk_dict_is_cached():
    state = _State()
    AttrResolver.resolve(state, "a", {"rho": [np.arange(2.0)]})
    assert "rho" in state.a


# A dictionary that does not hold chunk lists is left alone
def test_resolve_plain_dict():
    state = _State()
    val = {"rho": np.arange(3)}
    assert AttrResolver.resolve(state, "a", val) is val


# An empty list or dict has nothing to join
def test_resolve_empty_containers():
    state = _State()
    assert AttrResolver.resolve(state, "a", []) == []
    assert AttrResolver.resolve(state, "b", {}) == {}


# A value carrying a unit is never materialised
def test_resolve_keeps_unit_aware_values():
    class _WithUnit:
        unit = "g/cm3"

    state = _State()
    val = _WithUnit()
    assert AttrResolver.resolve(state, "a", val) is val


# A view on another array is copied into memory it owns
def test_resolve_view_is_copied():
    state = _State()
    base = np.arange(6.0)
    view = base[2:]
    result = AttrResolver.resolve(state, "a", view)
    npt.assert_allclose(result, [2.0, 3.0, 4.0, 5.0])
    assert result.base is None


# A memory-mapped array is found through the chain of views
def test_get_mmap_finds_the_mapping(tmp_path):
    """LONG TEST: CHECK"""
    binary = tmp_path / "data.bin"
    binary.write_bytes(np.arange(8, dtype=np.float64).tobytes())

    mapped = np.memmap(binary, dtype=np.float64, mode="r")
    assert isinstance(AttrResolver._get_mmap(mapped), mmap.mmap)
    assert isinstance(AttrResolver._get_mmap(mapped[2:]), mmap.mmap)
    del mapped


# An array that is not memory mapped has no mapping to find
def test_get_mmap_without_mapping():
    assert AttrResolver._get_mmap(np.arange(4)) is None


# Releasing the pages of a plain array is simply a no-op
def test_dontneed_on_plain_array():
    assert AttrResolver._dontneed(np.arange(4)) is None


# The chunks keep their order when they are joined
def test_copy_chunks_keeps_order():
    chunks = [np.array([1.0, 2.0]), np.array([3.0]), np.array([4.0, 5.0])]
    npt.assert_allclose(
        AttrResolver._copy_chunks(chunks), [1.0, 2.0, 3.0, 4.0, 5.0]
    )


# The joined array keeps the dtype of the chunks
def test_copy_chunks_keeps_dtype():
    chunks = [np.arange(2, dtype=np.float32)]
    assert AttrResolver._copy_chunks(chunks).dtype == np.float32
