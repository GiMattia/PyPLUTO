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
        The LaTeX option. Is True is selected, the default LaTeX font
        is used. If 'pgf' is selected, the pgf backend is used to save pdf
        figures with minimal file size. If XeLaTeX is not installed and the 
        'pgf' option is selected, the LaTeX option True is used as backup 
        strategy.

    Notes
    -----

    - None

    ----

    Examples
    ========

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

    # LaTeX inatalled, try now to set the pgf backend
    if LaTeX == 'pgf':
        # Set the pgf backend
        try:
            plt.switch_backend('pgf')

            # Preamble (LaTeX commands and packages)
            pgf_preamble = r"""
            \usepackage{amsmath}
            \usepackage{amssymb}
            \usepackage{mathptmx}
            \usepackage{siunitx}
            \usepackage[T1]{fontenc}
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
            warn = "The LaTeX = True option is not available."
            warnings.warn(warn, UserWarning)

    # End of the function
    return None


def _choose_colorlines(self, 
                       numcolor:  int,
                       oldcolor:  bool,
                       withblack: bool,
                       withwhite: bool
                      ) -> list[str]:
    """
    Chooses the colors for the lines. Depending on the number of colors
    and the option 'oldcolor', the colors are:

    - black, red, blue, cyan, green, orange (oldcolor = True)
    - a new list of colors (oldcolor = False)

    Both color lists are suited for all types of color vision deficiencies.

    Returns
    -------

    - colors: list[str]
        The list of colors for the lines.

    Parameters
    ----------

    - numcolor: int
        The number of colors.
    - oldcolor: bool
        If True, the old colors are used.
    - withblack: bool
        If True, the black color is used as first color.
    - withwhite: bool
        If True, the white color is used as first color.

    Notes
    -----

    - The withblack and withwhite options are only used if oldcolor = False
        and they cannot be used together (priority goes to black).

    ----

    Examples
    ========

    - Example #1: oldcolor = True
        
        >>> _choose_colorlines(6, True)

    - Example #2: oldcolor = False, withblack = True
        
        >>> _choose_colorlines(6, False, True)

    - Example #3: 12 colors, oldcolor = False, withwhite = True

        >>> _choose_colorlines(12, False, False, True)

    """

    # Old colors
    if oldcolor:    # black, red, blue, cyan, green, orange
        return ['k','#d7263d','#1815c5', '#12e3c0','#3f6600','#f67451']

    # New colors dictionary (black and white included)
    self.dictcol = { 0: '#ffffff',  1: '#e8ecfb',  2: '#d9cce3',  3: '#d1bbd7', 
                     4: '#caaccb',  5: '#ae76a3',  6: '#aa6f9e',  7: '#994f88',  
                     8: '#882e72',  9: '#0104fe', 10: '#1e3888', 11: '#437dbf',
                    12: '#5289c7', 13: '#6195cf', 14: '#7bafde', 15: '#4eb265',
                    16: '#90c987', 17: '#cae0ab', 18: '#f7f056', 19: '#f7cb45',
                    20: '#f6c141', 21: '#f4a736', 22: '#f1932d', 23: '#ee8026',
                    24: '#e8601c', 25: '#e65518', 26: '#dc050c', 27: '#a5170e',
                    28: '#72190e', 29: '#42150a', 30: '#777777', 31: '#000000',
                    32: '#0104fe'}

    # Colors are ordered to avoid color vision deficiencies           
    lstc = [9,26,15,23,14,17,6,25,28,18,11,2,8,16,10,21,7,27,4,13,19,29,1,30]

    # Black and white addition
    lstc = [0] + lstc if withwhite else [31] + lstc if withblack else lstc

    # End of function, return the colors
    return [self.dictcol[lstc[i]] for i in range(numcolor)]
    
    
def _create_figure(self, 
                   fig: Figure | None,  
                   **kwargs: Any
                  ) -> None:
    """
    Function that creates the figure associated to an Image instance. It is 
    called by default when the Image class is instantiated.

    Returns
    -------

    - None
    
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
    - suptitlesize: str | int, default 'large'
        The figure title size.
    - tight: bool, default True
        If True, the tight layout is used.

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: Create a new figure

        >>> _create_figure()

    - Example #2: Associate an Image to an existing figure

        >>> _create_figure(fig = fig)

    - Example #3: Create a new figure with different size and a figure title

        >>> _create_figure(suptitle = 'Super Title', figsize = [10,5])

    - Example #4: Create a new figure with a specific window number

        >>> _create_figure(nwin = 2)

    """

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
        self.fig.suptitle(kwargs['suptitle'], 
                          fontsize = kwargs.get('suptitlesize','large'))

    # Tight layout
    if self.tight is True:
        self.fig.tight_layout()

    # End of the function
    return None
