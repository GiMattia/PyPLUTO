import mmap

import numpy as np


def _inspect_bin(self, i: int, endian: str | None) -> None:
    """Routine to inspect the binary file and find the variables, the
    offset and the shape. The routine loops over the lines of the file
    and finds the relevant information. The routine then creates a key
    'tot' in the offset and shape dictionaries, which contains the
    offset and shape of the whole data.

    Returns
    -------
    - None

    Parameters
    ----------
    - endian: str | None
        The endianess of the files.
    - i: int
        The index of the file to be loaded.

    ----

    Examples
    --------
    - Example #1: Inspect the binary file

        >>> _inspect_bin(0, 'big')

    """
    # Initialize the offset, shape arrays and dimensions dictionary
    self._offset, self._shape, self._dictdim = ({}, {}, {})

    # Open the file and read the lines
    f = open(self._filepath, "rb")
    for line in f:

        # Split the lines (unsplit are binary data)
        try:
            _, spl1, spl2 = line.split()[0:3]
        except ValueError:
            break

        # Find the dimensions of the domain
        if spl1 == b"dimensions":
            self.dim = int(spl2)

        # Find the endianess of the file and compute the binary format
        elif spl1 == b"endianity":
            self._d_info["endianess"][i] = ">" if endian == b"big" else "<"
            self._d_info["endianess"][i] = (
                self._d_end[endian]
                if endian is not None
                else self._d_info["endianess"][i]
            )

            scrh = "f" if self._charsize == 4 else "d"
            self._d_info["binformat"][i] = self._d_info["endianess"][i] + scrh

        # Find the number of particles in the datafile and the maximum
        # number of particles in the simulation
        elif spl1 == b"nparticles":
            self.nshp = int(line.split()[2])
            # self.npart = self.nshp

        # To be fixed (multiple loading)
        elif spl1 == b"idCounter":
            self.maxpart = np.max([int(line.split()[2]), self.maxpart])

        # Find the time information
        elif spl1 == b"time":
            self.ntime[i] = float(spl2)

        # Find the variable names
        elif spl1 == b"field_names":
            self._d_info["varskeys"][i] = [
                elem.decode() for elem in line.split()[2:]
            ]
            self._d_info["varslist"][i] = ["tot"]

        # Find the variable dimensions
        elif spl1 == b"field_dim":
            self._vardim = np.array(
                [int(elem.decode()) for elem in line.split()[2:]]
            )
            self._offset["tot"] = f.tell()
            self._shape["tot"] = (self.nshp, np.sum(self._vardim))
            # To be fixed (multiple loading)
            # self._shape['tot']  = (self.maxpart,np.sum(self.vardim))

    f.close()

    # Create the key variables in the vars dictionary
    for ind, j in enumerate(self._d_info["varskeys"][i]):
        self._shape[j] = self.nshp
        self._dictdim[j] = self._vardim[ind]


