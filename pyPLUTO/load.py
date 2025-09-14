from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .h_pypluto import check_par


class Load:
    """The Load class loads the data (fluid) from the output files. The
    initialization corresponds to the loading, if wanted, of one or more
    datafiles for the fluid. The data are loaded in a memory mapped numpy
    multidimensional array. Such approach does not load the full data
    until needed. Basic operations (i.e. no numpy) are possible, as well
    as slicing the arrays, without fully loading the data.

    Returns
    -------
    - None

    Parameters
    ----------
    - alone: bool | None, default False
        If the files are standalone. If False, the code will look for the
        grid file in the folder. If True, the code will look for the grid
        information within the data files. Should be used only for non-binary
        files.
    - datatype: str | None, default None
        The format of the data file. If not specified, the code will look for
        the format from the list of possible formats. HDF5 (AMR) formats have
        not been implemented yet.
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
    - text: bool, default True
        If True, the folder and output are printed. In case the user needs a
        more detailed information of the structure and attributes loaded from
        the class, the __str__ method provides a easy display of all the
        important information.
    - vars: str | list | bool | None, default True
        The variables to be loaded. The default value, True, corresponds to all
        the variables.

    ----

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

        >>> D = pp.Load(nout=[0, 1, 2], vars=["rho", "vel1"])
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

    def __init__(
        self,
        nout: int | str | list[int | str] | None = "last",
        path: str | Path = "./",
        datatype: str | None = None,
        vars: str | list[str] | bool | None = True,
        text: bool = True,
        check: bool = True,
        **kwargs: Any,
    ) -> None:
        # Check parameters
        param = {
            "alone",
            "read_defh",
            "endian",
            "full3d",
            "level",
            "multiple",
            "fastvtk",
        }
        if check is True:
            check_par(param, "__init__", **kwargs)

        self.nout: NDArray  # Output to be loaded

        # Load PyPLUTO for different codes
        code = kwargs.get("code")
        codedict = {"echo": self.echo_load}
        # If not code is provided (or the code is PLUTO/gPLUTO) just skip
        if not code or code.lower() in {"pluto", "gpluto"}:
            pass
        elif code.lower() in codedict:
            init = f"Creating instance with alternate method using code: {code}"
            if text is True:
                print(init)
            codedict[code.lower()](nout, path, vars)
            self.nout = self.nout.astype(int)
            if text is True:
                print(f"Load: folder {path},     output {self.nout}")
            return
        else:
            raise NotImplementedError(f"{code} loading is not implemented!")

        # Check if the user wants to load the data
        if nout is None:
            return

        # Initialization or declaration of variables (used in this file)
        self._d_end: dict[str | None, str | None]  # Endianess dictionary
        self._multiple: bool  # Bool for single or multiple files
        self._alone: bool | None = None  # Bool for standalone files
        self._info: bool = True  # Bool for info (linked to alone)
        self._d_vars: dict = {}  # The dictionary of variables
        self.level: int = kwargs.get("level", 0)  # The level for AMR files

        # Initialization or declaration of variables (used in other files)
        self.pathdir: Path  # Path to the simulation directory
        self.format: str | None = None  # The format of the files to be loaded
        self.outlist: NDArray  # The list of outputs to be loaded
        self.timelist: NDArray  # The list of times to be loaded
        self.ntime: NDArray  # The time array
        self.set_vars: set[str]  # The set of variables to be loaded
        self.set_outs: set[int]  # The set of outputs to be loaded
        self.geom: str  # The geometry of the simulation
        self.dim: int  # The dimension of the simulation
        self.nshp: int | tuple[int, ...]  # The shape of the grid
        self.nfile_lp: int | None = None  # File number for the lp methods

        self._charsize: int  # The data size in the files
        self._lennout: int  # The number of outputs to be loaded
        self._d_info: dict[str, Any]  # Info dictionary
        self._matching_files: list[str]  # The list of files to be loaded
        self._pathgrid: Path  # Path to the grid file
        self._pathdata: Path | None = (
            None  # Path to the data files to be loaded
        )
        self._filepath: Path  # The filepath to be loaded
        self._load_vars: list[str]  # The list of variables to be loaded
        self._offset: dict[str, int]  # The offset of the variables
        self._shape: dict[str, tuple[int, ...]]  # The shape of the variables
        self._vardim: list[int]  # The dimension of the variables
        self._dictdim: dict  # The dictionary of dimensions
        self._fastvtk: bool = kwargs.get(
            "fastvtk", True
        )  # Bool for fast vtk loading

        # Declaration of the grid variables
        self.x1: NDArray
        self.x2: NDArray
        self.x3: NDArray  # centered grid
        self.x1r: NDArray
        self.x2r: NDArray
        self.x3r: NDArray  # staggered grid
        self.x1c: NDArray
        self.x2c: NDArray  # cartesian centered grid
        self.x1rc: NDArray
        self.x2rc: NDArray  # cartesian staggered grid
        self.dx1: NDArray
        self.dx2: NDArray
        self.dx3: NDArray  # cell size
        self.nx1: int
        self.nx2: int
        self.nx3: int  # number of cells
        self.gridsize: int  # total number of cells
        self.gridlist3: list[str]
        self.x1p: NDArray
        self.x2p: NDArray
        self.x1rp: NDArray
        self.x2rp: NDArray

        self._gridsize_st1: int
        self._nshp_st1: NDArray
        self._gridsize_st2: int
        self._nshp_st2: NDArray
        self._gridsize_st3: int
        self._nshp_st3: NDArray
        self._full3d: bool = kwargs.get("full3d", False)

        _nout_out: int | list[int]  # Output to be printed

        # Check the input endianess
        self._d_end = {
            "big": ">",
            "little": "<",
            ">": ">",
            "<": "<",
            None: None,
        }

        if (endian := kwargs.get("endian")) not in self._d_end.keys():
            error = f"Invalid endianess. Valid values are {self._d_end.keys()}"
            raise ValueError(error)

        # Check the input multiple
        multiple = kwargs.get("multiple", False)
        if not isinstance(multiple, bool):
            raise TypeError("Invalid data type. 'multiple' must be a boolean.")
        else:
            self._multiple = multiple

        # Check if the path is an existing directory
        self._check_pathformat(path)

        # Find the format of the data files
        self._find_format(datatype, kwargs.get("alone"))

        # Find relevant information without opening the files (e.g.
        # the number of files to be loaded) or opening the *.out files
        if self._alone is True:
            self._findfiles(nout)
        else:
            self._read_outfile(nout, endian)

        # For every output load the desired variables
        for i, exout in enumerate(self.nout):
            self._load_variables(vars, i, exout, endian)

        # Assign the variables to the class
        for key in self._d_vars:
            setattr(self, key, self._d_vars[key])

        # Transpose nshp (to match with variables)
        try:
            self.nshp = self.nshp[::-1] if self.dim > 1 else self.nshp
        except ValueError:
            pass

        # Convert ntime if only one number of a list
        if isinstance(self.ntime, np.ndarray) and len(self.ntime) == 1:
            self.ntime = self.ntime[0]

        # Print loaded folder and output
        if text:
            _nout_out = (
                self.nout[0]
                if len(self.nout) == 1
                else [int(x) for x in self.nout]
            )
            print(f"Load: folder {path},     output {_nout_out}")

        # Try to read the file definitions.h
        defh = kwargs.get("defh")
        if defh is not False:
            pathdefh = self.pathdir / "definitions.h"
            defhfile = "definitions.hpp"
            if not pathdefh.exists():
                pathdefh = self.pathdir / "definitions.hpp"
                defhfile = "definitions.h"
            try:
                self.defh = self._read_defh(pathdefh)
            except FileNotFoundError:
                print(f"No {defhfile} is read!") if defh is True else ...

        # Try to read the file pluto.ini
        plini = kwargs.get("plini")
        if plini is not False:
            pathplini = self.pathdir / "pluto.ini"
            try:
                self.plini = self._read_plini(pathplini)
            except FileNotFoundError:
                print("No pluto.ini is read!") if plini is True else ...
        return

    def __str__(self):
        text3 = f"        - Projections {['x1c', 'x2c', 'x1rc', 'x2rc']}\n"
        text3 = text3 if self.geom != "CARTESIAN" else ""

        text = f"""
        Load class.
        It loads the data.

        File properties:
        - Current path loaded (pathdir)      {self.pathdir}
        - Format loaded       (format)       {self.format}

        Simulation properties
        - Dimensions    (dim)      {self.dim}
        - Geometry      (geom)     {self.geom}
        - Grid size     (gridsize) {self.gridsize}
        - Grid shape    (nshp)     {self.nshp}
        - Output loaded (nout)     {self.nout}
        - Time loaded   (ntime)    {self.ntime}

        Public attributes available:
        - Number of cells in each direction {["nx1", "nx2", "nx3"]}
        - Grid values (cell center)         {["x1", "x2", "x3"]}
        - Grid values (face center)         {["x1r", "x2r", "x3r"]}
        - Cells size                        {["dx1", "dx2", "dx3"]}
        - Time attributes                   {["outlist", "timelist"]}\n{text3}
        Variables available:
        {self._d_info["varslist"][0]}
        Variables loaded:
        {self._load_vars}

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

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, f"_{name}")
        except AttributeError:
            raise AttributeError(f"'Load' object has no attribute '{name}'")

    from .amr import _DataScanHDF5, _inspect_hdf5
    from .codes.echo_load import echo_load
    from .loadfuncs.defpluto import _read_defh, _read_plini
    from .loadfuncs.read_files import _read_dat, _read_h5, read_file
    from .loadfuncs.readdata import (
        _assign_var,
        _check_nout,
        _findfiles,
        _init_vardict,
        _load_variables,
    )
    from .loadfuncs.readfluid import (
        _compute_offset,
        _inspect_h5,
        _inspect_vtk,
        _offset_bin,
        _read_tabfile,
    )
    from .loadfuncs.readformat import _check_pathformat, _find_format
    from .loadfuncs.readgridout import (
        _read_grid_h5,
        _read_grid_vtk,
        _read_gridfile,
        _read_outfile,
        _split_gridfile,
    )
    from .loadfuncs.write_files import _write_h5, write_file
    from .toolfuncs.findlines import _check_var, find_contour, find_fieldlines
    from .toolfuncs.fourier import fourier
    from .toolfuncs.nabla import curl, divergence, gradient
    from .toolfuncs.transform import (
        _congrid,
        cartesian_vector,
        mirror,
        reshape_cartesian,
        reshape_uniform,
        slices,
    )
