"""Lazy mmap-backed attribute materialisation shared across Load classes."""

from __future__ import annotations

import contextlib
import mmap
from typing import cast

import numpy as np


class AttrResolver:
    """Materialise lazy mmap-backed attributes on first access.

    All three Load classes (Load, Image, LoadPart) call AttrResolver.resolve().
    Only LoadPart carries mmap-backed data, so only it will hit the
    materialisation branches; the others fall straight through to
    ``return val``.
    """

    @staticmethod
    def resolve(state: object, name: str, val: object) -> object:
        """Dispatch val to the appropriate materialisation strategy."""
        # Keep unit-aware arrays untouched (e.g., astropy Quantity).
        if hasattr(val, "unit"):
            return val
        if isinstance(val, list) and val and isinstance(val[0], np.ndarray):
            return AttrResolver._chunk_list(
                state,
                name,
                cast("list[np.ndarray]", val),
            )
        if isinstance(val, dict) and val:
            first = next(iter(val.values()))
            is_chunk_list = (
                isinstance(first, list)
                and first
                and isinstance(first[0], np.ndarray)
            )
            if is_chunk_list:
                return AttrResolver._chunk_dict(state, name, val)
        if isinstance(val, np.ndarray) and val.base is not None:
            return AttrResolver._mmap_array(state, name, val)
        return val

    @staticmethod
    def _chunk_list(
        state: object,
        name: str,
        val: list[np.ndarray],
    ) -> np.ndarray:
        """Concatenate a list of array chunks, cache the result, and return it.

        Parameters
        ----------
        - state: object
            The owner object on which the materialised array will be cached.
        - name: str
            Attribute name used to store the result back onto *state*.
        - val: list[np.ndarray]
            Ordered list of contiguous array chunks to concatenate.

        Returns
        -------
        - np.ndarray
        """
        result = AttrResolver._copy_chunks(val)
        setattr(state, name, result)
        return result

    @staticmethod
    def _chunk_dict(state: object, name: str, val: dict) -> dict:
        """Concatenate chunk-lists for every value in a dict, cache, and return.

        Each dictionary value is expected to be a list of array chunks (the
        same structure accepted by ``_chunk_list``).  The resulting dict maps
        the same keys to fully materialised arrays.

        Parameters
        ----------
        - state: object
            The owner object on which the materialised dict will be cached.
        - name: str
            Attribute name used to store the result back onto *state*.
        - val: dict
            Mapping whose values are ordered lists of array chunks.

        Returns
        -------
        - dict
        """
        result = {k: AttrResolver._copy_chunks(v) for k, v in val.items()}
        setattr(state, name, result)
        return result

    @staticmethod
    def _mmap_array(state: object, name: str, val: np.ndarray) -> np.ndarray:
        """Copy an mmap-backed array into owned memory and release the mapping.

        The copy is performed via ``np.array(val)`` which forces a full
        read into a new allocation.  After copying, ``MADV_DONTNEED`` is
        issued on the backing mmap so the OS can reclaim the page-cache pages.

        Parameters
        ----------
        - state: object
            The owner object on which the owned array will be cached.
        - name: str
            Attribute name used to store the result back onto *state*.
        - val: np.ndarray
            An array whose ``.base`` chain ultimately leads to an mmap object.

        Returns
        -------
        - np.ndarray
        """
        result = np.array(val)
        AttrResolver._dontneed(val)
        setattr(state, name, result)
        return result

    @staticmethod
    def _get_mmap(arr: np.ndarray) -> mmap.mmap | None:
        """Walk the .base chain to find the underlying mmap.mmap, if any."""
        obj = arr
        base = getattr(obj, "base", None)
        while isinstance(base, np.ndarray):
            obj = base
            base = getattr(obj, "base", None)
        return base if isinstance(base, mmap.mmap) else None

    @staticmethod
    def _dontneed(arr: np.ndarray) -> None:
        """Hint the OS to evict the page cache pages backing arr's mmap."""
        if (mm := AttrResolver._get_mmap(arr)) is not None:
            with contextlib.suppress(AttributeError, OSError):
                mm.madvise(mmap.MADV_DONTNEED)

    @staticmethod
    def _copy_chunks(chunks: list[np.ndarray]) -> np.ndarray:
        """Pre-allocate result, copy one chunk at a time, evict each."""
        total = sum(c.shape[-1] for c in chunks)
        result = np.empty((*chunks[0].shape[:-1], total), dtype=chunks[0].dtype)
        pos = 0
        for chunk in chunks:
            n = chunk.shape[-1]
            result[..., pos : pos + n] = chunk
            AttrResolver._dontneed(chunk)
            pos += n
        return result
