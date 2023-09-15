from .libraries import *

def _find_formatfile(self, datatype: str) -> None:

    class_name = self.__class__.__name__
    if class_name == 'Load':
        raise NotImplementedError('Standalone fluid file load has not been implemented yet')
    elif class_name == 'LoadPart':
        if datatype is None:
            raise NotImplementedError('particles rec format has not been implemented yet')
        else:
            pattern = self.pathdir / ('particles.*.' + datatype)

            matching_files = glob.glob(str(pattern))
        if not matching_files:
            raise FileNotFoundError(f'file particles.*.{datatype} not found!')
        else:
            self.format = datatype 
            if self.format != 'vtk':
                raise NotImplementedError('non-vtk files have not been implemented yet')
            self.charsize = 8 if self.format == 'dbl' else 4
    else:
        raise NameError('Invalid class name')
    return None

def _read_varsfile(self, nout, vars):
    '''
    Reads the 'filetype'.out file and stores the relevant information within the
    class. Such information are the time array, the output variables, the file
    type (single or multiples), the endianess, the simulation path and the bin
    format. All these information are relevant in order to open the output files
    and access the data.

    Returns
    -------
        None

    Parameters
    ----------
        - nout: int, default 'last'
            the output file to be opened. If default ('last'), the last file
    '''

    # Initialize the info dictionary
    self.Dinfo = {}

    return None
    