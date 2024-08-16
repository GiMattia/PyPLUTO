from .libraries  import *

class Image:
    """
    Class that creates a new figure and sets the LaTeX 
    conditions and blablabla...

    - style: str, default 'default'
        The style of the figure. Possible values are: 'seaborn', 'ggplot',
        'fivethirtyeight', 'bmh', 'grayscale', 'dark_background', 'classic',
        etc.
    """

    def __init__(self, 
                 LaTeX: bool | str = True, 
                 text: bool = False, 
                 fig: Figure | None = None, 
                 **kwargs: Any
                ) -> None:

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
        self._create_figure(fig, text, **kwargs)
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
        - set_axis
          Changes the parameter of a specific subplot
        - plot
          Plots one line in a subplot
        - legend
          Places one legend in a subplot
        - display
          Plots a 2D quantity in a subplot
        - colorbar
          Places a colorbar in a subplot or next to a subplot
        - zoom
          Creates an inset zoom region of a subplot
        - text
          Places the text in the figure or in a subplot
        - savefig
          Saves the figure
        - show
          Shows the figure
        
        

        Please refrain from using "private" methods and attributes.
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


    

    

    
