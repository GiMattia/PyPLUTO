"""Figure Manager Module."""

from __future__ import annotations

import shutil
from typing import Unpack

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from pyPLUTO.imagekwargs import FigureKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs
from pyPLUTO.utils.ppwarnings import (
    PPWarn,
    PyPLUTOBehaviorWarning,
    PyPLUTOConflictWarning,
    PyPLUTODependencyWarning,
    PyPLUTODeprecationWarning,
    PyPLUTOOptionWarning,
)


class FigureManager(ImageMixin):
    """Manages the figure and sets the style, size, and LaTeX settings.

    It creates a new figure and sets the LaTeX conditions, as well as the
    matplotlib style. Every Image is associated to a figure object and only one
    in order to avoid confusion between images and figures. If you
    want to create multiple figures, you have to create multiple Image objects.

    Parameters
    ----------
    - close: bool, default True
        If True, the existing figure with the same window number is closed.
    - fig (not optional): Figure | None, default None
        The figure instance. If not None, the figure is used (only if we
        need to associate an Image to an existing figure).
    - figsize: Sequence[float], default varies
        Sets the figure size. The default is [6*sqrt(ncol), 5*sqrt(nrow)],
        computed from the number of rows and columns (or [8,5] for a single
        plot).
    - fontweight: str, default "normal"
        Sets the font weight for all the axis components.
    - fontsize: float, default 17.0
        Sets the fontsize for all the axis components.
    - LaTeX (not optional): bool | str
        The LaTeX option. If True is selected, the default LaTeX font is
        used. If 'pgf' is selected, the pgf backend is used to save pdf
        figures with minimal file size. If XeLaTeX is not installed and the
        'pgf' option is selected, the LaTeX option True is used as backup
        strategy.
    - numcolors: int, default 10
        The number of colors.
    - nwin: int, default 1
        The window number.
    - replace: bool, default False
        If True, the existing figure with the same window number will be
        replaced.
    - suptitle: str, default None
        Creates a figure title over all the subplots.
    - suptitlesize: int | str, default 'large'
        The figure title size.
    - tight: bool, default True
        Enables/disables tight layout options for the figure. In case of a
        highly customized plot (e.g. ratios or space between rows and
        columns) the option is set by default to False since that option
        would not be available for standard matplotlib functions.
    - withblack: bool, default False
        If True, the black color is used as first color.
    - withwhite: bool default False
        If True, the white color is used as first color.
    """

    @track_kwargs
    def __init__(
        self,
        state: ImageState,
        _check: bool = True,
        **kwargs: Unpack[FigureKwargs],
    ) -> None:
        """Initialize the FigureManager class with a given state."""
        self.state = state

        # `close` closed whatever was in the window, `replace` decided
        # whether a new figure was built, and neither did anything on its
        # own: replace could not replace without close having emptied the
        # window first. They are one keyword now.
        deprecated_close = kwargs.pop("close", None)
        if deprecated_close is not None:
            warn = "'close' argument is deprecated. Use 'replace' instead."
            PPWarn.warn(warn, PyPLUTODeprecationWarning)

        # A figure passed with `fig` is the one the user wants used, so it is
        # kept unless replacing is asked for; anything else means taking over
        # the window with a new figure.
        default_replace = (
            deprecated_close
            if deprecated_close is not None
            else "fig" not in kwargs
        )
        replace = kwargs.pop("replace", default_replace)

        self.state.fontweight = kwargs.pop("fontweight", self.state.fontweight)
        numcolors = kwargs.pop("numcolors", 10)
        suptitle = kwargs.pop("suptitle", None)
        suptitlesize = kwargs.pop("suptitlesize", "large")
        withblack = kwargs.pop("withblack", False)
        withwhite = kwargs.pop("withwhite", False)

        fig = kwargs.get("fig")
        self.state.figsize = kwargs.get("figsize", self.state.figsize)
        self.state.fontsize = kwargs.get("fontsize", self.state.fontsize)
        self.state.LaTeX = kwargs.get("LaTeX", self.state.LaTeX)
        self.state.nwin = kwargs.get("nwin", self.state.nwin)
        self.state.style = kwargs.get("style", self.state.style)
        self.state.tight = kwargs.get("tight", self.state.tight)

        self.check_previous_fig(fig, replace)

        # A figure carries its own window number and cannot be renumbered, so
        # an nwin given together with `fig` is dropped. Said out loud only
        # when the two disagree, since asking for the number it already has
        # is no mistake.
        if "nwin" in kwargs and kwargs["nwin"] != self.state.nwin:
            warn = (
                f"The figure given has window number {self.state.nwin}, "
                f"so nwin={kwargs['nwin']} is ignored."
            )
            PPWarn.warn(warn, PyPLUTOConflictWarning)

        # check_previous_fig copies the size, the fontsize and the layout off
        # the figure being attached to, which would silently drop whatever
        # was asked for here, so anything explicit is applied again.
        if "figsize" in kwargs:
            self.state.figsize = kwargs["figsize"]
            self.state.set_size = True
        if "fontsize" in kwargs:
            self.state.fontsize = kwargs["fontsize"]
        if "tight" in kwargs:
            self.state.tight = kwargs["tight"]

        self.setup_style()
        self.state.color = self.choose_colorlines(
            numcolors,
            withblack,
            withwhite,
        )
        self.assign_LaTeX(self.state.fontweight)
        self.create_figure(fig, replace, suptitle, suptitlesize)

        # create_figure sizes a figure it creates itself; one attached to
        # with `fig` is resized here, so an explicit figsize reaches it too.
        if "figsize" in kwargs:
            self.state.fig.set_size_inches(
                self.state.figsize[0], self.state.figsize[1]
            )

    def setup_style(self) -> None:
        """Set the matplotlib style."""
        try:
            plt.style.use(self.state.style)
        except OSError:
            warn = f"Warning: Style '{self.state.style}' not found. \
                Switching to 'default'"
            PPWarn.warn(warn, PyPLUTOOptionWarning)
            self.state.style = "default"

    def choose_colorlines(
        self,
        numcolors: int,
        withblack: bool,
        withwhite: bool,
    ) -> list[str]:
        """Choose the colors for the lines.

        The colors are taken from a list of colors that are suitable for all
        types of color vision deficiencies.

        Parameters
        ----------
        - numcolors: int, default 10
            The number of colors.
        - withblack: bool, default False
            If True, the black color is used as first color.
        - withwhite: bool default False
            If True, the white color is used as first color.

        Returns
        -------
        - list[str]

        Examples
        --------
        - Example #1: withblack = True

            >>> _choose_colorlines(6, True)

        - Example #2: 12 colors, withwhite = True

            >>> _choose_colorlines(12, False, True)

        """
        # New colors dictionary (black and white included)
        self.state.dictcol = {
            0: "#ffffff",
            1: "#e8ecfb",
            2: "#d9cce3",
            3: "#d1bbd7",
            4: "#caaccb",
            5: "#ae76a3",
            6: "#aa6f9e",
            7: "#994f88",
            8: "#882e72",
            9: "#0104fe",
            10: "#1e3888",
            11: "#437dbf",
            12: "#5289c7",
            13: "#6195cf",
            14: "#7bafde",
            15: "#4eb265",
            16: "#90c987",
            17: "#cae0ab",
            18: "#f7f056",
            19: "#f7cb45",
            20: "#f6c141",
            21: "#f4a736",
            22: "#f1932d",
            23: "#ee8026",
            24: "#e8601c",
            25: "#e65518",
            26: "#dc050c",
            27: "#a5170e",
            28: "#72190e",
            29: "#42150a",
            30: "#777777",
            31: "#000000",
            32: "#0104fe",
        }

        # Colors are ordered to avoid color vision deficiencies
        lstc = [
            9,
            26,
            15,
            23,
            14,
            17,
            6,
            25,
            28,
            18,
            11,
            2,
            8,
            16,
            10,
            21,
            7,
            27,
            4,
            13,
            19,
            29,
            1,
            30,
        ]

        # Black and white addition
        lstc = [0, *lstc] if withwhite else [31, *lstc] if withblack else lstc

        # End of function, return the colors
        return [self.state.dictcol[lstc[i]] for i in range(numcolors)]

    def assign_LaTeX(self, fontweight: str) -> None:
        """Set the LaTeX conditions.

        The option 'pgf' requires XeLaTeX and should be used only to get
        vectorial figures with minimal file size.

        Parameters
        ----------
        - LaTeX (not optional): bool | str
            The LaTeX option. If True is selected, the default LaTeX font is
            used. If 'pgf' is selected, the pgf backend is used to save pdf
            figures with minimal file size. If XeLaTeX is not installed and the
            'pgf' option is selected, the LaTeX option True is used as backup
            strategy.
        - fontweight: str, default "normal"
            Sets the font weight for all the axis components.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: LaTeX option True

            >>> _assign_LaTeX(True)

        - Example #2: LaTeX option 'pgf'

            >>> _assign_LaTeX("pgf")

        """
        # LaTeX option 'pgf' (requires XeLaTeX)
        if self.state.LaTeX == "pgf" and not shutil.which("latex"):
            warn = "LaTeX not installed, switching to LaTeX = True"
            PPWarn.warn(warn, PyPLUTODependencyWarning)
            self.state.LaTeX = True

        if self.state.LaTeX == "pgf":
            # Set the pgf backend
            try:
                plt.switch_backend("pgf")

                # Preamble (LaTeX commands and packages)
                pgf_preamble = r"""
                \usepackage{amsmath}
                \usepackage{amssymb}
                \usepackage{mathptmx}
                \usepackage{siunitx}
                \usepackage[T1]{fontenc}
                \newcommand{\DS}{\displaystyle}
                """

                # Update the rcParams
                mpl.rcParams.update(
                    {
                        "pgf.preamble": pgf_preamble,
                        "font.family": "serif",
                        "font.weight": fontweight,
                        "text.usetex": True,
                    },
                )

            # If errors occur, the LaTeX option True is used and a warning
            # message is displayed
            except ImportError:
                warn = "The pgf backend is not available, reverting to True\n"
                PPWarn.warn(warn, PyPLUTODependencyWarning)
                self.state.LaTeX = True

        # LaTeX option True: default LaTeX font
        if self.state.LaTeX is True:
            try:
                mpl.rcParams["mathtext.fontset"] = "stix"
                mpl.rcParams["font.family"] = "STIXGeneral"
            except ImportError:
                warn = "The LaTeX = True option is not available."
                PPWarn.warn(warn, PyPLUTODependencyWarning)

        # End of the function

    def check_previous_fig(self, fig: Figure | None, replace: bool) -> None:
        """Read what an attached fig carries, and empty the window to replace.

        A figure given with `fig` decides the size, the fontsize, the window
        number and the layout of the Image, since those are properties of the
        figure rather than of the Image attached to it. What the user asked
        for explicitly is applied again afterwards, in `__init__`.

        Parameters
        ----------
        - fig: Figure | None
            The figure given with `fig`, or None if none was given.
        - replace: bool, default True
            If True, the figure holding the window number is cleared and
            closed, so that a new one can take its place. If False, that
            figure is left alone and inherited.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: empty the window, to replace what is in it

            >>> self.check_previous_fig(None, True)

        - Example #2: attach to a figure and keep it

            >>> self.check_previous_fig(fig, False)

        """
        if fig is not None:
            self.state.figsize = [fig.get_figwidth(), fig.get_figheight()]
            self.state.fontsize = plt.rcParams["font.size"]
            try:
                fignum = fig.number
                if isinstance(fignum, int):
                    self.state.nwin = fignum
            except AttributeError:
                PPWarn.warn(
                    "The figure is not associated to a window number",
                    PyPLUTOBehaviorWarning,
                )
                self.state.nwin = 1
            # get_tight_layout() reports matplotlib's layout engine, which
            # pyPLUTO never installs: it calls tight_layout() once instead.
            # So False means "no engine here", not "no tight layout wanted",
            # and only a True is worth inheriting.
            if fig.get_tight_layout():
                self.state.tight = True

        # Close the existing figure if it exists (and 'close' is enabled).
        # `clf()` releases artists/axes payloads immediately, which prevents
        # stale Image instances (still holding axes/text refs) from retaining
        # heavy plot data in memory.
        if plt.fignum_exists(self.state.nwin) and replace is True:
            existing_fig = plt.figure(self.state.nwin)
            existing_fig.clf()
            plt.close(existing_fig)

    def create_figure(
        self,
        fig: Figure | None,
        replace: bool,
        suptitle: str | None,
        suptitlesize: int | str,
    ) -> None:
        """Create the figure associated to an Image instance.

        It is called by default when the Image class is instantiated.

        Parameters
        ----------
        - fig: Figure | None
            The figure given with `fig`, used unless replace is True. If
            None, a new figure is created.
        - replace: bool, default False
            If True, the existing figure with the same window number will be
            replaced.
        - suptitle: str, default None
            Creates a figure title over all the subplots.
        - suptitlesize: int | str, default 'large'
            The figure title size.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Create a new figure

            >>> self.create_figure(None, True, None, "large")

        - Example #2: Associate an Image to an existing figure

            >>> self.create_figure(fig, False, None, "large")

        - Example #3: Create a new figure with a figure title

            >>> self.create_figure(None, True, "Super Title", "large")

        """
        # A figure given is used, unless replace asks for a new one
        if fig is not None and replace is False:
            self.state.fig = fig
        elif plt.fignum_exists(self.state.nwin):
            # Inheriting the figure already in that window: pyplot hands
            # it back and warns about every argument given with it, so
            # the size is applied afterwards instead, in __init__.
            self.state.fig = plt.figure(self.state.nwin)
        else:
            self.state.fig = plt.figure(
                self.state.nwin,
                figsize=(self.state.figsize[0], self.state.figsize[1]),
            )
        plt.rcParams.update({"font.size": self.state.fontsize})

        # Suptitle
        if suptitle is not None:
            self.state.fig.suptitle(suptitle, fontsize=suptitlesize)

        # Tight layout
        if self.state.tight is True:
            self.state.fig.tight_layout()
