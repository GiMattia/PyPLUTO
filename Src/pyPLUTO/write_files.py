from .libraries import *

def _write_h5(self, 
             data: NDArray | dict, 
             filename: str,
             dataname: str | None = None, 
             grid: bool = False,
             **kwargs: Any
            ) -> None:
    """
    Write the data to a HDF5 file.

    Returns
    -------

    - None

    Parameters
    ----------

    - filename: str
        the name of the HDF5 file
    - grid: bool
        if True, write the grid to the HDF5 file

    Notes
    -----

    - None

    ----

    ========
    Examples
    ========

    - Example #1: Write the data to a HDF5 file

        >>> write_h5('data.h5')

    """

    # Create the path to the HDF5 file
    path_h5 = self.pathdir / filename
    if not filename.endswith('.h5'): path_h5 += '.h5'

    # Open the HDF5 file
    with h5py.File(path_h5, 'w') as f:

        # Write the data to the HDF5 file
        if isinstance(data, dict):
            
            for key in data.keys():
                f.create_dataset(key, data = data[key])
        else:
            dataname = 'data' if dataname is None else dataname
            f.create_dataset(dataname, data = data)
        
        # Write the grid to the HDF5 file
        if grid is True:
            f.create_dataset('nx1', data = kwargs.get('nx1', self.nx1))
            f.create_dataset('nx2', data = kwargs.get('nx2', self.nx2))
            f.create_dataset('nx3', data = kwargs.get('nx3', self.nx3))
            f.create_dataset('x1',  data = kwargs.get('x1',  self.x1))
            f.create_dataset('x2',  data = kwargs.get('x2',  self.x2))
            f.create_dataset('x3',  data = kwargs.get('x3',  self.x3))
            f.create_dataset('dx1', data = kwargs.get('dx1', self.dx1))
            f.create_dataset('dx2', data = kwargs.get('dx2', self.dx2))
            f.create_dataset('dx3', data = kwargs.get('dx3', self.dx3))
    
    # End of the function
    return None
    

def write_vtk(self):
    """
    Write the data to a VTK file.

    Returns
    -------

    - None

    Parameters
    ----------

    - None

    Notes
    -----

    - None

    ----

    ========
    Examples
    ========

    - Example #1: Write the data to a VTK file

        >>> write_vtk()

    """
    
    raise NotImplementedError("write_vtk() is not yet implemented.")
    # Create the path to the VTK file
    self._pathvtk = self.pathdir / (self.format + '.vtk')
    
    # Open the VTK file
    with open(self._pathvtk, 'w') as f:
        
        # Write the header to the VTK file
        f.write('# vtk DataFile Version 3.0\n')
        f.write('VTK file for ' + self.format + '\n')
        f.write('ASCII\n')
        f.write('DATASET STRUCTURED_POINTS\n')
        f.write('DIMENSIONS ' + str(self.grid['nx1']) + ' ' + str(self.grid['nx2']) + ' ' + str(self.grid['nx3']) + '\n')
        f.write('ORIGIN ' + str(self.grid['x1'][0]) + ' ' + str(self.grid['x2'][0]) + ' ' + str(self.grid['x3'][0]) + '\n')
        f.write('SPACING ' + str(self.grid['dx1']) + ' ' + str(self.grid['dx2']) + ' ' + str(self.grid['dx3']) + '\n')
        f.write('POINT_DATA ' + str(self.grid['nx1'] * self.grid['nx2'] * self.grid['nx3']) + '\n')
        
        # Write the data to the VTK file
        for key in self.data.keys():
            f.write('SCALARS ' + key + ' float\n')
            f.write('LOOKUP_TABLE default\n')
            for i in range(self.grid['nx1']):
                for j in range(self.grid['nx2']):
                    for k in range(self.grid['nx3']):
                        f.write(str(self.data[key][i, j, k]) + '\n')
    
    # End of the function
    return None

def write_tab(self):
    """
    Write the data to a tab-separated file.

    Returns
    -------

    - None

    Parameters
    ----------

    - None

    Notes
    -----

    - None

    ----

    ========
    Examples
    ========

    - Example #1: Write the data to a tab-separated file

        >>> write_tab()

    """

    raise NotImplementedError("write_tab() is not yet implemented.")
    
    # Create the path to the tab-separated file
    self._pathtab = self.pathdir / (self.format + '.tab')
    
    # Open the tab-separated file
    with open(self._pathtab, 'w') as f:
        
        # Write the header to the tab-separated file
        f.write('# ' + self.format + '\n')
        
        # Write the data to the tab-separated file
        for key in self.data.keys():
            f.write('# ' + key + '\n')
            for i in range(self.grid['nx1']):
                for j in range(self.grid['nx2']):
                    for k in range(self.grid['nx3']):
                        f.write(str(self.data[key][i, j, k]) + '\t')
                    f.write('\n')
    
    # End of the function
    return None


def write_bin(self):
    """
    Write the data to a binary file.

    Returns
    -------

    - None

    Parameters
    ----------

    - None

    Notes
    -----

    - None

    ----

    ========
    Examples
    ========

    - Example #1: Write the data to a binary file

        >>> write_bin()

    """

    raise NotImplementedError("write_bin() is not yet implemented.")
    
    # Create the path to the binary file
    self._pathbin = self.pathdir / (self.format + '.bin')
    
    # Open the binary file
    with open(self._pathbin, 'wb') as f:
        
        # Write the data to the binary file
        for key in self.data.keys():
            f.write(self.data[key].tobytes())
    
    # End of the function
    return None

def write_file(self, 
             data: NDArray | dict, 
             filename: str,
             datatype: str | None = None,
             dataname: str | None = None, 
             grid: bool = False
            ) -> None:
    """
    Write the data to a file.

    Returns
    -------

    - None

    Parameters
    ----------

    - filename: str
        the name of the file

    Notes
    -----

    - None

    ----

    ========
    Examples
    ========

    - Example #1: Write the data to a file
    
            >>> write_file('data.h5')

    """
    
    # Check the datatype of the input data
    if datatype is None: datatype = filename.split('.')[-1]
    poss_types = {'dbl', 'flt', 'vtk', 'h5', 'tab'}
    if datatype not in poss_types:
        warn = f"Invalid datatype: {datatype}. Resetting to 'h5'"
        warnings.warn(warn)
        datatype = 'h5'
        
    # Check the format of the output files
    if datatype == 'h5':
        _write_h5(self, data, filename, dataname, grid)
    else:
        warn = f"Invalid datatype: {datatype}, not implemented yet! " \
                "Resetting to 'h5'"
        warnings.warn(warn)
        pass
    
    # End of the function
    return None