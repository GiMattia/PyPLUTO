"""Mixin class for image handling."""

from typing import Any

from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .imagestate import ImageState


class ImageMixin:
    """Mixin class for image handling.

    It provides properties and methods related to the image state and axes."""

    # pylint: disable=too-many-public-methods

    state: ImageState

    @property
    def ax(self) -> list[Axes]:
        """Get the ax attribute of the image."""
        return self.state.ax

    @ax.setter
    def ax(self, value: list[Axes]) -> None:
        """Set the ax attribute of the image."""
        self.state.ax = value

    @property
    def color(self) -> list[str]:
        """Get the color attribute of the image."""
        return self.state.color

    @color.setter
    def color(self, value: list[str]) -> None:
        """Set the color attribute of the image."""
        self.state.color = value

    @property
    def dictcol(self) -> dict[int, str]:
        """Get the dictcol attribute of the image."""
        return self.state.dictcol

    @dictcol.setter
    def dictcol(self, value: dict[int, str]) -> None:
        """Set the dictcol attribute of the image."""
        self.state.dictcol = value

    @property
    def fig(self) -> Figure:
        """Get the fig attribute of the image."""
        return self.state.fig

    @fig.setter
    def fig(self, value: Figure) -> None:
        """Set the fig attribute of the image."""
        self.state.fig = value

    @property
    def figsize(self) -> list[float]:
        """Get the figsize attribute of the image."""
        return self.state.figsize

    @figsize.setter
    def figsize(self, value: list[float]) -> None:
        """Set the figsize attribute of the image."""
        self.state.figsize = value

    @property
    def fontsize(self) -> int:
        """Get the fontsize attribute of the image."""
        return self.state.fontsize

    @fontsize.setter
    def fontsize(self, value: int) -> None:
        """Set the fontsize attribute of the image."""
        self.state.fontsize = value

    @property
    def LaTeX(self) -> bool | str:
        """Get the LaTeX attribute of the image."""
        return self.state.LaTeX

    @LaTeX.setter
    def LaTeX(self, value: bool | str) -> None:
        """Set the LaTeX attribute of the image."""
        self.state.LaTeX = value

    @property
    def legpar(self) -> list[list[float]]:
        """Get the legpar attribute of the image."""
        return self.state.legpar

    @legpar.setter
    def legpar(self, value: list[list[float]]) -> None:
        """Set the legpar attribute of the image."""
        self.state.legpar = value

    @property
    def legpos(self) -> list[int | str | None]:
        """Get the legpos attribute of the image."""
        return self.state.legpos

    @legpos.setter
    def legpos(self, value: list[int | str | None]) -> None:
        """Set the legpos attribute of the image."""
        self.state.legpos = value

    @property
    def ncol0(self) -> int:
        """Get the ncol0 attribute of the image."""
        return self.state.ncol0

    @ncol0.setter
    def ncol0(self, value: int) -> None:
        """Set the ncol0 attribute of the image."""
        self.state.ncol0 = value

    @property
    def nline(self) -> list[int]:
        """Get the nline attribute of the image."""
        return self.state.nline

    @nline.setter
    def nline(self, value: list[int]) -> None:
        """Set the nline attribute of the image."""
        self.state.nline = value

    @property
    def nrow0(self) -> int:
        """Get the nrow0 attribute of the image."""
        return self.state.nrow0

    @nrow0.setter
    def nrow0(self, value: int) -> None:
        """Set the nrow0 attribute of the image."""
        self.state.nrow0 = value

    @property
    def ntext(self) -> list[Any | None]:
        """Get the ntext attribute of the image."""
        return self.state.ntext

    @ntext.setter
    def ntext(self, value: list[Any | None]) -> None:
        """Set the ntext attribute of the image."""
        self.state.ntext = value

    @property
    def nwin(self) -> int:
        """Get the nwin attribute of the image."""
        return self.state.nwin

    @nwin.setter
    def nwin(self, value: int) -> None:
        """Set the nwin attribute of the image."""
        self.state.nwin = value

    @property
    def setax(self) -> list[Any | int]:
        """Get the setax attribute of the image."""
        return self.state.setax

    @setax.setter
    def setax(self, value: list[Any | int]) -> None:
        """Set the setax attribute of the image."""
        self.state.setax = value

    @property
    def setay(self) -> list[Any | int]:
        """Get the setay attribute of the image."""
        return self.state.setay

    @setay.setter
    def setay(self, value: list[Any | int]) -> None:
        """Set the setay attribute of the image."""
        self.state.setay = value

    @property
    def set_size(self) -> bool:
        """Get the set_size attribute of the image."""
        return self.state.set_size

    @set_size.setter
    def set_size(self, value: bool) -> None:
        """Set the set_size attribute of the image."""
        self.state.set_size = value

    @property
    def shade(self) -> list[str]:
        """Get the shade attribute of the image."""
        return self.state.shade

    @shade.setter
    def shade(self, value: list[str]) -> None:
        """Set the shade attribute of the image."""
        self.state.shade = value

    @property
    def style(self) -> str:
        """Get the style attribute of the image."""
        return self.state.style

    @style.setter
    def style(self, value: str) -> None:
        """Set the style attribute of the image."""
        self.state.style = value

    @property
    def tickspar(self) -> list[Any | int]:
        """Get the tickspar attribute of the image."""
        return self.state.tickspar

    @tickspar.setter
    def tickspar(self, value: list[Any | int]) -> None:
        """Set the tickspar attribute of the image."""
        self.state.tickspar = value

    @property
    def tight(self) -> bool:
        """Get the tight attribute of the image."""
        return self.state.tight

    @tight.setter
    def tight(self, value: bool) -> None:
        """Set the tight attribute of the image."""
        self.state.tight = value

    @property
    def vlims(self) -> list[list[float]]:
        """Get the vlims attribute of the image."""
        return self.state.vlims

    @vlims.setter
    def vlims(self, value: list[list[float]]) -> None:
        """Set the vlims attribute of the image."""
        self.state.vlims = value

    @property
    def xscale(self) -> list[str]:
        """Get the xscale attribute of the image."""
        return self.state.xscale

    @xscale.setter
    def xscale(self, value: list[str]) -> None:
        """Set the xscale attribute of the image."""
        self.state.xscale = value

    @property
    def yscale(self) -> list[str]:
        """Get the yscale attribute of the image."""
        return self.state.yscale

    @yscale.setter
    def yscale(self, value: list[str]) -> None:
        """Set the yscale attribute of the image."""
        self.state.yscale = value
