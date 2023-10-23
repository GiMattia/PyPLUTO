from .libraries import *

def _check_pathformat(self, path: str) -> None:
    """
    Check if the path is consistent, i.e. if the path is given 
    through a non-empty string. If the path is consistent, it is 
    converted to a Path object. Then, a check is performed to see if
    the path is a directory. The path is stored in the class as a 
    Path object self.pathdir.

    Returns
    -------

        None

    Parameters
    ----------
        - path: str
            the path to the simulation directory
    """

    # Initialize the dictionary of variables (duplicate, to be removed)
    self.D_vars = {}

    # Check if the path is a non-empty string. Then convert the 
    # string to a Path object
    if not isinstance(path, str):
        raise TypeError("Invalid data type. 'path' must be a "\
                        "non-empty string.")
    elif not path.strip():
        raise ValueError("'path' cannot be an empty string.")
    else:
        self.pathdir = Path(path)

    # Check that the path is a directory
    if not self.pathdir.is_dir():
        raise NotADirectoryError(f"Directory {self.pathdir} not found.")

    return None

def _find_format(self, datatype: str, alone: bool) -> None:
    '''
    Finds the format of the data files to load.
    If no format is given the first format found between
    dbl, vtk and flt (in this order) is taken.

    Returns
    -------

        None

    Parameters
    ----------

        - datatype: str, default None
            the file format. If None the format is recovered between (in
            order) dbl, vtk and flt.
            HDF5 and tab formats have not been implemented yet.
    '''
    if alone is not True:
        self._find_formatout(datatype)
    else:
        self._find_formatfile(datatype)
    return None



def _new_find_format(self, datatype: str, alone: bool) -> None:
    """
    Finds the format of the data files to load.
    At first, the code checks the filetype to be loaded (if fluid or
    particles). Then, depending on the filetype given, the code 
    checks if the corresponding filetype is present Depending on the
    properties of the filetype and of the type of the output (if
    fluid or particles) different checks are performed. 
    If no format is given or if the given format is not found, the
    code checks the presence other filetypes in the directory. If no
    file is found, an error is raised. CUrrent filetypes available 
    are dbl, flt, vtk, dbl.h5 and flt.h5.

    Returns
    -------

        None

    Parameters
    ----------

        - datatype: str, default None
            the file format. If None the format is recovered between 
            (in order) dbl, flt, vtk, dbl.h5 and flt.h5.
            Formats hdf5 (AMR) and tab have not been implemented yet.
        - alone: bool, default False
            if the output files are standalone or they require a .out
            file to be loaded. Only suggested for fluid files, .vtk
            format and standalone files, otherwise the code finds 
            the alone property by itself.
    """

    # Get the class name and define the possible filetypes. Also
    # initialize the self.format keyword as None
    class_name  = self.__class__.__name__
    self.format = None

    # Define the possible filetypes and set the keyword "alone"
    # accordingly
    if class_name == 'Load' or class_name == 'NewLoad':
        type_out = ['dbl','flt','vtk','dbl.h5','flt.h5']
        type_lon = ['vtk','dbl.h5','flt.h5']
        if datatype != 'vtk':
            alone = False
    elif class_name == 'LoadPart':
        alone = True
        type_out = []
        type_lon = ['dbl', 'flt', 'vtk']
    else:
        raise NameError("Invalid class name.")
    
    # Check if the given datatype is valid
    if datatype not in type_out + type_lon + [None]:
        raise ValueError(f"Invalid datatype {datatype}.")
    
    # Create the list of types to iterate over
    typeout0, typelon0 = ([], []) if \
                    datatype is not None else (type_out, type_lon)
    type_out = [datatype] if  datatype in type_out else typeout0
    type_lon = [datatype] if  datatype in type_lon else typelon0
    
    # Create the list of functions to be called (.out or alone)
    funcf  = [self._check_typeout] if len(type_out) > 0 else []
    funcf += [self._check_typelon] if len(type_lon) > 0 else []

    # Iterate over the functions to be called
    for do_check in funcf:
        do_check(datatype, type_out, type_lon)

        # Check if the format has been found
        if self.format is not None:
            # Store the charsize depending on the format
            dbl = {"dbl","dbl.h5"}
            self.charsize = 8 if self.format in dbl else 4
            return None
        
    # No file has been found, so raise an error
    if datatype is not None:
        raise FileNotFoundError(f"Type {datatype} not found.")
    else:
        raise FileNotFoundError(f"No available type has been found.")



def _new_load_vars(self, vars: bool, i: int, exout: int, endian: bool) -> None:
    """
    Loads the variables in the class. The function checks if the
    variables to be loaded are valid and then loads them. If the
    variables are not valid, an error is raised. If the variables
    are valid, the function loads them in the class through memory
    mapping. The offset and shape of each variable is computed depenging
    on the format and typefile characteristics. In case the files are
    standalone, the relevand time and grid information is loaded.

    Returns
    -------

        None

    Parameters
    ----------

        - vars: bool, default True
            if True all the variables are loaded, otherwise just a selection
            is loaded.
        - i: int
            the index of the file to be loaded.
        - exout: int
            the index of the output to be loaded.
        - endian: bool
            the endianess of the files. If True the endianess is big, 
            otherwise it is little.
    """

    # Find the class name and find the single_file filepath
    class_name  = self.__class__.__name__
    if class_name == 'Load' or class_name == 'NewLoad':
        self.filepath = self.pathdir / ('data' + self.Dinfo['endpath'][i])
    else:
        self.filepath = self.pathdir / ('particles' + self.Dinfo['endpath'][i])

    # If files in single_file format, inspect the file
    # or compute the offset and shape
    if self.Dinfo['typefile'][i] == 'single_file':
        self._compute_offset(i, endian, exout, None)

    # Check if only specific variables should be loaded
    if vars is True:
        self.load_vars = self.Dinfo['varslist'][i]
    else:
        self.load_vars = makelist(vars)

    # Loop over the variables to be loaded
    for j in self.load_vars:
    
        # Change filepath, offset and shape in case of multiple_files
        if self.Dinfo['typefile'][i] == 'multiple_files':
            self.filepath = self.pathdir / (j + self.Dinfo['endpath'][i])
            self._compute_offset(i, endian, exout, j)

        # Initialize the variables dictionary
        self._new_init_vardict(j) if self.lennout != 1 else None

        # Load the variable through memory mapping and store them in the class
        #if self.format not in {'dbl.h5','flt.h5'}:
        scrh = np.memmap(self.filepath,self.Dinfo['binformat'][i],mode="r+",
                         offset=self.offset[j], shape = self.shape[j]).T
        self._new_assign_var(i, j, scrh)
    #print(self.D_vars['tot'][0])

    return None