from .libraries import *

def read_vtk(self):
    """
    Read the data from a VTK file.

    Returns
    -------

    - None

    Parameters
    ----------

    - None

    Notes
    -----

    - None

    Examples
    --------

    - Example #1: Read the data from a VTK file

        >>> read_vtk()

    """
    
    # Create the path to the VTK file
    self._pathvtk = self.pathdir / (self.format + '.vtk')
    
    # Open the VTK file
    with open(self._pathvtk, 'r') as f:
        
        # Read the data from the VTK file
        data = f.readlines()
    
    # End of the function
    return None

def _read_h5(self, filename: str):
    """
    Read the data from a HDF5 file.

    Returns
    -------

    - None

    Parameters
    ----------

    - None

    Notes
    -----

    - None

    Examples
    --------

    - Example #1: Read the data from a HDF5 file

        >>> read_h5()

    """
    
    # Create the path to the HDF5 file
    try:
        self._pathh5 = self.pathdir / filename
    except:
        self._pathh5 = filename
    
    # Open the HDF5 file
    with h5py.File(self._pathh5, 'r') as f:
        for key in f.keys():
            setattr(self,key,f[key][()])#self.key = f[key]
    
    # End of the function
    return None

def read_tab(self):
    """
    Read the data from a tab file.

    Returns
    -------

    - None

    Parameters
    ----------

    - None

    Notes
    -----

    - None

    Examples
    --------

    - Example #1: Read the data from a tab file

        >>> read_tab()

    """
    
    # Create the path to the tab file
    self._pathtab = self.pathdir / (self.format + '.out')
    
    # Read the data from the tab file
    data = np.loadtxt(self._pathtab)
    
    # End of the function
    return None

def read_bin(self):
    """
    Read the data from a binary file.

    Returns
    -------

    - None

    Parameters
    ----------

    - None

    Notes
    -----

    - None

    Examples
    --------

    - Example #1: Read the data from a binary file

        >>> read_bin()

    """
    
    # Create the path to the binary file
    self._pathbin = self.pathdir / (self.format + '.out')
    
    # Read the data from the binary file
    with open(self._pathbin, 'rb') as f:
        data = np.fromfile(f, dtype=self.dtype)
    
    # End of the function
    return None

def read_files(self):
    """
    Read the data from the output files.

    Returns
    -------

    - None

    Parameters
    ----------

    - None

    Notes
    -----

    - None

    Examples
    --------

    - Example #1: Read the data from the output files

        >>> read_files()

    """
    
    # Check if the format is VTK
    if self.format == 'vtk':
        read_vtk(self)
    
    # Check if the format is HDF5
    elif self.format in ['dbl.h5', 'flt.h5']:
        _read_h5(self)
    
    # Check if the format is tab
    elif self.format == 'tab':
        read_tab(self)
    
    # Check if the format is binary
    elif self.format in ['dbl', 'flt']:
        read_bin(self)
    
    # End of the function
    return None