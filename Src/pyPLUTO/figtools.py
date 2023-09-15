from .libraries import *

def savefig(self, filename = 'img.png', bbox = 'tight'):
    self.fig.savefig(filename, bbox_inches = bbox)

def show(self, block = True):
    self.fig.show(block = block)

def text(self, text, x = 0.9, y = 0.9, ax = None, **kwargs):

    # Find figure and number of the axis
    ax = self.fig.gca() if ax is None else ax
    nax = self._check_fig(ax)

    coordinates = {'fraction': ax.transAxes, 'points': ax.transData, 'figure': self.fig.transFigure}

    xycoord = kwargs.get('xycoords', 'points')

    self._hide_text(nax, ax.texts) and xycoord != 'figure'
    coord = coordinates[xycoord]
    
    hortx = kwargs.get('horalign','left')
    vertx = kwargs.get('veralign','baseline')

    ax.text(x, y, text, c = kwargs.get('c','k'), fontsize = kwargs.get('textsize', self.fontsize),
                            transform = coord, horizontalalignment = hortx, verticalalignment = vertx)

    return None

