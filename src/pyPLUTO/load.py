"""The Load class loads the data (fluid) from the output files."""

from __future__ import annotations

# ruff: noqa: ANN201
import logging
from typing import Any, Generic, TypeVar, Unpack, cast, overload

import numpy as np

from pyPLUTO.configure import set_text
from pyPLUTO.loadfuncs.initload import InitLoadManager
from pyPLUTO.loadfuncs.read_files import ReadFilesManager
from pyPLUTO.loadfuncs.readdefplini import FiledefpliniManager
from pyPLUTO.loadfuncs.write_files import WriteFilesManager
from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState
from pyPLUTO.toolfuncs.compute_units import UnitManager
from pyPLUTO.toolfuncs.findlines import FindLinesManager
from pyPLUTO.toolfuncs.fourier import FourierManager
from pyPLUTO.toolfuncs.nabla import NablaManager
from pyPLUTO.toolfuncs.set_units import SetUnitsManager
from pyPLUTO.toolfuncs.transform import TransformManager
from pyPLUTO.utils.annotator import AllKwargs
from pyPLUTO.utils.inspector import track_kwargs
from pyPLUTO.utils.resolver import AttrResolver

logger = logging.getLogger(__name__)

_VarT = TypeVar("_VarT", bound="np.ndarray | dict[int, np.ndarray]")


