from .libraries  import *

class Image:
    """
    Class that creates a new figure and sets the LaTeX
    conditions, as well as the matplotlib style.
    Every Image is associated to a figure object and only one in order to
    avoid confusion between images and figures. If you want to create multiple
    figures, you have to create multiple Image objects.

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
    - LaTeX: bool | str, default False
        The LaTeX option. Is True is selected, the default LaTeX font
        is used. If 'pgf' is selected, the pgf backend is used to save pdf
        figures with minimal file size. If XeLaTeX is not installed and the
        'pgf' option is selected, the LaTeX option True is used as backup
        strategy.
    - numcolor: int
        The number of colors.
    - nwin: int, default 1
        The window number.
    - oldcolor: bool
        if True, the old colors are used
    - style: str, default 'default'
        The style of the figure. Possible values are: 'seaborn', 'ggplot',
        'fivethirtyeight', 'bmh', 'grayscale', 'dark_background', 'classic',
        etc.
    - suptitle: str, default None
        The super title of the figure.
    - suptitlesize: str | int, default 'large'
        The figure title size.
    - tight: bool, default True
        If True, the tight layout is used.
    - withblack: bool
        If True, the black color is used as first color.
    - withwhite: bool
        If True, the white color is used as first color.

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: create an empty image

        >>> import pyPLUTO as pp
        >>> I = pp.Image()

    - Example #2: create an image with the pgf backend

        >>> import pyPLUTO as pp
        >>> I = pp.Image(LaTeX = 'pgf')

    - Example #3: create an image with the LaTeX option True

        >>> import pyPLUTO as pp
        >>> I = pp.Image(LaTeX = True)

    - Example #4: create an image with fixed size

        >>> import pyPLUTO as pp
        >>> I = pp.Image(figsize = [5,5])

    - Example #5: create an image with a title

        >>> import pyPLUTO as pp
        >>> I = pp.Image(suptitle = 'Title')

    """

    def __init__(self,
                 LaTeX: bool | str = True,
                 check: bool = True,
                 text: bool = False,
                 fig: Figure | None = None,
                 **kwargs: Any
                ) -> None:
        
        # Check parameters
        param = {'close','figsize','fontsize','numcolor','nwin','oldcolor',
                 'style','suptitle','suptitlesize','tight','withblack',
                 'withwhite'}
        if check is True:
            check_par(param, '__init__', **kwargs)

        self.fontsize: int = 17 # fontsize
        self.tight: bool = True # tight layout
        self.figsize: list[float] = [8,5] # figure size
        self._set_size: bool = False # if True the figure size is set
        self.nwin: int = 1 # window number
        self.nrow0: int = 0 # number of rows in the figure
        self.ncol0: int = 0 # number of columns in the figure
        self.ax: list[Axes] = [] # list of axes in the figure
        self.vlims: list[list[float]] = [] # colorscale limits
        self.nline: list[int] = [] # number of lines in the axis
        self.ntext: list[Any | None] = [] # text in the axis
        self.setax: list[Any |int] = [] # keyword for the range in x-direction
        self.setay: list[Any |int] = [] # keyword for the range in y-direction
        self.legpos: list[int | str | None] = [] # legend position
        self.legpar: list[list[float]] = [] # legend parameters
        self.tickspar: list[Any | int] = [] # ticks parameters
        self.shade: list[str] = [] # shading of the plot
        self.fontweight: str = kwargs.get('fontweight','normal') # fontweight
        self.tg: bool # tight layout of the figure
        self.fig: Figure # the figure associated to the image
        self.anim_var: NDArray # the variable to be animated
        self.anim_ax: Axes # the axes of the animation
        self.slider: Slider # the slider
        self.anim_pcm: Any # the animation collection

        # Set the style of the figure
        plt.style.use(kwargs.get('style','default'))

        # Set the options for the color lines
        self.color = self._choose_colorlines(kwargs.get('numcolor',10),
                                             kwargs.get('oldcolor',False),
                                             kwargs.get('withblack',False),
                                             kwargs.get('withwhite',False))

        # Set the LaTeX option
        self._assign_LaTeX(LaTeX)

        # Create the figure
        self._create_figure(fig, **kwargs)
        if text is not False:
            print(f"Creating Figure in window {self.nwin}")


    def __getattr__(self, name):
        try:
            return getattr(self, f'_{name}')
        except:
            raise AttributeError(f"'Image' object has no attribute '{name}'")


    def __str__(self):
        return rf"""
        Image class.
        It plots the data.

        Image properties:
        - Figure size        (figsize)       {self.figsize}
        - Window number      (nwin)          {self.nwin}
        - Number of subplots (nrow0 x ncol0) {self.nrow0} x {self.ncol0}
        - Global fontsize    (fontsize)      {self.fontsize}

        Public methods available:

        - create_axes
            Adds a set of [nrow,ncol] subplots to the figure.
        - colorbar
            Places a colorbar in a subplot or next to a subplot.
        - contour
            Plots a contour plot in a subplot.
        - display
            Plots a 2D quantity in a subplot.
        - interactive
            Creates an interactive plot with a slider to change the data.
        - legend
            Places one legend in a subplot.
        - set_axis
            Changes the parameter of a specific subplot.
        - plot
            Plots one line in a subplot.
        - savefig
            Saves the figure in a file.
        - scatter
            Plots a scatter plot in a subplot.
        - streamplot
            Plots a stream plot in a subplot.
        - text
            Places the text in the figure or in a subplot.
        - zoom
            Creates an inset zoom region of a subplot.

        Public attributes available:

        - ax:
            The list of relevant axes in the figure.
        - fig
            The figure associated to the image.
        - fontsize
            The fontsize in the figure.
        - fontweight
            The fontweight in the figure.
        - nwin
            The window number.
        - tg
            The tight layout of the figure.

        Please do not use 'private' methods and attributes if not absolutely
        necessary.
        """

    from .setaxes    import create_axes, set_axis
    from .plot1d     import plot, legend
    from .plot2d     import display, scatter, colorbar, _set_cscale
    from .plotzoom   import zoom
    from .imagetools import savefig, show, text
    from .interact   import interactive, _update_slider
    from .plotlines  import contour, streamplot
    from .figure     import _create_figure, _assign_LaTeX, _choose_colorlines
    from .h_image    import _add_ax, _hide_text
    from .h_image    import _set_xrange, _set_yrange, _assign_ax
