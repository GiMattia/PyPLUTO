import h5py
import numpy as np


def _inspect_hdf5(self, i: int, exout: int) -> None:
    """Routine to inspect the hdf5 file from chombo.

    Returns
    -------
    - None

    Parameters
    ----------
        - exout (not optional): int
        The index of the output to be loaded.
    - i (not optional): int
        The index of the file to be loaded.

    Notes
    -----
    - This routines will be optimize in the future, alongside a novel
            implementation of the AMR in the PLUTO code.

    ----

    Examples
    --------
        - Example #1: Inspect the hdf5 file

                >>> _inspect_hdf5(0, 0)

    """
    try:
        self._read_gridfile()
    except FileNotFoundError:
        pass

    self.x1range = None
    self.x2range = None
    self.x3range = None

    h5file = h5py.File(self._filepath, "r")
    self.multiple = False
    self.d_info["varslist"] = []
    self.ntime = h5file.attrs.get("time")
    for i in range(h5file.attrs.get("num_components")):
        self.d_info["varslist"].append(h5file.attrs.get("component_" + str(i)))

    NewData = self._DataScanHDF5(h5file, self.d_info["varslist"], self.level)

    for key in NewData.keys():
        if key == "grid":
            for key2 in NewData[key].keys():
                setattr(self, key2, NewData[key][key2])
            continue
        setattr(self, key, NewData[key])

    h5file.close()