class Load(LoadMixin, Generic[_VarT]):
    """The Load class loads the data (fluid) from the output files.

    The initialization corresponds to the loading, if wanted, of one or more
    datafiles for the fluid. The data are loaded in a memory mapped numpy
    multidimensional array. Such approach does not load the full data
    until needed. Basic operations (i.e. no numpy) are possible, as well
    as slicing the arrays, without fully loading the data.

    Parameters
    ----------
    - alone: bool | None, default False
        If the files are standalone. If False, the code will look for the
        grid file in the folder. If True, the code will look for the grid
        information within the data files. Should be used only for non-binary
        files.
    - code: str | None, default None
        The code from which the data are loaded. If None, the code assumes
        PLUTO/gPLUTO. If a different code is provided, the corresponding
        loading method is used (if implemented).
    - datatype: str | None, default None
        The format of the data file. If not specified, the code will look for
        the format from the list of possible formats. HDF5 (AMR) formats have
        not been implemented yet.
    - defh: bool | str | None, default None
        The path to the definitions header file. If True, the code will look for
        the default definitions header file. If a string is provided, it will be
        used as the path to the definitions header file. If False, the code will
        not attempt to read the definitions header file.
    - endian: str | None, default None
        Endianess of the datafiles. Should be used only if specific
        architectures are used, since the code computes it by itself. Valid
        values are 'big' and 'little' (or '<' and '>').
    - full3d: bool, default True
        If disabled, the 3D meshgrids for the grid in non-cartesian coordinates
        are not used. Instead, a combination of an external loop and2D meshgrid
        is employed. The aim is to allow for cartesian meshes from non-cartesian
        geometries without saturating the computer memory (suited for laptops).
    - level: int, default 0
        The refinement level of the grid. Should be used only if the grid is
        refined through AMR.
    - multiple: bool, default False
        If the files are multiple. If False, the code will look for the single
        files, otherwise for the multiple files each corresponding to the loaded
        variables. Should be used only if both single files and multiple files
        are present in the same format for the same datatype.
    - nout: int | str | list | None, default 'last'
        The files to be loaded. Possible choices are int values (which
        correspond to the number of the output file), strings ('last', which
        corresponds to the last file, 'all', which corresponds to all files) or
        a list of the aforementioned types. Note that the 'all' value should be
        used carefully, e.g. only when the data need to be shown interactively.
    - path: str, default './'
        The path of the folder where the files should be loaded.
    - plini: bool | str | None, default None
        The path to the pluto.ini file. If True, the code will look for the
        default pluto.ini file. If a string is provided, it will be used as the
        path to the pluto.ini file. If False, the code will not attempt to read
        the pluto.ini file.
    - text: bool, default True
        If True, the folder and output are printed. In case the user needs a
        more detailed information of the structure and attributes loaded from
        the class, the __str__ method provides a easy display of all the
        important information.
    - var: str | list[str] | bool | None, default True
        The variables to be loaded. The default value, True, corresponds to all
        the variables.

    Returns
    -------
    - None

    Examples
    --------
    - Example #1: Load the data from the default folder and output

        >>> D = pp.Load()
        Loading folder ./,     output [0]

    - Example #2: Load the data from the default folder but output 0

        >>> D = pp.Load(nout=0)
        Loading folder ./,     output [0]

    - Example #3: Load the data from the default folder but last output is
        specified

        >>> D = pp.Load(nout="last")
        Loading folder ./,     output [1]

    - Example #4: Load the data from the default folder and all outputs

        >>> D = pp.Load(nout="all")
        Loading folder ./,     output [0, 1, 2, 3, 4]

    - Example #5: Load the data from the default folder and multiple
        selected outputs

        >>> D = pp.Load(nout=[0, 1, 2])
        Loading folder ./,     output [0, 1, 2]

    - Example #6: Load the data from the default folder and multiple selected
        outputs and variables

        >>> D = pp.Load(nout=[0, 1, 2], var=["rho", "vel1"])
        Loading folder ./,     output [0, 1, 2]

    - Example #7: Load the data from the default folder, multiple selected
        outputs and variables, without text

        >>> D = pp.Load(nout=[0, 1, 2], vars=["rho", "vel1"], text=False)

    - Example #8: Load the data from the default format with selected output
        and format

        >>> D = pp.Load(data="vtk", nout=0)
        Loading folder ./,     output [0]

    - Example #9: Load the data from the default folder with selected output,
        variables and format

        >>> D = pp.Load(data="vtk", nout=0, vars=["rho", "vel1"])
        Loading folder ./,     output [0]

    - Example #10: Load the data from a specific folder with selected output

        >>> D = pp.Load(path="./data/", nout=0)
        Loading folder ./data/,     output [0]

    """

    @overload
    def __new__(
        cls,
        nout: int | None = ...,
        var: str | list[str] | bool | None = ...,
        _check: bool = ...,
        **kwargs: Unpack[AllKwargs],
    ) -> Load[np.ndarray]: ...

    @overload
    def __new__(
        cls,
        nout: list[int | str],
        var: str | list[str] | bool | None = ...,
        _check: bool = ...,
        **kwargs: Unpack[AllKwargs],
    ) -> Load[dict[int, np.ndarray]]: ...

    @overload
    def __new__(
        cls,
        nout: str = ...,
        var: str | list[str] | bool | None = ...,
        _check: bool = ...,
        **kwargs: Unpack[AllKwargs],
    ) -> Load[np.ndarray] | Load[dict[int, np.ndarray]]: ...

    def __new__(cls, *_args: Any, **_kwargs: Any) -> Load[Any]:
        """Allocate a new Load instance."""
        return super().__new__(cls)

    @track_kwargs
    def __init__(
        self,
        nout: int | str | list[int | str] | None = "last",
        var: str | list[str] | bool | None = True,
        _check: bool = True,
        **kwargs: Unpack[AllKwargs],
    ) -> None:
        """Initialize the Load class."""
        self.state: LoadState = LoadState()
        self.state.text = kwargs.get("text", self.state.text)
        set_text(self.state.text)
        self.state.class_name = self.__class__.__name__
        self.state.full3D = kwargs.get("full3D", self.state.full3D)
        self.state.level = kwargs.get("level", self.state.level)
        InitLoadManager(self.state, nout, var, _check=False, **kwargs)
        FiledefpliniManager(self.state, kwargs.get("defh"), kwargs.get("plini"))

        self.ReadFileManager = ReadFilesManager(self.state)
        self.WriteFileManager = WriteFilesManager(self.state)
        self.FindLinesManager = FindLinesManager(self.state)
        self.FourierManager = FourierManager(self.state)
        self.NablaManager = NablaManager(self.state)
        self.TransformManager = TransformManager(self.state)
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
            if hasattr(self.state, "nout"):
                if isinstance(self.state.nout, (int, np.integer)):
                    nout_out = self.state.nout
                else:
                    nout_out = (
                        np.atleast_1d(self.state.nout).astype(int).tolist()
                    )
            else:
                nout_out = None
            logger.info("Load: folder %s,     output %s", path, nout_out)

    def __str__(self) -> str:
        """Return the string representation of the Load class."""
        text3 = f"        - Projections {['x1c', 'x2c', 'x1rc', 'x2rc']}\n"
        text3 = text3 if self.geom != "CARTESIAN" else ""

        text = f"""
        Load class.
        It loads the data.

        File properties:
        - Current path loaded (pathdir)      {self.state.pathdir}
        - Format loaded       (format)       {self.state.datatype}

        Simulation properties
        - Dimensions    (dim)      {self.state.dim}
        - Geometry      (geom)     {self.state.geom}
        - Grid size     (gridsize) {self.state.gridsize}
        - Grid shape    (nshp)     {self.state.nshp}
        - Output loaded (nout)     {self.state.nout}
        - Time loaded   (ntime)    {self.state.ntime}

        Public attributes available:
        - Number of cells in each direction {["nx1", "nx2", "nx3"]}
        - Grid values (cell center)         {["x1", "x2", "x3"]}
        - Grid values (face center)         {["x1r", "x2r", "x3r"]}
        - Cells size                        {["dx1", "dx2", "dx3"]}
        - Time attributes                   {["outlist", "timelist"]}\n{text3}
        Variables available:
        {self.state.d_info["varslist"][0]}
        Variables loaded:
        {list(self.state.d_vars.keys())}

        Public methods available:

        - slices
        - cartesian_vector
        - reshape_cartesian
        - write_file
        - fourier
        - nabla
        - find_contour
        - find_fieldlines
        - vector_field

        Please refrain from using "private" methods and attributes.
        """
        return text

    def __getattr__(self, name: str) -> _VarT:
        """Get the attribute of the Load class."""
        val = getattr(self.state, name)
        return cast(_VarT, AttrResolver.resolve(self.state, name, val))

    def __setattr__(self, name: str, value: object) -> None:
        """Set the attribute of the Load class."""
        if name == "state" or not hasattr(self, "state"):
            return super().__setattr__(name, value)
        return setattr(self.state, name, value)

    @property
    def write_file(self):
        """Property for the write_file method."""
        return self.WriteFileManager.write_file

    @property
    def read_file(self):
        """Property for the read_file method."""
        return self.ReadFileManager.read_file

    @property
    def gradient(self):
        """Property for the gradient method."""
        return self.NablaManager.gradient

    @property
    def divergence(self):
        """Property for the divergence method."""
        return self.NablaManager.divergence

    @property
    def curl(self):
        """Property for the curl method."""
        return self.NablaManager.curl

    @property
    def fourier(self):
        """Property for the fourier method."""
        return self.FourierManager.fourier

    @property
    def slices(self):
        """Property for the slices method."""
        return self.TransformManager.slices

    @property
    def mirror(self):
        """Property for the mirror method."""
        return self.TransformManager.mirror

    @property
    def repeat(self):
        """Property for the repeat method."""
        return self.TransformManager.repeat

    @property
    def cartesian_vector(self):
        """Property for the cartesian_vector method."""
        return self.TransformManager.cartesian_vector

    @property
    def reshape_cartesian(self):
        """Property for the reshape_cartesian method."""
        return self.TransformManager.reshape_cartesian

    @property
    def reshape_uniform(self):
        """Property for the reshape_uniform method."""
        return self.TransformManager.reshape_uniform

    @property
    def find_fieldlines(self):
        """Property for the find_fieldlines method."""
        return self.FindLinesManager.find_fieldlines

    @property
    def find_contour(self):
        """Property for the find_contour method."""
        return self.FindLinesManager.find_contour

    @property
    def to_astropy_units(self):
        """Property for the to_astropy_units method."""
        return self.SetUnitsManager.to_astropy_units

    @property
    def to_code_units(self):
        """Property for the to_code_units method."""
        return self.SetUnitsManager.to_code_units
