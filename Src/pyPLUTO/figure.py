from .libraries import *

def _assign_LaTeX(self, 
                  LaTeX: bool | str
                 ) -> None:
    """
    Sets the LaTeX conditions. The option 'pgf' requires XeLaTeX
    and should be used only to get vectorial figures with minimal file size.

    Returns
    -------

    - None

    Parameters
    ----------

    - LaTeX: bool | str, default False
        the LaTeX option. Is True is selected, the default LaTeX font
        is used. If 'pgf' is selected, the pgf backend is used.
        If XeLaTeX is not installed and the 'pgf' option is selected, the 
        LaTeX option True is used as backup strategy.

    Notes
    -----

    - None

    Examples
    --------

    - Example #1: LaTeX option True
        
        >>> _assign_LaTeX(True)

    - Example #2: LaTeX option 'pgf'
        
        >>> _assign_LaTeX('pgf')

    """

    # LaTeX option 'pgf' (requires XeLaTeX)
    if LaTeX == 'pgf':

        # Check if XeLaTeX is installed
        # If not, the LaTeX option True is used
        if not shutil.which('latex'): 
            warn = "LaTeX not installed, switching to LaTeX = True"
            warnings.warn(warn, UserWarning)
            LaTeX = True

        # Set the pgf backend
        try:
            plt.switch_backend('pgf')

            # Preamble (LaTeX commands and packages)
            pgf_preamble = r"""
            \usepackage{amsmath}
            \usepackage{amssymb}
            \usepackage{mathptmx}
            \usepackage[detect-all]{siunitx}
            \newcommand{\DS}{\displaystyle}
            """

            # Update the rcParams
            mpl.rcParams.update({
                'pgf.preamble': pgf_preamble,
                'font.family': 'serif',
                'font.weight':  self.fontweight,
                'text.usetex':  True
            })

        # If errors occur, the LaTeX option True is used and a warning 
        # message is displayed
        except: 
            str1 = ("XeLaTeX is required to use the pgf backend.\n" 
                    "Please, install XeLaTeX and try again.")
            str2 = "The pgf backend is not available."
            warn = str1 if LaTeX is True else str2
            warnings.warn(warn, UserWarning)
            LaTeX = True

    # LaTeX option True: default LaTeX font
    if LaTeX is True:
        try:
            mpl.rcParams['mathtext.fontset'] = 'stix'
            mpl.rcParams['font.family']      = 'STIXGeneral'
        except:
            warn = "The LaTeX option is not available."
            warnings.warn(warn, UserWarning)

    # End of the function
    return None
    
    
def _create_figure(self, 
                   fig: Figure | None, 
                   check: bool = True, 
                   **kwargs: Any
                  ) -> None:
    """
    Function that creates the figure associated to the Image. It is called 
    by default when the Image class is instantiated.

    Returns
    -------

    - None.
    
    Parameters
    ----------

    - check: bool, default True
        If enabled perform a check on the method's parameters, raising a 
        warning if a parameter is not present among the set of available 
        parameters.
    - close: bool, default True
        If True, the existing figure with the same window number is closed.
    - fig: Figure | None, default None
        The the figure instance. If not None, the figure is used (only 
        if we need to associate an Image to an existing figure).
    - figsize: list[float], default [8,5]
        The figure size.
    - fontsize: int, default 17
        The font size.
    - nwin: int, default 1
        The window number.
    - suptitle: str, default None
        The super title of the figure.
    - style: str, default 'default'
        The style of the figure. Possible values are: 'seaborn', 'ggplot',
        'fivethirtyeight', 'bmh', 'grayscale', 'dark_background', 'classic',
        etc.
    - tight: bool, default True
        If True, the tight layout is used.

    Notes
    -----

    - None.

    Examples
    --------

    - Example #1: Create a new figure

        >>> _create_figure()

    - Example #2: Associate an Image to an existing figure

        >>> _create_figure(fig = fig)

    - Example #3: Create a new figure with a super title and different size

        >>> _create_figure(suptitle = 'Super Title', figsize = [10,5])

    - Example #4: Create a new figure with a specific window number

        >>> _create_figure(nwin = 2)

    """

    # Check parameters
    param = {'close','fig','figsize','fontsize','nwin','style','suptitle',
             'tight'}
    if check is True:
        check_par(param, 'create_fig', **kwargs)

    plt.style.use(kwargs.get('style','default'))

    # Changes keywords if figure has been already assigned
    if isinstance(fig,Figure):
        self.figsize  = [fig.get_figwidth(),fig.get_figheight()]
        self.fontsize = plt.rcParams['font.size']
        self.nwin     = fig.number
        self.tg       = fig.get_tight_layout()

    # If figsize is assigned, a keyword fixes it
    if 'figsize' in kwargs:
        self._set_size = True

    # Keywords assigned
    self.figsize  = kwargs.get('figsize',self.figsize)
    self.fontsize = kwargs.get('fontsize',self.fontsize)
    self.nwin     = kwargs.get('nwin',self.nwin)
    self.tight    = kwargs.get('tight',self.tight)

    # Close the existing figure if it exists (and 'close' is enabled)
    if plt.fignum_exists(self.nwin) and kwargs.get('close',True) is True:
        plt.close(self.nwin)

    # Create a new figure instance with the provided window number   
    self.fig = plt.figure(self.nwin, figsize=(self.figsize[0],self.figsize[1]))
    plt.rcParams.update({'font.size': self.fontsize})

    # Suptitle
    if 'suptitle' in kwargs:
        self.fig.suptitle(kwargs['suptitle'])

    # Tight layout
    if self.tight is True:
        self.fig.tight_layout()

    # End of the function
    return None