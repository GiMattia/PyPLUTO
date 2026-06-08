"""The Load class loads the data (fluid) from the output files."""

from __future__ import annotations

# noqa: RUF100
import logging
import warnings
from collections.abc import Callable, Iterable
from typing import Generic, Literal, TypeVar, Unpack, cast, overload

import numpy as np

from pyPLUTO.baseloadmixin import BaseLoadMixin
from pyPLUTO.baseloadstate import BaseLoadState
from pyPLUTO.loadfuncs.initload import InitLoadManager
from pyPLUTO.loadkwargs import LoadPartKwargs, SpectrumKwargs
from pyPLUTO.toolfuncs.compute_units import UnitManager
from pyPLUTO.toolfuncs.parttools import PartToolsManager
from pyPLUTO.toolfuncs.set_units import SetUnitsManager
from pyPLUTO.utils.configure import set_text
from pyPLUTO.utils.inspector import track_kwargs
from pyPLUTO.utils.resolver import AttrResolver

logger = logging.getLogger(__name__)

_VarT = TypeVar("_VarT", bound="np.ndarray | dict[int, np.ndarray]")


class LoadPart(BaseLoadMixin[BaseLoadState], Generic[_VarT]):
    """Load the particles from the simulation.

    The class is used to load
    the particles from the simulation and store the data in the class
    attributes. The data are loaded in a memory mapped numpy
    multidimensional array. Such approach does not load the full data
    until needed. Basic operations (i.e. no numpy) are possible, as well
    as slicing the arrays, without fully loading the data. At the
    moment, only one output can be loaded at a time.

    Parameters
    ----------
    - datatype: str, default None
        The format of the data files to be loaded. If None, the code
        finds the format between dbl, flt and vtk.
    - endian: str | None, default None
        The endianess of the data files. If None, the code finds the
        endianess.
    - chnk: int | Sequence[int] | None, default None
        The chunk(s) to load. If None, all chunks are loaded. If a requested
        chunk does not exist for a given output, a ``UserWarning`` is issued and
        that output is skipped; for multi-output loads only the outputs that
        contain the requested chunk are returned.
    - nout: int | str | list | None, default 'last'
        The output number to be loaded. If 'last' the last output is loaded.
        If None, the data are not loaded.
    - path: str, default './'
        The path to the simulation directory.
    - text: bool | None, default None
        Controls output verbosity. None (default) prints standard load info at
        INFO level. False silences all output. True enables full DEBUG logging.
    - var: str | list | bool | None, default True
        The variables to be loaded. If True, all the variables are loaded.
        If None, the data are not loaded.

    Returns
    -------
    - None

    Examples
    --------
    - Example #1: Load the last output from the simulation

        >>> LoadPart()

    - Example #2: Load the last output from the simulation with a specific
        endianess

        >>> LoadPart(endian="big")

    - Example #3: Load the last output from the simulation with a specific
        set of variables

        >>> LoadPart(vars=["rho", "vx", "vy", "vz"])

    - Example #4: Load the last output from the simulation without printing
        the folder and the specific output loaded

        >>> LoadPart(0, text=False)

    - Example #5: Load the last output from the simulation without loading
        the data

        >>> LoadPart(nout=None)

    - Example #6: Load the last output from the simulation with a specific
        file number for the lp methods

        >>> LoadPart(nfile_lp=1)
    """

    @overload
    def __new__(
        cls,
        nout: int | None = ...,
        var: str | list[str] | bool | None = ...,
        **kwargs: Unpack[LoadPartKwargs],
    ) -> LoadPart[np.ndarray]: ...

    @overload
    def __new__(  # pyright: ignore[reportOverlappingOverload]
        cls,
        nout: list[int | str] | Literal["all"],
        var: str | list[str] | bool | None = ...,
        **kwargs: Unpack[LoadPartKwargs],
    ) -> LoadPart[dict[int, np.ndarray]]: ...

    @overload
    def __new__(
        cls,
        nout: str = ...,
        var: str | list[str] | bool | None = ...,
        **kwargs: Unpack[LoadPartKwargs],
    ) -> LoadPart[np.ndarray]: ...

    def __new__(
        cls, *_args: object, **_kwargs: object
    ) -> LoadPart[np.ndarray] | LoadPart[dict[int, np.ndarray]]:
        """Allocate a new LoadPart instance."""
        return cast(
            LoadPart[np.ndarray] | LoadPart[dict[int, np.ndarray]],
            super().__new__(cls),
        )

    @track_kwargs
    def __init__(
        self,
        nout: int | str | list[int | str] | None = "last",
        var: str | list[str] | bool | None = True,
        _check: bool = True,
        **kwargs: Unpack[LoadPartKwargs],
    ) -> None:
        """Initialize the LoadPart class."""
        self.state: BaseLoadState = BaseLoadState()
        self.cached_vars = set()
        self.state.text = kwargs.get("text", self.state.text)
        set_text(self.state.text)
        self.state.class_name = self.__class__.__name__
        if "nfile_lp" in kwargs:
            warnings.warn(
                "'nfile_lp' is deprecated, use 'chnk' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            kwargs.setdefault("chnk", kwargs.pop("nfile_lp"))
        self.state.chnk = kwargs.get("chnk")
        InitLoadManager(self.state, nout, var, _check=False, **kwargs)
        self.PartToolsManager = PartToolsManager(self.state)
        self.UnitManager = UnitManager(self.state)
        self.SetUnitsManager = SetUnitsManager(self.state)

        self.state.unit_userdef = kwargs.get("user_units", {}) or {}
        self.units = self.UnitManager._make_units_dict()
        self.unit_attached.clear()

        units = kwargs.get("units", False)
        skip_units = kwargs.get("skip_units")
        if units is not False:
            self.to_astropy_units(var=units, skip_units=skip_units)

        if self.state.text is not False:
            path = kwargs.get("path", self.state.pathdir)
            if isinstance(self.state.nout, (int, np.integer)):
                nout_out = self.state.nout
            else:
                nout_out = np.atleast_1d(self.state.nout).astype(int).tolist()
            logger.info("Load: folder %s,     output %s", path, nout_out)

    def __repr__(self) -> str:
        """Return the repr of the LoadPart class."""
        return (
            f"LoadPart(nout={self.state.nout!r}, path={self.state.pathdir!r})"
        )

    def __str__(self) -> str:
        """Return the string representation of the LoadPart class."""
        text = f"""
        LoadPart class.
        It loads the particles.

        File properties:
        - Simulation path     (pathdir)      {self.state.pathdir}
        - File format         (datatype)     {self.state.datatype}

        Simulation properties
        - N. particles in loaded output (nshp)  {self.state.nshp}
        - Loaded output index/indices (nout)    {self.state.nout}
        - Loaded simulation time(s) (ntime)     {self.state.ntime}

        Variables loaded:
        {list(self.state.d_vars.keys())}

        Public methods available:

        - select
        - spectrum

        Please refrain from using "private" methods and attributes.
        """
        return text

    def __getattr__(self, name: str) -> _VarT:
        """Get the attribute of the Load class."""
        val = getattr(self.state, name)
        return cast("_VarT", AttrResolver.resolve(self.state, name, val))

    def __setattr__(self, name: str, value: object) -> None:
        """Set the attribute of the Load class."""
        if name == "state" or not hasattr(self, "state"):
            return super().__setattr__(name, value)
        return setattr(self.state, name, value)

    def select(
        self,
        var: np.ndarray,
        cond: str | Callable,
        sort: bool = False,
        ascending: bool = True,
    ) -> np.ndarray:
        """Select method."""
        return self.PartToolsManager.select(var, cond, sort, ascending)

    select.__doc__ = PartToolsManager.select.__doc__

    def spectrum(
        self,
        var: np.ndarray,
        scale: str = "lin",
        vmin: float | None = None,
        vmax: float | None = None,
        _check: bool = True,
        **kwargs: Unpack[SpectrumKwargs],
    ) -> tuple[np.ndarray, np.ndarray]:
        """Spectrum method."""
        return self.PartToolsManager.spectrum(
            var,
            scale,
            vmin,
            vmax,
            _check=_check,
            **kwargs,
        )

    spectrum.__doc__ = PartToolsManager.spectrum.__doc__

    def to_astropy_units(
        self,
        var: str | Iterable[str] | bool | None = None,
        skip_units: str | Iterable[str] | None = None,
    ) -> None:
        """To astropy units method."""
        return self.SetUnitsManager.to_astropy_units(var, skip_units)

    to_astropy_units.__doc__ = SetUnitsManager.to_astropy_units.__doc__

    def to_code_units(
        self,
        var: str | Iterable[str] | bool | None = None,
        skip_units: str | Iterable[str] | None = None,
    ) -> None:
        """To code units method."""
        return self.SetUnitsManager.to_code_units(var, skip_units)

    to_code_units.__doc__ = SetUnitsManager.to_code_units.__doc__
