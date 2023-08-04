def _find_format(self, datatype):
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

    # Check if the file grid.out exists and that the path is a directory
    if not self.pathdir.is_dir():
        raise NotADirectoryError(f'directory {self.pathdir} not found!')
    self.pathgrid = self.pathdir / 'grid.out'
    if not self.pathgrid.is_file():
        raise FileNotFoundError(f'directory {self.pathdir} has no grid.out!')

    # Recover the file format needed to load the files
    if datatype is None:
        self.rec_format()
    else:
        self.pathdata = self.pathdir  / (datatype + '.out')
        if self.pathdata.is_file():
            self.format = datatype
        else:
            raise FileNotFoundError(f'file {datatype}.out not found!')

    # Store the charsize depending on the format
    self.charsize = 8 if self.format == 'dbl' else 4
    return None