def _DataScanHDF5(self, fp, myvars, ilev) -> dict:
    """Scans the Chombo HDF5 data files for AMR in PLUTO.

    Returns
    -------
    - OutDict: dictionary
        The dictionary consisting of variable names as keys and its values.

    Parameters
    ----------
    - fp: pointer
        The data file pointer.
    - ilev: float
        The AMR level.
    - myvars: str
        The names of the variables to be read.

    Notes
    -----
    - Due to the particularity of AMR, the grid arrays loaded in ReadGridFile
      are overwritten here.
    - This routines will be optimize in the future, alongside a novel
      implementation of the AMR in the PLUTO code.

    ----

    Examples
    --------
    - Example #1:

            >>> _DataScanHDF5(fp, myvars, ilev)

    """
    # Read the grid information
    dim = fp["Chombo_global"].attrs.get("SpaceDim")
    nlev = fp.attrs.get("num_levels")
    il = min(nlev - 1, ilev)
    lev = []
    for i in range(nlev):
        lev.append("level_" + str(i))
    freb = np.zeros(nlev, dtype="int")
    for i in range(il + 1)[::-1]:
        fl = fp[lev[i]]
        if i == il:
            pdom = fl.attrs.get("prob_domain")
            dx = fl.attrs.get("dx")
            dt = fl.attrs.get("dt")
            ystr = 1.0
            zstr = 1.0
            logr = 0
            try:
                # self.geom = fl.attrs.get("geometry")
                logr = fl.attrs.get("logr")
                if dim >= 2:
                    ystr = fl.attrs.get("g_x2stretch")
                if dim == 3:
                    zstr = fl.attrs.get("g_x3stretch")
            except DeprecationWarning:
                print("Old HDF5 file, not reading stretch and logr factors")
            freb[i] = 1
            x1b = fl.attrs.get("domBeg1")
            if dim == 1:
                x2b = 0
            else:
                x2b = fl.attrs.get("domBeg2")
            if dim == 1 or dim == 2:
                x3b = 0
            else:
                x3b = fl.attrs.get("domBeg3")
            jbeg = 0
            jend = 0
            ny = 1
            kbeg = 0
            kend = 0
            nz = 1
            if dim == 1:
                ibeg = pdom[0]
                iend = pdom[1]
                nx = iend - ibeg + 1
            elif dim == 2:
                ibeg = pdom[0]
                iend = pdom[2]
                nx = iend - ibeg + 1
                jbeg = pdom[1]
                jend = pdom[3]
                ny = jend - jbeg + 1
            elif dim == 3:
                ibeg = pdom[0]
                iend = pdom[3]
                nx = iend - ibeg + 1
                jbeg = pdom[1]
                jend = pdom[4]
                ny = jend - jbeg + 1
                kbeg = pdom[2]
                kend = pdom[5]
                nz = kend - kbeg + 1
        else:
            rat = fl.attrs.get("ref_ratio")
            freb[i] = rat * freb[i + 1]

    dx0 = dx * freb[0]

    ## Allow to load only a portion of the domain
    if self.x1range is not None:
        if logr == 0:
            self.x1range = self.x1range - x1b
        else:
            self.x1range = [
                np.log(self.x1range[0] / x1b),
                np.log(self.x1range[1] / x1b),
            ]
        ibeg0 = min(self.x1range) / dx0
        iend0 = max(self.x1range) / dx0
        ibeg = max([ibeg, int(ibeg0 * freb[0])])
        iend = min([iend, int(iend0 * freb[0] - 1)])
        nx = iend - ibeg + 1
    if self.x2range is not None:
        self.x2range = (self.x2range - x2b) / ystr
        jbeg0 = min(self.x2range) / dx0
        jend0 = max(self.x2range) / dx0
        jbeg = max([jbeg, int(jbeg0 * freb[0])])
        jend = min([jend, int(jend0 * freb[0] - 1)])
        ny = jend - jbeg + 1
    if self.x3range is not None:
        self.x3range = (self.x3range - x3b) / zstr
        kbeg0 = min(self.x3range) / dx0
        kend0 = max(self.x3range) / dx0
        kbeg = max([kbeg, int(kbeg0 * freb[0])])
        kend = min([kend, int(kend0 * freb[0] - 1)])
        nz = kend - kbeg + 1

    ## Create uniform grids at the required level
    if logr == 0:
        x1 = x1b + (ibeg + np.array(range(nx)) + 0.5) * dx
    else:
        x1 = (
            x1b
            * (
                np.exp((ibeg + np.array(range(nx)) + 1) * dx)
                + np.exp((ibeg + np.array(range(nx))) * dx)
            )
            * 0.5
        )
    x2 = x2b + (jbeg + np.array(range(ny)) + 0.5) * dx * ystr
    x3 = x3b + (kbeg + np.array(range(nz)) + 0.5) * dx * zstr
    if logr == 0:
        dx1 = np.ones(nx) * dx
    else:
        dx1 = x1b * (
            np.exp((ibeg + np.array(range(nx)) + 1) * dx)
            - np.exp((ibeg + np.array(range(nx))) * dx)
        )
    dx2 = np.ones(ny) * dx * ystr
    dx3 = np.ones(nz) * dx * zstr

    # Create the xr arrays containing the edges positions
    # Useful for pcolormesh which should use those
    x1r = np.zeros(len(x1) + 1)
    x1r[1:] = x1 + dx1 / 2.0
    x1r[0] = x1r[1] - dx1[0]
    x2r = np.zeros(len(x2) + 1)
    x2r[1:] = x2 + dx2 / 2.0
    x2r[0] = x2r[1] - dx2[0]
    x3r = np.zeros(len(x3) + 1)
    x3r[1:] = x3 + dx3 / 2.0
    x3r[0] = x3r[1] - dx3[0]
    NewGridDict = dict(
        [
            ("n1", nx),
            ("n2", ny),
            ("n3", nz),
            ("x1", x1),
            ("x2", x2),
            ("x3", x3),
            ("x1r", x1r),
            ("x2r", x2r),
            ("x3r", x3r),
            ("dx1", dx1),
            ("dx2", dx2),
            ("dx3", dx3),
            ("Dt", dt),
        ]
    )

    # Variables table
    nvar = len(myvars)
    vars = np.zeros((nx, ny, nz, nvar))
    LevelDic = {
        "nbox": 0,
        "ibeg": ibeg,
        "iend": iend,
        "jbeg": jbeg,
        "jend": jend,
        "kbeg": kbeg,
        "kend": kend,
    }
    AMRLevel = []
    AMRBoxes = np.zeros((nx, ny, nz))
    for i in range(il + 1):
        AMRLevel.append(LevelDic.copy())
        fl = fp[lev[i]]
        data = fl["data:datatype=0"]
        boxes = fl["boxes"]
        nbox = len(boxes["lo_i"])
        AMRLevel[i]["nbox"] = nbox
        ncount = 0
        AMRLevel[i]["box"] = []
        for j in range(nbox):  # loop on all boxes of a given level
            AMRLevel[i]["box"].append(
                {
                    "x0": 0.0,
                    "x1": 0.0,
                    "ib": 0,
                    "ie": 0,
                    "y0": 0.0,
                    "y1": 0.0,
                    "jb": 0,
                    "je": 0,
                    "z0": 0.0,
                    "z1": 0.0,
                    "kb": 0,
                    "ke": 0,
                }
            )
            # Box indexes
            ib = boxes[j]["lo_i"]
            ie = boxes[j]["hi_i"]
            nbx = ie - ib + 1
            jb = 0
            je = 0
            nby = 1
            kb = 0
            ke = 0
            nbz = 1
            if dim > 1:
                jb = boxes[j]["lo_j"]
                je = boxes[j]["hi_j"]
                nby = je - jb + 1
            if dim > 2:
                kb = boxes[j]["lo_k"]
                ke = boxes[j]["hi_k"]
                nbz = ke - kb + 1
            szb = nbx * nby * nbz * nvar
            # Rescale to current level
            kb = kb * freb[i]
            ke = (ke + 1) * freb[i] - 1
            jb = jb * freb[i]
            je = (je + 1) * freb[i] - 1
            ib = ib * freb[i]
            ie = (ie + 1) * freb[i] - 1

            # Skip boxes lying outside ranges
            if (
                (ib > iend)
                or (ie < ibeg)
                or (jb > jend)
                or (je < jbeg)
                or (kb > kend)
                or (ke < kbeg)
            ):
                ncount = ncount + szb
            else:
                ### Read data
                q = data[ncount : ncount + szb].reshape((nvar, nbz, nby, nbx)).T

                ### Find boxes intersections with current domain ranges
                ib0 = max([ibeg, ib])
                ie0 = min([iend, ie])
                jb0 = max([jbeg, jb])
                je0 = min([jend, je])
                kb0 = max([kbeg, kb])
                ke0 = min([kend, ke])

                ### Store box corners in the AMRLevel structure
                if logr == 0:
                    AMRLevel[i]["box"][j]["x0"] = x1b + dx * (ib0)
                    AMRLevel[i]["box"][j]["x1"] = x1b + dx * (ie0 + 1)
                else:
                    AMRLevel[i]["box"][j]["x0"] = x1b * np.exp(dx * (ib0))
                    AMRLevel[i]["box"][j]["x1"] = x1b * np.exp(dx * (ie0 + 1))
                AMRLevel[i]["box"][j]["y0"] = x2b + dx * (jb0) * ystr
                AMRLevel[i]["box"][j]["y1"] = x2b + dx * (je0 + 1) * ystr
                AMRLevel[i]["box"][j]["z0"] = x3b + dx * (kb0) * zstr
                AMRLevel[i]["box"][j]["z1"] = x3b + dx * (ke0 + 1) * zstr
                AMRLevel[i]["box"][j]["ib"] = ib0
                AMRLevel[i]["box"][j]["ie"] = ie0
                AMRLevel[i]["box"][j]["jb"] = jb0
                AMRLevel[i]["box"][j]["je"] = je0
                AMRLevel[i]["box"][j]["kb"] = kb0
                AMRLevel[i]["box"][j]["ke"] = ke0
                AMRBoxes[
                    ib0 - ibeg : ie0 - ibeg + 1,
                    jb0 - jbeg : je0 - jbeg + 1,
                    kb0 - kbeg : ke0 - kbeg + 1,
                ] = il

                ### Extract the box intersection from data stored in q
                cib0 = (ib0 - ib) // freb[i]
                cie0 = (ie0 - ib) // freb[i]
                cjb0 = (jb0 - jb) // freb[i]
                cje0 = (je0 - jb) // freb[i]
                ckb0 = (kb0 - kb) // freb[i]
                cke0 = (ke0 - kb) // freb[i]
                q1 = np.zeros(
                    (cie0 - cib0 + 1, cje0 - cjb0 + 1, cke0 - ckb0 + 1, nvar)
                )
                q1 = q[cib0 : cie0 + 1, cjb0 : cje0 + 1, ckb0 : cke0 + 1, :]

                # Remap the extracted portion
                if dim == 1:
                    new_shape = (ie0 - ib0 + 1, 1)
                elif dim == 2:
                    new_shape = (ie0 - ib0 + 1, je0 - jb0 + 1)
                else:
                    new_shape = (ie0 - ib0 + 1, je0 - jb0 + 1, ke0 - kb0 + 1)

                stmp = list(new_shape)
                while stmp.count(1) > 0:
                    stmp.remove(1)
                new_shape = tuple(stmp)

                for iv in range(nvar):
                    vars[
                        ib0 - ibeg : ie0 - ibeg + 1,
                        jb0 - jbeg : je0 - jbeg + 1,
                        kb0 - kbeg : ke0 - kbeg + 1,
                        iv,
                    ] = self._congrid(
                        q1[:, :, :, iv].squeeze(),
                        new_shape,
                        method="linear",
                        minusone=True,
                    ).reshape((ie0 - ib0 + 1, je0 - jb0 + 1, ke0 - kb0 + 1))
                ncount = ncount + szb

    h5vardict = {}
    for iv in range(nvar):
        myvars[iv] = myvars[iv].decode()
        h5vardict[myvars[iv]] = vars[:, :, :, iv].squeeze().T
    self.load_vars = myvars
    AMRdict = dict([("AMRBoxes", AMRBoxes), ("AMRLevel", AMRLevel)])
    OutDict = dict(NewGridDict)
    OutDict.update(AMRdict)
    OutDict.update(h5vardict)

    return OutDict


