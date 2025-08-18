from .imagestate import ImageState


class ImageMixin:
    """Mixin class for image handling. It provides properties and methods
    related to the image state and axes."""

    state: ImageState

    @property
    def LaTeX(self):
        """Get the LaTeX state of the image."""
        return self.state.LaTeX

    @LaTeX.setter
    def LaTeX(self, value):
        """Set the LaTeX state of the image."""
        self.state.LaTeX = value

    @property
    def style(self):
        return self.state.style

    @style.setter
    def style(self, value):
        self.state.style = value

    @property
    def ax(self):
        return self.state.ax

    @ax.setter
    def ax(self, value):
        self.state.ax = value

    @property
    def color(self):
        return self.state.color

    @color.setter
    def color(self, value):
        self.state.color = value

    @property
    def dictcol(self):
        return self.state.dictcol

    @dictcol.setter
    def dictcol(self, value):
        self.state.dictcol = value

    @property
    def fig(self):
        return self.state.fig

    @fig.setter
    def fig(self, value):
        self.state.fig = value

    @property
    def figsize(self):
        return self.state.figsize

    @figsize.setter
    def figsize(self, value):
        self.state.figsize = value

    @property
    def fontsize(self):
        return self.state.fontsize

    @fontsize.setter
    def fontsize(self, value):
        self.state.fontsize = value

    @property
    def legpar(self):
        return self.state.legpar

    @legpar.setter
    def legpar(self, value):
        self.state.legpar = value

    @property
    def legpos(self):
        return self.state.legpos

    @legpos.setter
    def legpos(self, value):
        self.state.legpos = value

    @property
    def ncol0(self):
        return self.state.ncol0

    @ncol0.setter
    def ncol0(self, value):
        self.state.ncol0 = value

    @property
    def nline(self):
        return self.state.nline

    @nline.setter
    def nline(self, value):
        self.state.nline = value

    @property
    def nrow0(self):
        return self.state.nrow0

    @nrow0.setter
    def nrow0(self, value):
        self.state.nrow0 = value

    @property
    def ntext(self):
        return self.state.ntext

    @ntext.setter
    def ntext(self, value):
        self.state.ntext = value

    @property
    def nwin(self):
        return self.state.nwin

    @nwin.setter
    def nwin(self, value):
        self.state.nwin = value

    @property
    def setax(self):
        return self.state.setax

    @setax.setter
    def setax(self, value):
        self.state.setax = value

    @property
    def setay(self):
        return self.state.setay

    @setay.setter
    def setay(self, value):
        self.state.setay = value

    @property
    def set_size(self):
        return self.state.set_size

    @set_size.setter
    def set_size(self, value):
        self.state.set_size = value

    @property
    def shade(self):
        return self.state.shade

    @shade.setter
    def shade(self, value):
        self.state.shade = value

    @property
    def tickspar(self):
        return self.state.tickspar

    @tickspar.setter
    def tickspar(self, value):
        self.state.tickspar = value

    @property
    def tight(self):
        return self.state.tight

    @tight.setter
    def tight(self, value):
        self.state.tight = value

    @property
    def vlims(self):
        return self.state.vlims

    @vlims.setter
    def vlims(self, value):
        self.state.vlims = value

    @property
    def xscale(self):
        return self.state.xscale

    @xscale.setter
    def xscale(self, value):
        self.state.xscale = value

    @property
    def yscale(self):
        return self.state.yscale

    @yscale.setter
    def yscale(self, value):
        self.state.yscale = value
