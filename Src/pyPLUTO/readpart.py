from .libraries import *

def _store_bin_particles(self, i: int) -> None:
    """
    Routine to store the particles data. The routine loops over the
    variables and stores the data in the dictionary from the 'tot' key.
    Then the 'tot' keyword is removed from the dictionary for memory and
    clarity reasons.

    Returns
    -------

        None
    
    Parameters
    ----------

        - i: int
            the index of the file to be loaded. 
    """

    # Mask the array (to be fixed for multiple loadings)
    #masked_array = np.ma.masked_array(self._d_vars['tot'][0].astype('int'), 
    #                                                 np.isnan(self._d_vars['tot'][0]))

    # Start with column 0 (id) and loop over the variable names
    ncol = 0
    for j, var in enumerate(self._d_info['varskeys'][i]):

        # Compute the size of the variable and store the data
        szvar = self._vardim[j]
        print(np.shape(self._d_vars[var]), szvar)
        if self._lennout != 1:
            # To be fixed for multiple loadings
            raise NotImplementedError('multiple loading not implemented yet')
            #self._d_vars[var][i][:] = self._d_vars['tot'][i][ncol:ncol+szvar]
        else:
            self._d_vars[var][:] = self._d_vars['tot'][ncol:ncol+szvar]

        # Update the column counter
        ncol += szvar

    # Remove the 'tot' key from the dictionary
    del self._d_vars['tot']

    return None