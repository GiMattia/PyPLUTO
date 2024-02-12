from .libraries  import *
from .figure     import _create_figure, _assign_LaTeX
from .setaxes    import create_axes, set_axis
from .plot1d     import plot, legend
from .plot2d     import display, scatter, colorbar
from .plotzoom   import zoom
from .pytools    import copy_docstring
from .imagetools import savefig, show, text
from .interact   import interactive, _update_slider
from .h_image    import _check_fig, _add_ax, _hide_text, _set_parax
from .h_image    import _set_xrange, _set_yrange, _assign_ax

class Image:
    """
    Class that creates a new figure and sets the LaTeX 
    conditions and blablabla...
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
        self.color: list[str] = ['k','#d7263d','#1815c5',
                                 '#12e3c0','#3f6600','#f67451']
        
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
        self.anim_pcm: Any # FIXME: Type

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
    
    @copy_docstring(create_axes)
    def create_axes(self,*args,**kwargs):
        return create_axes(self,*args,**kwargs)

    @copy_docstring(set_axis)
    def set_axis(self,*args,**kwargs):
        return set_axis(self,*args,**kwargs)
    
    @copy_docstring(plot)
    def plot(self,*args,**kwargs):
        return plot(self,*args,**kwargs)
    
    @copy_docstring(legend)
    def legend(self,*args,**kwargs):
        return legend(self,*args,**kwargs)
    
    @copy_docstring(display)
    def display(self,*args,**kwargs):
        return display(self,*args,**kwargs)
    
    @copy_docstring(scatter)
    def scatter(self,*args,**kwargs):
        return scatter(self,*args,**kwargs)
    
    @copy_docstring(colorbar)
    def colorbar(self,*args,**kwargs):
        return colorbar(self,*args,**kwargs)
    
    @copy_docstring(savefig)
    def savefig(self,*args,**kwargs):
        return savefig(self,*args,**kwargs)
    
    @copy_docstring(show)
    def show(self,*args,**kwargs):
        return show(self,*args,**kwargs)
    
    @copy_docstring(text)
    def text(self,*args,**kwargs):
        return text(self,*args,**kwargs)
    
    @copy_docstring(zoom)
    def zoom(self,*args,**kwargs):
        return zoom(self,*args,**kwargs)
    
    @copy_docstring(interactive)
    def interactive(self,*args,**kwargs):
        return interactive(self,*args,**kwargs)
    
    @copy_docstring(_update_slider)
    def _update_slider(self,*args,**kwargs):
        return _update_slider(self,*args,**kwargs)
    
    def _create_figure(self,*args,**kwargs):
        return _create_figure(self,*args,**kwargs)
    
    def _assign_LaTeX(self,*args,**kwargs):
        return _assign_LaTeX(self,*args,**kwargs)
    
    def _check_fig(self,*args,**kwargs):
        return _check_fig(self,*args,**kwargs)
    
    def _add_ax(self,*args,**kwargs):
        return _add_ax(self,*args,**kwargs)
    
    def _hide_text(self,*args,**kwargs):
        return _hide_text(self,*args,**kwargs)
    
    def _set_parax(self,*args,**kwargs):
        return _set_parax(self,*args,**kwargs)
    
    def _set_xrange(self,*args,**kwargs):
        return _set_xrange(self,*args,**kwargs)
    
    def _set_yrange(self,*args,**kwargs):
        return _set_yrange(self,*args,**kwargs)
    
    def _assign_ax(self,*args,**kwargs):
        return _assign_ax(self,*args,**kwargs)
    

    

    

    
