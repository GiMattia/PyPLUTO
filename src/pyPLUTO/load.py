"""The Load class loads the data (fluid) from the output files.

Load is a facade: it implements almost nothing itself. It builds the state,
builds a manager for each family of operations on that same state, and then
every public method is two lines handing the call to the manager that does
the work. `pyPLUTO/template.py` describes the pattern and why it is used.

Reading this file is therefore mostly reading the class docstring, which is
the user-facing documentation of every keyword, and the four pieces of
machinery that are not delegation: the `__new__` overloads that decide what
type a load is, the constructor, and the two attribute hooks that make
`Data.rho` work.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Generic, Literal, TypeVar, Unpack, cast, overload

import numpy as np

from pyPLUTO.loadfuncs.initload import InitLoadManager
from pyPLUTO.loadfuncs.read_files import ReadFilesManager
from pyPLUTO.loadfuncs.readdefplini import FiledefpliniManager
from pyPLUTO.loadfuncs.write_files import WriteFilesManager
from pyPLUTO.loadkwargs import (
    CartesianVectorKwargs,
    FindContourKwargs,
    FindFieldlinesKwargs,
    FourierKwargs,
    LoadKwargs,
    ReadFileKwargs,
    ReshapeKwargs,
    SlicesKwargs,
    WriteFileKwargs,
)
from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState
from pyPLUTO.toolfuncs.compute_units import UnitManager
from pyPLUTO.toolfuncs.findlines import FindLinesManager
from pyPLUTO.toolfuncs.fourier import FourierManager
from pyPLUTO.toolfuncs.nabla import NablaManager
from pyPLUTO.toolfuncs.set_units import SetUnitsManager
from pyPLUTO.toolfuncs.transform import TransformManager
from pyPLUTO.utils.configure import set_text
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
        Whether to read the definitions header file. If True, the code will
        look for definitions.h (or .hpp) in the simulation folder. If False,
        the code will not attempt to read it. A string is currently accepted
        and ignored: the file is looked for by name in the folder either way.
    - endian: str | None, default None
        Endianess of the datafiles. Should be used only if specific
        architectures are used, since the code computes it by itself. Valid
        values are 'big' and 'little' (or '<' and '>').
    - full3D: bool, default False
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
    - skip_units: str | list[str] | None, default None
        The variables that keep plain arrays when units are attached. Has no
        effect unless 'units' is given.
    - text: bool | None, default None
        Controls output verbosity. None (default) prints standard load info at
        INFO level. False silences all output. True enables full DEBUG logging.
    - units: bool | str | list[str] | None, default None
        The variables that are converted to astropy units while loading. True
        converts every variable, a name or a list of names only those.
    - user_units: dict[str, float] | None, default None
        Unit scales given by the user, e.g. {'unit_density': 1.0}, taking
        precedence over the ones read from the simulation.
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

    # The three overloads exist to tell the type checkers what a variable of
    # this load will be. Asking for one output gives arrays, asking for
    # several gives a dict of arrays keyed by output number, so `D.rho` has a
    # different type depending on the nout that was passed. The overloads let
    # that be known from the call rather than discovered at runtime; only the
    # signatures are read, the last definition is the one that runs.
    @overload
    def __new__(
        cls,
        nout: int | None = ...,
        var: str | list[str] | bool | None = ...,
        **kwargs: Unpack[LoadKwargs],
    ) -> Load[np.ndarray]: ...

    @overload
    def __new__(  # pyright: ignore[reportOverlappingOverload]
        cls,
        nout: list[int | str] | Literal["all"],
        var: str | list[str] | bool | None = ...,
        **kwargs: Unpack[LoadKwargs],
    ) -> Load[dict[int, np.ndarray]]: ...

    @overload
    def __new__(
        cls,
        nout: str = ...,
        var: str | list[str] | bool | None = ...,
        **kwargs: Unpack[LoadKwargs],
    ) -> Load[np.ndarray]: ...

    def __new__(
        cls, *_args: object, **_kwargs: object
    ) -> Load[np.ndarray] | Load[dict[int, np.ndarray]]:
        """Allocate a new Load instance."""
        return cast(
            "Load[np.ndarray] | Load[dict[int, np.ndarray]]",
            super().__new__(cls),
        )

    @track_kwargs
    def __init__(
        self,
        nout: int | str | list[int | str] | None = "last",
        var: str | list[str] | bool | None = True,
        _check: bool = True,
        **kwargs: Unpack[LoadKwargs],
    ) -> None:
        """Initialize the Load class."""
        # The state comes first and everything else is built on it. Note it is
        # assigned through the name "state", which __setattr__ below treats as
        # the one exception to its forwarding: without that, this line would
        # try to store the state inside a state that does not exist yet.
        self.state: LoadState = LoadState()

        # Verbosity is settled before anything can log.
        self.state.text = kwargs.get("text", self.state.text)
        set_text(self.state.text)
        self.state.class_name = self.__class__.__name__
        self.state.full3D = kwargs.get("full3D", self.state.full3D)
        self.state.level = kwargs.get("level", self.state.level)

        # The reading happens here: these two fill the state with the grid,
        # the variables and the metadata. _check=False because this call is
        # not the outermost one -- __init__ is, and it judges the keywords.
        InitLoadManager(self.state, nout, var, _check=False, **kwargs)
        FiledefpliniManager(self.state, kwargs.get("defh"), kwargs.get("plini"))

        # Every manager is given the same state object, which is how a result
        # written by one is visible to all the others.
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

    def __repr__(self) -> str:
        """Return the repr of the Load class."""
        return (
            f"Load(nout={self.state.nout!r}, "
            f"path={self.state.pathdir!r}, "
            f"geom={self.state.geom!r})"
        )

    def __str__(self) -> str:
        """Return the string representation of the Load class."""
        text3 = f"        - Projections {['x1c', 'x2c', 'x1rc', 'x2rc']}\n"
        text3 = text3 if self.geom != "CARTESIAN" else ""

        text = f"""
        Load class.
        It loads the data.

        File properties:
        - Current path loaded (pathdir)      {self.state.pathdir}
        - Format loaded       (datatype)     {self.state.datatype}

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

        - cartesian_vector
        - curl
        - divergence
        - find_contour
        - find_fieldlines
        - fourier
        - gradient
        - mirror
        - read_file
        - reshape_cartesian
        - reshape_uniform
        - slices
        - to_astropy_units
        - to_code_units
        - write_file

        Please refrain from using "private" methods and attributes.
        """
        return text

    def __getattr__(self, name: str) -> _VarT:
        """Get the attribute of the Load class.

        Called only for names Python could not find the usual way, so the
        fields with a property on LoadMixin never reach here: this is the
        path for the loaded variables, whose names come from the simulation
        and cannot be declared in advance.

        The value goes through AttrResolver, which is what turns a
        memory-mapped window into an array the state owns, once, on the first
        access. See `utils/resolver.py`.
        """
        val = getattr(self.state, name)
        return cast("_VarT", AttrResolver.resolve(self.state, name, val))

    def __setattr__(self, name: str, value: object) -> None:
        """Set the attribute of the Load class.

        Every assignment is forwarded to the state, so `D.rho = ...` and a
        user's own `D.my_var = ...` are stored in the one place the managers
        read from.

        Two exceptions, both in the first line: the state itself, which has to
        live on the Load, and anything assigned before the state exists, which
        is what makes the first line of __init__ possible.
        """
        if name == "state" or not hasattr(self, "state"):
            return super().__setattr__(name, value)
        return setattr(self.state, name, value)

    def write_file(
        self,
        data: np.ndarray | dict,
        filename: str,
        datatype: str | None = None,
        dataname: str | None = None,
        grid: bool = False,
        _check: bool = True,
        **kwargs: Unpack[WriteFileKwargs],
    ) -> None:
        """Write file method."""
        return self.WriteFileManager.write_file(
            data,
            filename,
            datatype,
            dataname,
            grid,
            _check=_check,
            **kwargs,
        )

    # Every method below follows this shape: a one-line placeholder docstring,
    # a body that forwards to the manager, and this line copying the manager's
    # full documentation onto the facade method. Without the copy, `help(D.
    # write_file)` would show the placeholder instead of the real thing.
    write_file.__doc__ = WriteFilesManager.write_file.__doc__

    def read_file(
        self,
        filename: str,
        datatype: str | None = None,
        _check: bool = True,
        **kwargs: Unpack[ReadFileKwargs],
    ) -> dict[str, np.ndarray]:
        """Read file method."""
        return self.ReadFileManager.read_file(
            filename,
            datatype,
            _check=_check,
            **kwargs,
        )

    read_file.__doc__ = ReadFilesManager.read_file.__doc__

    def gradient(
        self,
        var: np.ndarray,
        x1slice: float | None = None,
        x2slice: float | None = None,
        x3slice: float | None = None,
        edge_order: int = 2,
    ) -> np.ndarray:
        """Gradient method."""
        return self.NablaManager.gradient(
            var,
            x1slice,
            x2slice,
            x3slice,
            edge_order,
        )

    gradient.__doc__ = NablaManager.gradient.__doc__

    def divergence(
        self,
        v1: np.ndarray | None = None,
        v2: np.ndarray | None = None,
        v3: np.ndarray | None = None,
        x1slice: float | None = None,
        x2slice: float | None = None,
        x3slice: float | None = None,
        edge_order: int = 2,
    ) -> np.ndarray:
        """Divergence method."""
        return self.NablaManager.divergence(
            v1,
            v2,
            v3,
            x1slice,
            x2slice,
            x3slice,
            edge_order,
        )

    divergence.__doc__ = NablaManager.divergence.__doc__

    def curl(
        self,
        v1: np.ndarray | None = None,
        v2: np.ndarray | None = None,
        v3: np.ndarray | None = None,
        x1slice: float | None = None,
        x2slice: float | None = None,
        x3slice: float | None = None,
        edge_order: int = 2,
    ) -> np.ndarray:
        """Curl method."""
        return self.NablaManager.curl(
            v1,
            v2,
            v3,
            x1slice,
            x2slice,
            x3slice,
            edge_order,
        )

    curl.__doc__ = NablaManager.curl.__doc__

    def fourier(
        self,
        f: np.ndarray,
        _check: bool = True,
        **kwargs: Unpack[FourierKwargs],
    ) -> tuple[list[np.ndarray], np.ndarray]:
        """Fourier method."""
        return self.FourierManager.fourier(f, _check=_check, **kwargs)

    fourier.__doc__ = FourierManager.fourier.__doc__

    def slices(
        self,
        var: np.ndarray,
        diag: bool | str | None = None,
        x1: int | list | None = None,
        x2: int | list | None = None,
        x3: int | list | None = None,
        _check: bool = True,
        **kwargs: Unpack[SlicesKwargs],
    ) -> np.ndarray:
        """Slices method."""
        return self.TransformManager.slices(
            var,
            diag,
            x1,
            x2,
            x3,
            _check=_check,
            **kwargs,
        )

    slices.__doc__ = TransformManager.slices.__doc__

    def mirror(
        self,
        var: np.ndarray,
        dirs: str | list = "l",
        xax: np.ndarray | None = None,
        yax: np.ndarray | None = None,
    ) -> list[np.ndarray]:
        """Mirror method."""
        return self.TransformManager.mirror(var, dirs, xax, yax)

    mirror.__doc__ = TransformManager.mirror.__doc__

    def repeat(
        self,
        var: np.ndarray,
        dirs: str | list,
        xax: np.ndarray | None = None,
        yax: np.ndarray | None = None,
    ) -> np.ndarray:
        """Repeat method."""
        return self.TransformManager.repeat(var, dirs, xax, yax)

    repeat.__doc__ = TransformManager.repeat.__doc__

    def cartesian_vector(
        self,
        var: str | None = None,
        _check: bool = True,
        **kwargs: Unpack[CartesianVectorKwargs],
    ) -> tuple[np.ndarray, ...]:
        """Cartesian vector method."""
        return self.TransformManager.cartesian_vector(
            var,
            _check=_check,
            **kwargs,
        )

    cartesian_vector.__doc__ = TransformManager.cartesian_vector.__doc__

    def reshape_cartesian(
        self,
        var1: np.ndarray,
        var2: np.ndarray | None = None,
        var3: np.ndarray | None = None,
        _check: bool = True,
        **kwargs: Unpack[ReshapeKwargs],
    ) -> tuple[np.ndarray, ...]:
        """Reshape cartesian method."""
        return self.TransformManager.reshape_cartesian(
            var1,
            var2,
            var3,
            _check=_check,
            **kwargs,
        )

    reshape_cartesian.__doc__ = TransformManager.reshape_cartesian.__doc__

    def reshape_uniform(
        self,
        var1: np.ndarray,
        var2: np.ndarray | None = None,
        var3: np.ndarray | None = None,
        _check: bool = True,
        **kwargs: Unpack[ReshapeKwargs],
    ) -> tuple[np.ndarray, np.ndarray, list[np.ndarray]]:
        """Reshape uniform method."""
        return self.TransformManager.reshape_uniform(
            var1,
            var2,
            var3,
            _check=_check,
            **kwargs,
        )

    reshape_uniform.__doc__ = TransformManager.reshape_uniform.__doc__

    def find_fieldlines(
        self,
        var1: str | np.ndarray,
        var2: str | np.ndarray,
        x0: list | float | None = None,
        y0: list | float | None = None,
        x1: np.ndarray | None = None,
        x2: np.ndarray | None = None,
        text: bool = False,
        _check: bool = True,
        **kwargs: Unpack[FindFieldlinesKwargs],
    ) -> list:
        """Find fieldlines method."""
        return self.FindLinesManager.find_fieldlines(
            var1,
            var2,
            x0,
            y0,
            x1,
            x2,
            text,
            _check=_check,
            **kwargs,
        )

    find_fieldlines.__doc__ = FindLinesManager.find_fieldlines.__doc__

    def find_contour(
        self,
        var: str | np.ndarray,
        _check: bool = True,
        **kwargs: Unpack[FindContourKwargs],
    ) -> list:
        """Find contour method."""
        return self.FindLinesManager.find_contour(var, _check=_check, **kwargs)

    find_contour.__doc__ = FindLinesManager.find_contour.__doc__

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
