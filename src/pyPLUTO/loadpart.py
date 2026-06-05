"""The Load class loads the data (fluid) from the output files."""

# ruff: noqa: ANN201  # noqa: RUF100

from typing import Any

import numpy as np

from pyPLUTO.baseloadmixin import BaseLoadMixin
from pyPLUTO.baseloadstate import BaseLoadState
from pyPLUTO.loadfuncs.initload import InitLoadManager
from pyPLUTO.toolfuncs.compute_units import UnitManager
from pyPLUTO.toolfuncs.parttools import PartToolsManager
from pyPLUTO.toolfuncs.set_units import SetUnitsManager
from pyPLUTO.utils.inspector import track_kwargs
from pyPLUTO.utils.resolver import AttrResolver


class LoadPart(BaseLoadMixin):
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
    - nfile_lp: int | None, default None
        The file number for the lp methods. If None, the code finds the
        file number.
    - nout: int | str | list | None, default 'last'
        The output number to be loaded. If 'last' the last output is loaded.
        If None, the data are not loaded.
    - path: str, default './'
        The path to the simulation directory.
    - text: bool, default True
        If True, the folder and output are printed.
        In case the user needs a more detailed information of the structure
        and attributes loaded from the class, the __str__ method provides a
        easy display of all the important information.
    - vars: str | list | bool | None, default True
        The variables to be loaded. If True, all the variables are loaded.
        If None, the data are not loaded.

    Returns
    -------
    - None

    ----

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

    @track_kwargs
    def __init__(
        self,
        nout: int | str | list[int | str] | None = "last",
        var: str | list[str] | bool | None = True,
        check: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize the Load class."""
        kwargs.pop("kwargscheck", check)

        self.state: BaseLoadState = BaseLoadState()
        self.cached_vars = set()
        self.state.text = kwargs.get("text", self.state.text)
        self.state.class_name = self.__class__.__name__
        InitLoadManager(self.state, nout, var, **kwargs)
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
                nout_out = int(self.state.nout)
            else:
                nout_out = np.atleast_1d(self.state.nout).astype(int).tolist()
            print(f"Load: folder {path},     output {nout_out}")

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

    def __getattr__(self, name: str):  # noqa: ANN204
        """Get the attribute of the Load class."""
        val = getattr(self.state, name)
        return AttrResolver.resolve(self.state, name, val)

    def __setattr__(self, name: str, value: object) -> None:
        """Set the attribute of the Load class."""
        if name == "state" or not hasattr(self, "state"):
            return super().__setattr__(name, value)
        return setattr(self.state, name, value)

    @property
    def select(self):
        """Proxy to particle selection manager."""
        return self.PartToolsManager.select

    @property
    def spectrum(self):
        """Proxy to particle spectrum manager."""
        return self.PartToolsManager.spectrum

    @property
    def to_astropy_units(self):
        """Property for the to_astropy_units method."""
        return self.SetUnitsManager.to_astropy_units

    @property
    def to_code_units(self):
        """Property for the to_code_units method."""
        return self.SetUnitsManager.to_code_units
