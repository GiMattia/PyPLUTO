from .libraries import *

def _assign_LaTeX(self, 
                  LaTeX: bool | str
                 ) -> None:
    """
    Sets the LaTeX conditions. The option 'pgf' requires XeLaTeX
    and should be used only to get vectorial figures with minimal file size.

    Returns
    -------

        None

    Parameters
    ----------

        - LaTeX: bool
            the LaTeX option
        - fontweight: str
            the fontweight of the LaTeX text
    """
    if LaTeX is True:
        mpl.rcParams['mathtext.fontset'] = 'stix'
        mpl.rcParams['font.family'] = 'STIXGeneral'

    if LaTeX == 'pgf':
        if shutil.which('latex'): print('latex installed')
        plt.switch_backend('pgf')

        pgf_preamble = r"""
        \usepackage{amsmath}
        \usepackage{amssymb}
        \usepackage{mathptmx}
        \newcommand{\DS}{\displaystyle}
        """

        mpl.rcParams.update({
            'pgf.preamble': pgf_preamble,
            'font.family': 'serif',
            'font.weight': self.fontweight,
            'text.usetex': True
        })

    return None
    
def _create_figure(self, 
                   fig: Figure | None, 
                   check: bool = True, 
                   **kwargs: Any
                  ) -> None:
    """
    Function that creates the figure associated to the Image.
    
    Parameters
    ----------

    fig : Figure | None
        The the figure instance.
    check : bool, optional
        If True, checks the parameters. The default is True.
    **kwargs : Any
        Additional parameters.
    
    Returns
    -------

    None.
    
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

    # Close the existing figure if it exists
    if plt.fignum_exists(self.nwin):
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

    return None