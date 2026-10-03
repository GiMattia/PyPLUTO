"""Attribute resolution shared across the Load classes.

Loading a simulation does not read the data files: it memory-maps them, so
the arrays on the state are windows onto the files rather than values in
memory. A load is therefore instant even for a dataset larger than the
available RAM, and a slice of a variable reads only the part of the file it
covers. The files are mapped copy-on-write, so a variable can be modified in
memory without the file being touched.

A mapped variable is handed out as it is. The one value built here is a
variable split over several files, a chunked particle output, whose pieces
are joined into a single array the first time it is read.
"""

from __future__ import annotations

import contextlib
import mmap
from typing import cast

import numpy as np


class AttrResolver:
    """Resolve the attributes of a load on access.

    All three facades (Load, Image, LoadPart) call AttrResolver.resolve().
    Only a chunked particle output, a variable split over several files,
    is built into a new value; everything else, mapped variables included,
    is handed back as it is.

    The class is a namespace of static methods rather than an object: it holds
    no state of its own, and the state it works on is passed in, since the
    caller is the one that owns the attribute being resolved.
    """

    @staticmethod
    def resolve(state: object, name: str, val: object) -> object:
        """Return the value of an attribute, joining a chunked one.

        Two kinds of value need work: a list of array chunks (one per file
        of a multi-chunk particle output) and a dictionary of such lists
        (one entry per variable). Anything else -- a mapped variable, a
        number, a unit-aware array -- is returned as it is.

        Parameters
        ----------
        - state (not optional): object
            The load state that owns the attribute. The materialised value is
            cached back onto it, so the work is done only once.
        - name (not optional): str
            The attribute name, used as the key for that cache.
        - val (not optional): object
            The value currently stored on the state, lazy or not.

        Returns
        -------
        - object
            The joined value for a chunked variable, ``val`` itself
            otherwise.

        Examples
        --------
        - Example #1: anything not chunked is handed straight back

            >>> AttrResolver.resolve(state, "nx1", 128)
            128

        - Example #2: a list of chunks is joined into one array

            >>> AttrResolver.resolve(state, "vx1", [chunk0, chunk1])

        """
        # A list of arrays is the chunked output of one variable. Only the
        # first element is examined: the list is built by the loader, so it
        # is homogeneous by construction.
        if isinstance(val, list) and val and isinstance(val[0], np.ndarray):
            return AttrResolver._chunk_list(
                state,
                name,
                cast("list[np.ndarray]", val),
            )

        # A dictionary of such lists holds several variables at once, and is
        # recognised the same way, from its first value.
        if isinstance(val, dict) and val:
            first = next(iter(val.values()))
            is_chunk_list = (
                isinstance(first, list)
                and first
                and isinstance(first[0], np.ndarray)
            )
            if is_chunk_list:
                return AttrResolver._chunk_dict(state, name, val)

        return val

    @staticmethod
    def _chunk_list(
        state: object,
        name: str,
        val: list[np.ndarray],
    ) -> np.ndarray:
        """Concatenate a list of array chunks, cache the result, and return it.

        A particle output is written one file per chunk, so a single variable
        arrives as a list of arrays that have to be joined end to end before
        the user sees it.

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

        Examples
        --------
        - Example #1: join the two chunks of a variable

            >>> AttrResolver._chunk_list(state, "vx1", [chunk0, chunk1])

        """
        result = AttrResolver._copy_chunks(val)

        # Cache on the state, so the next access finds a plain array and
        # resolve() falls straight through.
        setattr(state, name, result)
        return result

    @staticmethod
    def _chunk_dict(state: object, name: str, val: dict) -> dict:
        """Concatenate chunk-lists for every value in a dict, cache, and return.

        Each dictionary value is expected to be a list of array chunks (the
        same structure accepted by ``_chunk_list``).  The resulting dict maps
        the same keys to fully materialised arrays.

        Every entry is joined, not only the one that was inspected to
        recognise the structure: the dictionary is the whole set of variables
        of an output, and a half-materialised one would be a trap.

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

        Examples
        --------
        - Example #1: join every variable of a particle output

            >>> AttrResolver._chunk_dict(state, "d_vars", chunked)

        """
        result = {k: AttrResolver._copy_chunks(v) for k, v in val.items()}
        setattr(state, name, result)
        return result

    @staticmethod
    def _get_mmap(arr: np.ndarray) -> mmap.mmap | None:
        """Walk the .base chain to find the underlying mmap.mmap, if any.

        numpy collapses repeated slicing, so the base of a slice is the array
        that owns the memory rather than the view it was taken from. A memmap
        still puts one link in the way: the base of a slice is the memmap
        array, and the mapping is behind *that*. One lookup is therefore not
        enough, which is why the chain is walked rather than read once.

        Parameters
        ----------
        - arr: np.ndarray
            The array to look behind.

        Returns
        -------
        - mmap.mmap | None
            The mapping, or None when the chain ends on anything else: an
            array that owns its memory has no base at all, and one built on
            a buffer ends on an object with no pages to release.

        Examples
        --------
        - Example #1: the mapping behind a slice of a memmap

            >>> AttrResolver._get_mmap(mapped[2:])

        """
        # Follow the chain while each base is itself an array.
        obj = arr
        base = getattr(obj, "base", None)
        while isinstance(base, np.ndarray):
            obj = base
            base = getattr(obj, "base", None)

        # Whatever the chain ended on is only useful if it is a mapping.
        return base if isinstance(base, mmap.mmap) else None

    @staticmethod
    def _dontneed(arr: np.ndarray) -> None:
        """Hint the OS to evict the page cache pages backing arr's mmap.

        This is advice, not an instruction: the kernel is free to ignore it,
        and some platforms and filesystems reject it outright. Losing the
        hint only costs memory, so a refusal is swallowed rather than raised
        at a caller who was merely reading an attribute.

        Parameters
        ----------
        - arr: np.ndarray
            The array whose backing pages are no longer needed. An array with
            no mapping behind it is a no-op.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: release the pages of a chunk that has been copied

            >>> AttrResolver._dontneed(chunk)

        """
        if (mm := AttrResolver._get_mmap(arr)) is not None:
            # AttributeError covers a Python built without madvise.
            with contextlib.suppress(AttributeError, OSError):
                mm.madvise(mmap.MADV_DONTNEED)

    @staticmethod
    def _copy_chunks(chunks: list[np.ndarray]) -> np.ndarray:
        """Pre-allocate result, copy one chunk at a time, evict each.

        np.concatenate would do the same job in one line, but it cannot hand
        anything back until it has finished, so once it returns every chunk it
        read is still resident in the page cache. Writing into a pre-allocated
        array instead allows each chunk to be released the moment it has been
        copied, which is what the loop below is for.

        The difference is not in what Python allocates -- both build the same
        result -- but in the resident memory of the mapped chunks: for 64 MB
        of mapped chunks, np.concatenate leaves about 128 MB resident (the
        result plus every chunk) against about 64 MB here (the result alone).

        Parameters
        ----------
        - chunks: list[np.ndarray]
            Ordered chunks, joined along the last axis. They share every
            other axis and their dtype, being pieces of one variable.

        Returns
        -------
        - np.ndarray
            The joined array, with the dtype and leading shape of the chunks.

        Examples
        --------
        - Example #1: join three chunks of a particle variable

            >>> AttrResolver._copy_chunks([chunk0, chunk1, chunk2])

        """
        # The chunks differ only along the last axis, so the result takes the
        # leading shape and the dtype of the first one.
        total = sum(c.shape[-1] for c in chunks)
        result = np.empty((*chunks[0].shape[:-1], total), dtype=chunks[0].dtype)

        # Copy each chunk into its slice and hand its pages back immediately,
        # rather than holding them all until the join is finished.
        pos = 0
        for chunk in chunks:
            n = chunk.shape[-1]
            result[..., pos : pos + n] = chunk
            AttrResolver._dontneed(chunk)
            pos += n
        return result
