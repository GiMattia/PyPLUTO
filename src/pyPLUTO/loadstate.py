"""Module that contains the LoadState class.

LoadState is BaseLoadState plus the grid: everything that only a fluid
simulation has. LoadPart keeps using BaseLoadState directly, since particles
carry their positions as ordinary variables rather than on a mesh.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from pyPLUTO.baseloadstate import BaseLoadState


@dataclass
class LoadState(BaseLoadState):
    """Class that stores the state of the Load class.

    Its purpose is to keep track of the current state of the data loading,
    such as the file paths, data arrays, and other properties and update the
    key attributes through all the different classes that handle the data
    loading at runtime.

    Every field here is a result rather than a setting, apart from full3D and
    level, so they are declared `field(init=False, repr=False)`: a grid has no
    meaningful default, and its very shape depends on the simulation being
    read. See BaseLoadState for what that declaration means.

    The grid names follow a grammar worth reading once, since there are a lot
    of them. The stem is the axis: x1, x2, x3 in the geometry of the
    simulation. An `r` after the stem means face centred instead of cell
    centred. A final letter means a Cartesian projection of a curved mesh,
    which is what a plot needs: `c` for polar and cylindrical, `p` for the
    poloidal plane of a spherical mesh, `t` for its azimuthal plane. So `x1`
    is the first axis at cell centres, `x1r` the same at faces, and `x1rc`
    the Cartesian projection of those faces.

    The `_st1`, `_st2` and `_st3` suffixes name the three staggered
    components, not the three axes: the first has x1 on the faces and the
    other two at the centres, the third has x3 on the faces and x1 and x2 at
    the centres. Each therefore has a shape of its own.
    """

    # Contents of definitions.h, as parsed at load time
    defh: dict = field(init=False, repr=False)

    # Cell sizes along the first axis
    dx1: np.ndarray = field(init=False, repr=False)

    # Cell sizes along the second axis
    dx2: np.ndarray = field(init=False, repr=False)

    # Cell sizes along the third axis
    dx3: np.ndarray = field(init=False, repr=False)

    # Whether the Cartesian mesh is computed at once or slice by slice
    full3D: bool = False

    # Geometry of the mesh: CARTESIAN, POLAR, CYLINDRICAL or SPHERICAL
    geom: str = field(init=False, repr=False)

    # Total number of cells in the mesh
    gridsize: int = field(init=False, repr=False)

    # Number of cells of the first staggered component
    gridsize_st1: int = field(init=False, repr=False)

    # Number of cells of the second staggered component
    gridsize_st2: int = field(init=False, repr=False)

    # Number of cells of the third staggered component
    gridsize_st3: int = field(init=False, repr=False)

    # AMR refinement level to read
    level: int = 0

    # Shape of the first staggered component
    nshp_st1: int | tuple[int, ...] | None = field(init=False, repr=False)

    # Shape of the second staggered component
    nshp_st2: tuple[int, ...] | None = field(init=False, repr=False)

    # Shape of the third staggered component
    nshp_st3: tuple[int, ...] | None = field(init=False, repr=False)

    # Number of cells along the first axis
    nx1: int = field(init=False, repr=False)

    # Number of cells along the second axis
    nx2: int = field(init=False, repr=False)

    # Number of cells along the third axis
    nx3: int = field(init=False, repr=False)

    # Contents of pluto.ini, as parsed at load time
    plini: dict = field(init=False, repr=False)

    # First axis, at cell centres
    x1: np.ndarray = field(init=False, repr=False)

    # First axis projected on Cartesian x, for a polar or cylindrical mesh
    x1c: np.ndarray = field(init=False, repr=False)

    # First axis projected on the poloidal plane, for a spherical mesh
    x1p: np.ndarray = field(init=False, repr=False)

    # First axis, at cell faces
    x1r: np.ndarray = field(init=False, repr=False)

    # Faces of the first axis projected on Cartesian x, polar or cylindrical
    x1rc: np.ndarray = field(init=False, repr=False)

    # Faces of the first axis projected on the poloidal plane, spherical
    x1rp: np.ndarray = field(init=False, repr=False)

    # Faces of the first axis projected on the azimuthal plane, spherical
    x1rt: np.ndarray = field(init=False, repr=False)

    # First axis projected on the azimuthal plane, for a spherical mesh
    x1t: np.ndarray = field(init=False, repr=False)

    # Second axis, at cell centres
    x2: np.ndarray = field(init=False, repr=False)

    # Second axis projected on Cartesian y, for a polar or cylindrical mesh
    x2c: np.ndarray = field(init=False, repr=False)

    # Second axis projected on the poloidal plane, for a spherical mesh
    x2p: np.ndarray = field(init=False, repr=False)

    # Second axis, at cell faces
    x2r: np.ndarray = field(init=False, repr=False)

    # Faces of the second axis projected on Cartesian y, polar or cylindrical
    x2rc: np.ndarray = field(init=False, repr=False)

    # Faces of the second axis projected on the poloidal plane, spherical
    x2rp: np.ndarray = field(init=False, repr=False)

    # Third axis, at cell centres
    x3: np.ndarray = field(init=False, repr=False)

    # Third axis projected on Cartesian z, for a polar or cylindrical mesh
    x3c: np.ndarray = field(init=False, repr=False)

    # Third axis, at cell faces
    x3r: np.ndarray = field(init=False, repr=False)

    # Faces of the third axis projected on Cartesian z, polar or cylindrical
    x3rc: np.ndarray = field(init=False, repr=False)

    # Faces of the third axis projected on the azimuthal plane, spherical
    x3rt: np.ndarray = field(init=False, repr=False)

    # Third axis projected on the azimuthal plane, for a spherical mesh
    x3t: np.ndarray = field(init=False, repr=False)