def oplotbox(
    self,
    AMRLevel,
    lrange=[0, 0],
    cval=None,
    islice=-1,
    jslice=-1,
    kslice=-1,
    geom="CARTESIAN",
    ax=None,
    **kwargs,
) -> None:
    """This method overplots the AMR boxes up to the specified level.

    Returns
    -------
      - None

    Parameters
    ----------
      - AMRLevel: AMR object
    AMR object loaded during the reading and stored in the pload object.
      - ax: axis object
          The axis object where to plot the AMR boxes.
      - cval: str | None
          List of colors for the levels to be overplotted.
      - geom: str, default 'CARTESIAN'
          The specified geometry. At the moment 'CARTESIAN' and 'POLAR' are the
                      handled geometries.
      - islice: int
          The index of the 2D slice along x-axis direction.
      - jslice: int
          The index of the 2D slice along y-axis direction.
      - kslice: int, default min(x3)
          The index of the 2D slice along z-axis direction.
      - kwargs: Any
          The kwargs of the plot method.
      - lrange: [level_min, level_max]
          The range to be overplotted.

      ----

    Examples
    --------
      - Example #1: Overplot the AMR boxes up to the specified level

              >>> oplotbox(AMRLevel, lrange=[0, 2])

    """
    nlev = len(AMRLevel)
    lrange[1] = min(lrange[1], nlev - 1)
    npl = lrange[1] - lrange[0] + 1
    lpls = [lrange[0] + v for v in range(npl)]
    cols = cval[0:nlev] if cval is not None else self.color[0:nlev]
    # Get the offset and the type of slice
    Slice = 0
    inds = "k"
    xx = "x"
    yy = "y"
    if islice >= 0:
        Slice = islice + AMRLevel[0]["ibeg"]
        inds = "i"
        xx = "y"
        yy = "z"
    if jslice >= 0:
        Slice = jslice + AMRLevel[0]["jbeg"]
        inds = "j"
        xx = "x"
        yy = "z"
    if kslice >= 0:
        Slice = kslice + AMRLevel[0]["kbeg"]
        inds = "k"
        xx = "x"
        yy = "y"

    # Overplot the boxes
    for il in lpls:
        level = AMRLevel[il]
        for ib in range(level["nbox"]):
            box = level["box"][ib]
            if (Slice - box[inds + "b"]) * (box[inds + "e"] - Slice) >= 0:
                if geom == "CARTESIAN":
                    x0 = box[xx + "0"]
                    x1 = box[xx + "1"]
                    y0 = box[yy + "0"]
                    y1 = box[yy + "1"]
                    self.plot(
                        [x0, x1, x1, x0, x0],
                        [y0, y0, y1, y1, y0],
                        color=cols[il],
                        ax=ax,
                        **kwargs,
                    )
                elif (geom == "POLAR") or (geom == "SPHERICAL"):
                    dn = np.pi / 50.0
                    x0 = box[xx + "0"]
                    x1 = box[xx + "1"]
                    y0 = box[yy + "0"]
                    y1 = box[yy + "1"]
                    if y0 == y1:
                        y1 = 2 * np.pi + y0 - 1.0e-3
                    if kslice >= 0 and geom == "SPHERICAL":
                        y0 = np.pi / 2 - y0
                        y1 = np.pi / 2 - y1
                    xb = np.concatenate(
                        [
                            [x0 * np.cos(y0), x1 * np.cos(y0)],
                            x1
                            * np.cos(
                                np.linspace(y0, y1, num=int(abs(y0 - y1) / dn))
                            ),
                            [x1 * np.cos(y1), x0 * np.cos(y1)],
                            x0
                            * np.cos(
                                np.linspace(y1, y0, num=int(abs(y0 - y1) / dn))
                            ),
                        ]
                    )
                    yb = np.concatenate(
                        [
                            [x0 * np.sin(y0), x1 * np.sin(y0)],
                            x1
                            * np.sin(
                                np.linspace(y0, y1, num=int(abs(y0 - y1) / dn))
                            ),
                            [x1 * np.sin(y1), x0 * np.sin(y1)],
                            x0
                            * np.sin(
                                np.linspace(y1, y0, num=int(abs(y0 - y1) / dn))
                            ),
                        ]
                    )
                    self.plot(xb, yb, c=cols[il], ax=ax, **kwargs)


