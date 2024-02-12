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



def _find_format(self, datatype: str | None, 
                       alone: bool | None) -> None:
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

    # Initialization or declaration of variables
    type_out: list[str] # The list of possible filetypes for .out files
    type_lon: list[str] # The list of possible filetypes for standalone files
    typeout0: list[str] # The list of checked filetypes for .out files
    typelon0: list[str] # The list of checked filetypes for standalone files
    funcf: list[Callable] # The list of functions to be called
    class_name: str  = self.__class__.__name__ # The class name
    dbl: set[str] = {"dbl","dbl.h5"} # The set of double filetypes
    dict_func: dict[str, list[str]] # The dictionary of functions
    funcf: list[Callable] # The list of functions to be called
    scrh: str # The error message
    

    # Define the possible filetypes and set the keyword "alone" accordingly
    if class_name == 'Load':
        type_out = ['dbl','flt','vtk','dbl.h5','flt.h5','tab']
        type_lon = ['vtk','dbl.h5','flt.h5','tab']
        if datatype in {'dbl','flt'}:
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

    typeout0 , typelon0 = ([], []) if \
                    datatype is not None else (type_out, type_lon)
    type_out = [datatype] if  datatype in type_out else typeout0
    type_lon = [datatype] if  datatype in type_lon else typelon0
    
    # Create the list of functions to be called (.out or alone)
    funcf = [_check_typeout] if len(type_out) > 0 \
                                   and alone is not True else []
    funcf += [_check_typelon] if len(type_lon) > 0 \
                                   and alone is not False else []
    
    # Define the dictionary for the function argument
    dict_func = {'_check_typeout': type_out, '_check_typelon': type_lon}

    # Iterate over the functions to be called
    for do_check in funcf:
        do_check(self, dict_func[do_check.__name__])

        # Check if the format has been found
        if self.format is not None:
            # Store the charsize depending on the format
            self._charsize = 8 if self.format in dbl else 4
            return None
        
    # No file has been found, so raise an error
    scrh = f"No available type has been found in {self.pathdir}."
    if datatype is not None:
        scrh = f"Type {datatype} not found."
    raise FileNotFoundError(scrh)

def _check_typeout(self, 
                   type_out: list[str]
                  ) -> None:
    """
    Loops over possible formats in order to find, at first the 
    grid.out file, then the datatype.out file. If the datatype.out
    file is found, the file format is selected and the flag alone is
    set to False.

    Returns
    -------

        None

    Parameters
    ----------

        - datatype: str
            the format selected by the user (if not then is None)
        - type_out: [str]
            the list of possible formats for the output file
        - type_lon: [str]
            the list of possible formats for the output file
            (not used here but in _check_typelon)
    """
    
    # Loop over the possible formats
    for try_type in type_out:

        # Check if the grid.out file is present
        self._pathgrid = self.pathdir / 'grid.out'
        self._pathdata = self.pathdir / (try_type + '.out')
        
        # Check if the datatype.out file is present
        if self._pathdata.is_file() and self._pathgrid.is_file():
            self.format = try_type
            self._alone = False
            break
        
    return None



def _check_typelon(self, type_lon: list[str]) -> None:
    """
    Loops over posisble formats in order to find matching files
    with the datatype. If the file is found, the file format is
    selected and the flag alone is set to True.

    Returns
    -------

        None
    
    Parameters
    ----------

        - datatype: str
            the format selected by the user (if not then is None)
        - type_out: [str]
            the list of possible formats for the output file
            (not used here but in _check_typeout)
        - type_lon: [str]
            the list of possible formats for the output file
    """

    # Loop over the possible formats
    for try_type in type_lon:

        # Create the pattern to be searched
        pattern: Path = self.pathdir / ('*.*.' + try_type)
        self._matching_files = glob.glob(str(pattern))

        # Check if the file is present
        if self._matching_files:
            self.format = try_type
            self._alone = True
            break

    return None