def _inspect_vtk(self, i: int, endian: str | None) -> None:
    """Routine to inspect the vtk file and find the variables, the
    offset and the shape. The routine loops over the lines of the file
    and finds the relevant information. The routine also finds the time
    information if the file is standalone. The routine also finds the
    coordinates if the file is standalone and cartesian.

    Returns
    -------
    - None

    Parameters
    ----------
    - endian (not optional): str | None
        The endianess of the files.
    - i (not optional): int
        The index of the file to be loaded.

    ----

    Examples
    --------
    - Example #1: Inspect the vtk file

        >>> _inspect_vtk(0, 'big')

    """
    # Initialize the offset and shape arrays, the endianess and the coordinates dictionary
    self._offset, self._shape = ({}, {})

    endl = self._d_info["endianess"][i] = (
        ">" if endian is None else self._d_end[endian]
    )
    if endl is None:
        raise ValueError("Error: Wrong endianess in vtk file.")

    # Open the file and read the lines
    f = open(self._filepath, "rb")

    # This is a crude implementation to find the variables and their
    # offsets in the vtk file. The routine loops over the lines of the
    # file and finds the relevant information. The routine also finds
    # the time information if the file is standalone. The routine also
    # finds the coordinates if the file is standalone and cartesian.
    # The routine is (unfortunately) very slow since the file is read
    # line by line.
    """
    for l in f:

        # Split the lines (unsplit are binary data)
        try:
            spl0, spl1, _ = l.split()[0:3]

        except:
            continue

        # Find the number of points and store it
        if spl0 == b'POINTS':
            self.dim = int(spl1)
            self._offset['points'] = f.tell()
            self._shape['points']  = (self.dim,3)

        #elif spl1 == b'Identity':
        #    f.readline()
        #    self._offset['id'] = f.tell()
        #    self._shape['id'] = self.dim

        #elif spl1 == b'tinj':
        #    f.readline()
        #    self._offset['tinj'] = f.tell()
        #    self._shape['tinj'] = self.dim

        elif spl0 == b'SCALARS':
            var = spl1.decode()
            f.readline()
            self._offset[var] = f.tell()
            self._shape[var] = self.dim
            continue

        elif spl0 == b'VECTORS':
            var = spl1.decode()
            self._shape[var]  = (self.dim,int(l.split()[3]))
            self._offset[var] = f.tell()

    print(self._offset, self._shape)
    """

    mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

    search_pos = 0

    while True:
        # Find the next occurrence of the header
        points_pos = mmapped_file.find(b"POINTS", search_pos)

        # Determine the closest header found
        if points_pos == -1:  # and scalars_pos == -1 and vectors_pos == -1:
            break  # No more headers found

        # min_pos = min((pos for pos in [points_pos, scalars_pos, vectors_pos] if pos != -1))

        # if min_pos == points_pos:
        # Handle POINTS
        line_end = mmapped_file.find(b"\n", points_pos)
        line = mmapped_file[points_pos:line_end:1]
        parts = line.split()
        self.dim = int(parts[1])

        offset = line_end + 1
        self._offset["points"] = offset
        self._shape["points"] = (self.dim, 3)

        search_pos = line_end + 3 * 4 * self.dim + 1

    while True:
        # Find the next occurrence of the header
        # points_pos  = mmapped_file.find(b'POINTS', search_pos)
        scalars_pos = mmapped_file.find(b"SCALARS", search_pos)
        # vectors_pos = -1#mmapped_file.find(b'VECTORS', search_pos)

        # Determine the closest header found
        if scalars_pos == -1:  # and scalars_pos == -1 and vectors_pos == -1:
            break  # No more headers found

        # Move to the end of the 'SCALARS' line
        line_end = mmapped_file.find(b"\n", scalars_pos)
        line = mmapped_file[scalars_pos:line_end]
        parts = line.split()
        var = parts[1].decode()

        # Move to the start of the scalar data
        lookup_table_pos = mmapped_file.find(b"LOOKUP_TABLE default", line_end)
        self._offset[var] = mmapped_file.find(b"\n", lookup_table_pos) + 1
        self._shape[var] = self.dim

        search_pos = line_end + 4 * self.dim + 1

    while True:

        vectors_pos = mmapped_file.find(b"VECTORS", search_pos)

        # Determine the closest header found
        if vectors_pos == -1:  # and scalars_pos == -1 and vectors_pos == -1:
            break  # No more headers found
        # elif min_pos == vectors_pos:
        # Handle VECTORS
        line_end = mmapped_file.find(b"\n", vectors_pos)
        line = mmapped_file[vectors_pos:line_end]
        parts = line.split()
        var = parts[1].decode()

        self._shape[var] = (self.dim, int(parts[3]))
        self._offset[var] = line_end + 1

        search_pos = line_end + self.dim * int(parts[3]) * 4 + 1

    mmapped_file.close()

    # Find the variables and store them
    self._d_info["binformat"][i] = self._d_info["endianess"][i] + "f4"
    self._d_info["varslist"][i] = np.array(list(self._offset.keys()))

    f.close()

    # Create the key variables in the vars dictionary
    for ind, j in enumerate(self._d_info["varskeys"][i]):
        self._shape[j] = self.nshp
        self._dictdim[j] = self._vardim[ind]
        self._init_vardict(j)


