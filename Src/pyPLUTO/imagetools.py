from .libraries import *

def savefig(self, 
            filename: str = 'img.png', 
            bbox: str | None = 'tight'
           ) -> None:
    """
    Creation of a .png image file of the figure created with the Image class.

    Returns
    -------

    - None

    Parameters
    ----------

    - bbox: {'tight', None}, default 'tight'
        Crops the white borders of the Image to create a more balanced image
        file
    - filename: str, default 'img.png'
        The name of the saved image file

    Notes
    -----

    - None

    Examples
    --------

    - Example #1: save an empty image

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> I.savefig('namefile.png')
    
    """

    self.fig.savefig(filename, bbox_inches = bbox)

    return None

def show(self, 
         block: bool = True
        ) -> None:
    """
    Outputs on screen the figure created with Image class.

    Returns
    -------

    - None

    Parameters
    ----------

    - block: bool, default True
        Blocks the functioning of the terminal from which the script has been
        launched

    Notes
    -----

    - None

    Examples
    --------

    - Example #1: show an empty image

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> I.show()
    
    """

    warn = "Image show is deprecated, please use pp.show instead"
    warnings.warn(warn, DeprecationWarning)
    self.fig.show()

    return None

def text(self, 
         text: str, 
         x: float = 0.85, 
         y: float = 0.85, 
         ax: Axes | None = None,
         **kwargs: Any
        ) -> None:
    """
    Insertion of a text box inside the figure created with Image class.

    Returns
    -------

    - None

    Parameters
    ----------

    - ax: axis object, default None
        The axis where to insert the text box. If None, the last considered axis 
        will be used.
    - c: str, default 'k'
        Determines the text color.
    - horalign
    - text (not optional): str
        The text that will appear on the text box
    - textsize: float, default fontsize
        Sets the text fontsize. The default value corresponds to the value of
        the actual fontsize in the figure.
    - veralign
    - x: float, default 0.85
        The horizontal starting position of the text box, in units of figure
        size.
    - xycoords
    - y: float, default 0.85
        The vertical starting position of the text box, in units of figure size.

    Notes
    -----

    - None

    Examples
    --------

    - Example #1: create a simple text box
    bla bla bla      
    
    """

    # Import methods from other files
    from .h_image import _hide_text

    # Find figure and number of the axis
    ax, nax = self._assign_ax(ax, **kwargs)

    coordinates = {'fraction': ax.transAxes, 'points': ax.transData, 'figure': self.fig.transFigure}

    xycoord = kwargs.get('xycoords', 'fraction')

    if xycoord != 'figure': _hide_text(self, nax, ax.texts)
    coord = coordinates[xycoord]
    
    hortx = kwargs.get('horalign','left')
    vertx = kwargs.get('veralign','baseline')

    ax.text(x, y, text, c = kwargs.get('c','k'), fontsize = kwargs.get('textsize', self.fontsize),
                            transform = coord, horizontalalignment = hortx, verticalalignment = vertx)

    return None