def _read_gridfile(self) -> None:
    """The file grid.out is read and all the grid information are stored
    in the Load class. Such information are the dimensions, the
    geometry, the center and edges of each cell, the grid shape and size
    and, in case of non cartesian coordinates, the transformed cartesian
    coordinates (only 2D for now).bThe full non-cartesian 3D
    transformations have not been implemented yet.

    Returns
    -------
    - None

    Parameters
    ----------
    - None

    ----

    Examples
    --------
    - Example #1: read the grid file

        >>> _read_gridfile()

    """
    # Initialize relevant lists
    nmax, xL, xR = [], [], []

    # Open and read the gridfile
    with open(self._pathgrid) as gfp:
        for i in gfp.readlines():
            self._split_gridfile(i, xL, xR, nmax)

    # Compute nx1, nx2, nx3
    self.nx1, self.nx2, self.nx3 = nmax
    nx1p2 = self.nx1 + self.nx2
    nx1p3 = self.nx1 + self.nx2 + self.nx3

    # Define grid shapes based on dimensions
    nx1s, nx2s, nx3s = self.nx1 + 1, self.nx2 + 1, self.nx3 + 1
    GRID_SHAPES = {
        1: lambda nx1, _, __: (nx1, nx1s, None, None),
        2: lambda nx1, nx2, _: ((nx2, nx1), (nx2, nx1s), (nx2s, nx1), None),
        3: lambda nx1, nx2, nx3: (
            (nx3, nx2, nx1),
            (nx3, nx2, nx1s),
            (nx3, nx2s, nx1),
            (nx3s, nx2, nx1),
        ),
    }

    # Determine grid shape based on dimension
    (self.nshp, self._nshp_st1, self._nshp_st2, self._nshp_st3) = GRID_SHAPES[
        self.dim
    ](self.nx1, self.nx2, self.nx3)

    # Compute the centered and staggered grid values
    self.x1r = np.array(xL[0 : self.nx1] + [xR[self.nx1 - 1]])
    self.x1 = 0.5 * (self.x1r[:-1] + self.x1r[1:])
    self.dx1 = self.x1r[1:] - self.x1r[:-1]

    self.x2r = np.array(xL[self.nx1 : nx1p2] + [xR[nx1p2 - 1]])
    self.x2 = 0.5 * (self.x2r[:-1] + self.x2r[1:])
    self.dx2 = self.x2r[1:] - self.x2r[:-1]

    self.x3r = np.array(xL[nx1p2:nx1p3] + [xR[nx1p3 - 1]])
    self.x3 = 0.5 * (self.x3r[:-1] + self.x3r[1:])
    self.dx3 = self.x3r[1:] - self.x3r[:-1]

    # Compute the cartesian grid coordinates (non-cartesian geometry)

    if self.geom == "POLAR" or self.geom == "CYLINDRICAL":
        x1_2D, x2_2D = np.meshgrid(self.x1, self.x2, indexing="ij")
        x1r_2D, x2r_2D = np.meshgrid(self.x1r, self.x2r, indexing="ij")

        self.x1c = (np.cos(x2_2D) * x1_2D).T
        self.x2c = (np.sin(x2_2D) * x1_2D).T
        self.x1rc = (np.cos(x2r_2D) * x1r_2D).T
        self.x2rc = (np.sin(x2r_2D) * x1r_2D).T

        self.gridlist3 = ["x1c", "x2c", "x1rc", "x2rc"]
        del x1_2D, x2_2D, x1r_2D, x2r_2D
    elif self.geom == "SPHERICAL":
        x1_2D, x2_2D = np.meshgrid(self.x1, self.x2, indexing="ij")
        x1r_2D, x2r_2D = np.meshgrid(self.x1r, self.x2r, indexing="ij")

        self.x1p = (np.sin(x2_2D) * x1_2D).T
        self.x2p = (np.cos(x2_2D) * x1_2D).T
        self.x1rp = (np.sin(x2r_2D) * x1r_2D).T
        self.x2rp = (np.cos(x2r_2D) * x1r_2D).T

        x1_2D, x3_2D = np.meshgrid(self.x1, self.x3, indexing="ij")
        x1r_2D, x3r_2D = np.meshgrid(self.x1r, self.x3r, indexing="ij")

        self.x1t = (np.cos(x3_2D) * x1_2D).T
        self.x3t = (np.sin(x3_2D) * x1_2D).T
        self.x1rt = (np.cos(x3r_2D) * x1r_2D).T
        self.x3rt = (np.sin(x3r_2D) * x1r_2D).T

        self.gridlist3 = [
            "x1p",
            "x2p",
            "x1rp",
            "x2rp",
            "x1t",
            "x3t",
            "x1rt",
            "x3rt",
        ]

        del x1_2D, x2_2D, x1r_2D, x2r_2D, x3_2D, x3r_2D

        if self.dim == 3 and self._full3d is True:
            x1_3D, x2_3D, x3_3D = np.meshgrid(
                self.x1, self.x2, self.x3, indexing="ij"
            )
            x1r_3D, x2r_3D, x3r_3D = np.meshgrid(
                self.x1r, self.x2r, self.x3r, indexing="ij"
            )

            self.x1c = (np.sin(x2_3D) * np.cos(x3_3D) * x1_3D).T
            self.x2c = (np.sin(x2_3D) * np.sin(x3_3D) * x1_3D).T
            self.x3c = (np.cos(x2_3D) * x1_3D).T
            self.x1rc = (np.sin(x2r_3D) * np.cos(x3r_3D) * x1r_3D).T
            self.x2rc = (np.sin(x2r_3D) * np.sin(x3r_3D) * x1r_3D).T
            self.x3rc = (np.cos(x2r_3D) * x1r_3D).T

            self.gridlist3.extend(["x1c", "x2c", "x3c", "x1rc", "x2rc", "x3rc"])

            del x1_3D, x2_3D, x3_3D, x1r_3D, x2r_3D, x3r_3D
        else:
            pass
            # self.x1c = np.zeros((self.nx1,self.nx2,self.nx3))
            # print(np.shape(self.x1c))
            # self.pippo = np.meshgrid(self.x2, self.x3, indexing='xy')
            # print(np.shape(self.pippo))

    # Compute the gridsize both centered and staggered
    self.gridsize = self.nx1 * self.nx2 * self.nx3
    self.gridsize_st1 = nx1s * self.nx2 * self.nx3
    self.gridsize_st2 = self.nx1 * nx2s * self.nx3
    self.gridsize_st3 = self.nx1 * self.nx2 * nx3s

    self.info = False