def _store_bin_particles(self, i: int) -> None:
    """Routine to store the particles data. The routine loops over the
    variables and stores the data in the dictionary from the 'tot' key.
    Then the 'tot' keyword is removed from the dictionary for memory and
    clarity reasons.

    Returns
    -------
    - None

    Parameters
    ----------
    - i (not optional): int
        The index of the file to be loaded.

    ----

    Examples
    --------
    - Example 1: Store the data

        >>> _store_bin_particles(0)

    """
    # Mask the array (to be fixed for multiple loadings)
    # masked_array = np.ma.masked_array(self._d_vars['tot'][0].astype('int'),
    #                                          np.isnan(self._d_vars['tot'][0]))

    # Start with column 0 (id) and loop over the variable names
    ncol = 0
    for j, var in enumerate(self._d_info["varskeys"][i]):

        # Compute the size of the variable and store the data
        szvar = self._vardim[j]
        index = ncol if szvar == 1 else slice(ncol, ncol + szvar)
        if self._lennout != 1:
            # To be fixed for multiple loadings
            raise NotImplementedError("multiple loading not implemented yet")
            # self._d_vars[var][i] = self._d_vars['tot'][index]
        else:
            self._d_vars[var] = self._d_vars["tot"][index]

        # Update the column counter
        ncol += szvar

    # Remove the 'tot' key from the dictionary
    del self._d_vars["tot"]


def _store_vtk_particles(self, i: int) -> None:
    """Routine to store the particles data. Since positions and
    velocities are stored in 2d arrays, the routine splits the data in
    the different components and stores them in the dictionary.

    Returns
    -------
    - None

    Parameters
    ----------
    - i (not optional): int
        The index of the file to be loaded.

    ----

    Examples
    --------
    - Example 1: Store the data

        >>> _store_vtk_particles(0)

    """
    vardict = {
        "points": ["x1", "x2", "x3"],
        "Velocity": ["vx1", "vx2", "vx3"],
        "Four-Velocity": ["vx1", "vx2", "vx3"],
    }

    # Store the position in the dictionary
    for var in vardict:
        if var in self._d_vars:
            for i, j in enumerate(vardict[var]):
                self._d_vars[j] = self._d_vars[var][i]
            del self._d_vars[var]

    # Store the id in the dictionary
    if "Identity" in self._d_vars:
        self._d_vars["id"] = self._d_vars["Identity"]
        del self._d_vars["Identity"]

    # Store the position in the dictionary (old way)
    # if 'points' in self._d_vars:
    #    self._d_vars['x1'] = self._d_vars['points'][0]
    #    self._d_vars['x2'] = self._d_vars['points'][1]
    #    self._d_vars['x3'] = self._d_vars['points'][2]
    #    del self._d_vars['points']

    # Store the velocity in the dictionary
    # if 'Four-Velocity' in self._d_vars:
    #    self._d_vars['vx1'] = self._d_vars['Four-Velocity'][0]
    #    self._d_vars['vx2'] = self._d_vars['Four-Velocity'][1]
    #    self._d_vars['vx3'] = self._d_vars['Four-Velocity'][2]
    #    del self._d_vars['Four-Velocity']
    # elif 'Velocity' in self._d_vars:
    #    self._d_vars['vx1'] = self._d_vars['Velocity'][0]
    #    self._d_vars['vx2'] = self._d_vars['Velocity'][1]
    #    self._d_vars['vx3'] = self._d_vars['Velocity'][2]
    #    del self._d_vars['Velocity']
    # elif 'vel' in self._d_vars:
    #    self._d_vars['vx1'] = self._d_vars['vel'][0]
    #    self._d_vars['vx2'] = self._d_vars['vel'][1]
    #    self._d_vars['vx3'] = self._d_vars['vel'][2]
    #    del self._d_vars['vel']


def _compute_offset(
    self, i: int, endian: str | None, exout: int, var: str | None
) -> None:
    """Routine to compute the offset and shape of the variables to be
    loaded. The routine calls different functions depending on the file
    format.

    Returns
    -------
    - None

    Parameters
    ----------
    - endian (not optional): str | None
        The endianess of the files.
    - exout (not optional): int
        The index of the output to be loaded.
    - i (not optional): int
        The index of the file to be loaded.
    - var (not optional): str | None
        The variable to be loaded.

    ----

    Examples
    --------
    - Example #1: Load all the variables

        >>> _compute_offset(0, None, 0, True)

    """
    # Depending on the file calls different routines
    if self.format == "vtk":
        self._inspect_vtk(i, endian)
    else:
        self._inspect_bin(i, endian)
