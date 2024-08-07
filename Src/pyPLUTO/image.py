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

        self.fontsize: int = 17
        self.tight: bool = True
        self.figsize: list[float] = [8,5]
        self._set_size: bool = False
        self.nwin: int = 1
        self.nrow0: int = 0
        self.ncol0: int = 0
        self.ax: list[Axes] = []
                                # black, red, blue, cyan, green, orange
      
        
        self.vlims: list[list[float]] = []
        self.nline: list[int] = []
        self.ntext: list[Any | None] = []
        self.setax: list[Any |int] = []
        self.setay: list[Any |int] = []
        self.legpos: list[int | str | None] = []
        self.legpar: list[list[float]] = []
        self.tickspar: list[Any | int] = []
        self.shade: list[str] = []
        self.fontweight: str = kwargs.get('fontweight','normal')
        self.tg: bool
        self.fig: Figure
        self.anim_var: NDArray
        self.anim_ax: Axes
        self.slider: Slider
        self.anim_pcm: Any

        plt.style.use(kwargs.get('style','default'))

        self.color = self._choose_colorlines(kwargs.get('numcolor',10), 
                                             kwargs.get('oldcolor',False),
                                             kwargs.get('withblack',False),
                                             kwargs.get('withwhite',False))

        self._assign_LaTeX(LaTeX)
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

        Public attributes available: WIP...

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
        

        Please refrain from using "private" methods and attributes.
        """
    
    from .setaxes    import create_axes, set_axis
    from .plot1d     import plot, legend
    from .plot2d     import display, scatter, colorbar, _set_cscale
    from .plotzoom   import zoom
    from .imagetools import savefig, show, text
    from .interact   import interactive, _update_slider
    from .plotlines  import contour
    from .figure     import _create_figure, _assign_LaTeX
    from .h_image    import _add_ax, _hide_text, _choose_colorlines
    from .h_image    import _set_xrange, _set_yrange, _assign_ax


    

    

    