def _split_gridfile(
    self, i: str, xL: list[float], xR: list[float], nmax: list[int]
) -> None:
    """Splits the gridfile, storing the information in the variables
    passed by the function. Dimensions and geometry are stored in the
    class.

    Return
    ------

    - None

    Parameters
    ----------
    - i (not optional): str
        The line of the gridfile.
    - nmax (not optional): list[int]
        The number of the cells in the grid.
    - xL (not optional): list[float]
        The list of the left cell boundaries values.
    - xR (not optional): list[float]
        The list of the right cell boundaries values.

    ----

    Examples
    --------
    - Example #1: Split the gridfile

        >>> _split_gridfile(i, xL, xR, nmax)

    """
    # If the splitted line has only one string, try to convert it
    # to an integer (number of cells in a dimension).
    if len(i.split()) == 1:
        try:
            nmax.append(int(i.split(maxsplit=1)[0]))
        except ValueError:
            pass

    # Check if the splitted line has three strings
    if len(i.split()) == 3:
        # Try to convert the first string to an int (cell number in a dimension)
        # and the other two to floats (left and right cell boundaries)
        try:
            int(i.split(maxsplit=1)[0])
            xL.append(float(i.split()[1]))
            xR.append(float(i.split()[2]))

        # Check if the keyword is geometry or dimensions and
        # store the information in the class
        except ValueError:
            if i.split()[1] == "GEOMETRY:":
                self.geom = i.split()[2]
            if i.split()[1] == "DIMENSIONS:":
                self.dim = int(i.split()[2])
