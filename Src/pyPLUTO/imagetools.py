from .libraries import *

def savefig(self, filename = 'img.png', bbox = 'tight'):
    self.fig.savefig(filename, bbox_inches = bbox)

def show(self, block: bool = True):
    self.fig.show(block = block) # type: ignore

def text(self, text, x = 0.9, y = 0.9, ax = None, **kwargs):

    # Import methods from other files
    from .h_image import _check_fig, _hide_text

    # Find figure and number of the axis
    ax = self.fig.gca() if ax is None else ax
    nax = _check_fig(self, ax)

    coordinates = {'fraction': ax.transAxes, 'points': ax.transData, 'figure': self.fig.transFigure}

    xycoord = kwargs.get('xycoords', 'points')

    if xycoord != 'figure': _hide_text(self, nax, ax.texts)
    coord = coordinates[xycoord]
    
    hortx = kwargs.get('horalign','left')
    vertx = kwargs.get('veralign','baseline')

    ax.text(x, y, text, c = kwargs.get('c','k'), fontsize = kwargs.get('textsize', self.fontsize),
                            transform = coord, horizontalalignment = hortx, verticalalignment = vertx)

    return None

