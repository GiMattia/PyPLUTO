"""Mixin class for image handling."""

from .imagestate import ImageState


class ImageMixin:
    """Mixin class for image handling.

    It provides properties and methods related to the image state and axes."""

    state: ImageState

    @property
    def ax(self):
        """Get the ax attribute of the image."""
        return self.state.ax

    @ax.setter
    def ax(self, value):
        """Set the ax attribute of the image."""
        self.state.ax = value

    @property
    def color(self):
        """Get the color attribute of the image."""
        return self.state.color

    @color.setter
    def color(self, value):
        """Set the color attribute of the image."""
        self.state.color = value

    @property
    def dictcol(self):
        """Get the dictcol attribute of the image."""
        return self.state.dictcol

    @dictcol.setter
    def dictcol(self, value):
        """Set the dictcol attribute of the image."""
        self.state.dictcol = value

    @property
    def fig(self):
        """Get the fig attribute of the image."""
        return self.state.fig

    @fig.setter
    def fig(self, value):
        """Set the fig attribute of the image."""
        self.state.fig = value

    @property
    def figsize(self):
        """Get the figsize attribute of the image."""
        return self.state.figsize

    @figsize.setter
    def figsize(self, value):
        """Set the figsize attribute of the image."""
        self.state.figsize = value

    @property
    def fontsize(self):
        """Get the fontsize attribute of the image."""
        return self.state.fontsize

    @fontsize.setter
    def fontsize(self, value):
        """Set the fontsize attribute of the image."""
        self.state.fontsize = value

    @property
    def LaTeX(self):
        """Get the LaTeX attribute of the image."""
        return self.state.LaTeX

    @LaTeX.setter
    def LaTeX(self, value):
        """Set the LaTeX attribute of the image."""
        self.state.LaTeX = value

    @property
    def legpar(self):
        """Get the legpar attribute of the image."""
        return self.state.legpar

    @legpar.setter
    def legpar(self, value):
        """Set the legpar attribute of the image."""
        self.state.legpar = value

    @property
    def legpos(self):
        """Get the legpos attribute of the image."""
        return self.state.legpos

    @legpos.setter
    def legpos(self, value):
        """Set the legpos attribute of the image."""
        self.state.legpos = value

    @property
    def ncol0(self):
        """Get the ncol0 attribute of the image."""
        return self.state.ncol0

    @ncol0.setter
    def ncol0(self, value):
        """Set the ncol0 attribute of the image."""
        self.state.ncol0 = value

    @property
    def nline(self):
        """Get the nline attribute of the image."""
        return self.state.nline

    @nline.setter
    def nline(self, value):
        """Set the nline attribute of the image."""
        self.state.nline = value

    @property
    def nrow0(self):
        """Get the nrow0 attribute of the image."""
        return self.state.nrow0

    @nrow0.setter
    def nrow0(self, value):
        """Set the nrow0 attribute of the image."""
        self.state.nrow0 = value

    @property
    def ntext(self):
        """Get the ntext attribute of the image."""
        return self.state.ntext

    @ntext.setter
    def ntext(self, value):
        """Set the ntext attribute of the image."""
        self.state.ntext = value

    @property
    def nwin(self):
        """Get the nwin attribute of the image."""
        return self.state.nwin

    @nwin.setter
    def nwin(self, value):
        """Set the nwin attribute of the image."""
        self.state.nwin = value

    @property
    def setax(self):
        """Get the setax attribute of the image."""
        return self.state.setax

    @setax.setter
    def setax(self, value):
        """Set the setax attribute of the image."""
        self.state.setax = value

    @property
    def setay(self):
        """Get the setay attribute of the image."""
        return self.state.setay

    @setay.setter
    def setay(self, value):
        """Set the setay attribute of the image."""
        self.state.setay = value

    @property
    def set_size(self):
        """Get the set_size attribute of the image."""
        return self.state.set_size

    @set_size.setter
    def set_size(self, value):
        """Set the set_size attribute of the image."""
        self.state.set_size = value

    @property
    def shade(self):
        """Get the shade attribute of the image."""
        return self.state.shade

    @shade.setter
    def shade(self, value):
        """Set the shade attribute of the image."""
        self.state.shade = value

    @property
    def tickspar(self):
        """Get the tickspar attribute of the image."""
        return self.state.tickspar

    @tickspar.setter
    def tickspar(self, value):
        """Set the tickspar attribute of the image."""
        self.state.tickspar = value

    @property
    def style(self):
        """Get the style attribute of the image."""
        return self.state.style

    @style.setter
    def style(self, value):
        """Set the style attribute of the image."""
        self.state.style = value

    @property
    def tight(self):
        """Get the tight attribute of the image."""
        return self.state.tight

    @tight.setter
    def tight(self, value):
        """Set the tight attribute of the image."""
        self.state.tight = value

    @property
    def vlims(self):
        """Get the vlims attribute of the image."""
        return self.state.vlims

    @vlims.setter
    def vlims(self, value):
        """Set the vlims attribute of the image."""
        self.state.vlims = value

    @property
    def xscale(self):
        """Get the xscale attribute of the image."""
        return self.state.xscale

    @xscale.setter
    def xscale(self, value):
        """Set the xscale attribute of the image."""
        self.state.xscale = value

    @property
    def yscale(self):
        """Get the yscale attribute of the image."""
        return self.state.yscale

    @yscale.setter
    def yscale(self, value):
        """Set the yscale attribute of the image."""
        self.state.yscale = value
