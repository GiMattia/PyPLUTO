# figure_new.py
import shutil
import warnings
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from ..imagemixin import ImageMixin
from ..imagestate import ImageState
from ..utils.inspector import track_kwargs


class FigureManager(ImageMixin):
    """Manages the figure and sets the style, size, and LaTeX settings."""

    @track_kwargs
    def __init__(
        self,
        state: ImageState,
        **kwargs: Any,
    ) -> None:
        """Initialize the FigureManager class.

        It creates a new figure and sets the LaTeX conditions, as well as the
        matplotlib style. Every Image is associated to a figure object and only
        one in order to avoid confusion between images and figures. If you
        want to create multiple figures, you have to create multiple
        Image objects.

        Returns
        -------
        - None

        Parameters
        ----------
        - state: ImageState
            The state of the image, which contains the figure and other
            properties.
        - kwargs: dict[str, Any]
            Additional keyword arguments to customize the figure, such as
            `figsize`, `fontsize`, `nwin`, `suptitle`, etc.

        """
        # needed because the __init__ is longer than simply self.state = state
        self.state = state

        # Extract specific kwargs for colorlines, with defaults if not provided
        if "numcolor" in kwargs:
            warnings.warn(
                "numcolor is deprecated. Use numcolors instead.",
                DeprecationWarning,
            )

        close = kwargs.pop("close", True)
        fontweight = kwargs.pop("fontweight", "normal")
        kwargs.pop("numcolor", None)  # remove numcolor if present
        numcolors = kwargs.pop("numcolors", 10)
        replace = kwargs.pop("replace", False)
        suptitle = kwargs.pop("suptitle", None)
        suptitlesize = kwargs.pop("suptitlesize", "large")
        withblack = kwargs.pop("withblack", False)
        withwhite = kwargs.pop("withwhite", False)

        self.fig = kwargs.get("fig", self.fig)
        self.nwin = kwargs.get("nwin", self.nwin)

        self.check_previous_fig(close)
        self.LaTeX = kwargs.get("LaTeX", self.LaTeX)
        self.fontsize = kwargs.get("fontsize", self.fontsize)
        self.tight = kwargs.get("tight", self.tight)
        self.figsize = kwargs.get("figsize", self.figsize)
        self.style = kwargs.get("style", self.style)
        if "figsize" in kwargs:
            self.set_size = True

        self.setup_style()
        self.color = self.choose_colorlines(numcolors, withblack, withwhite)
        self.assign_LaTeX(fontweight)
        self.create_figure(replace, suptitle, suptitlesize)

    def setup_style(self) -> None:
        """Sets the matplotlib style."""
        try:
            plt.style.use(self.style)
        except OSError:
            warn = f"Warning: Style '{self.style}' not found. \
                Switching to 'default'"
            warnings.warn(warn, UserWarning)
            self.style = "default"

    def choose_colorlines(
        self, numcolors: int, withblack: bool, withwhite: bool
    ) -> list[str]:
        """Chooses the colors for the lines. The colors are taken from a
        list of colors that are suitable for all types of color vision
        deficiencies.

        Returns
        -------
        - colors: list[str]
            The list of colors for the lines.

        Parameters
        ----------
        - numcolors: int, default 10
            The number of colors.
        - withblack: bool, default False
            If True, the black color is used as first color.
        - withwhite: bool default False
            If True, the white color is used as first color.

        ----

        Examples
        --------
        - Example #1: withblack = True

            >>> _choose_colorlines(6, True)

        - Example #2: 12 colors, withwhite = True

            >>> _choose_colorlines(12, False, True)

        """
        # New colors dictionary (black and white included)
        self.dictcol = {
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
        lstc = [0] + lstc if withwhite else [31] + lstc if withblack else lstc

        # End of function, return the colors
        return [self.dictcol[lstc[i]] for i in range(numcolors)]

    def assign_LaTeX(self, fontweight: str) -> None:
        """Sets the LaTeX conditions. The option 'pgf' requires XeLaTeX
        and should be used only to get vectorial figures with minimal
        file size.

        Returns
        -------
        - None

        Parameters
        ----------
        - LaTeX (not optional): bool | str
            The LaTeX option. Is True is selected, the default LaTeX font is
            used. If 'pgf' is selected, the pgf backend is used to save pdf
            figures with minimal file size. If XeLaTeX is not installed and the
            'pgf' option is selected, the LaTeX option True is used as backup
            strategy.

        ----

        Examples
        --------
        - Example #1: LaTeX option True

            >>> _assign_LaTeX(True)

        - Example #2: LaTeX option 'pgf'

            >>> _assign_LaTeX("pgf")

        """
        # LaTeX option 'pgf' (requires XeLaTeX)
        if self.LaTeX == "pgf" and not shutil.which("latex"):
            warn = "LaTeX not installed, switching to LaTeX = True"
            warnings.warn(warn, UserWarning)
            self.LaTeX = True

        if self.LaTeX == "pgf":
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
                    }
                )

            # If errors occur, the LaTeX option True is used and a warning
            # message is displayed
            except ImportError:
                warn = "The pgf backend is not available, reverting to True\n"
                warnings.warn(warn, UserWarning)
                self.LaTeX = True

        # LaTeX option True: default LaTeX font
        if self.LaTeX is True:
            try:
                mpl.rcParams["mathtext.fontset"] = "stix"
                mpl.rcParams["font.family"] = "STIXGeneral"
            except ImportError:
                warn = "The LaTeX = True option is not available."
                warnings.warn(warn, UserWarning)

        # End of the function

    def check_previous_fig(self, close: bool) -> None:
        """Checks if there is an existing figure and if it is closed or
        not.

        Returns
        -------
        - None

        Parameters
        ----------
        - close: bool, default True
            If True, the existing figure with the same window number is closed.

        ----

        Examples
        --------
        - Example #1: Check if there is an existing figure

            >>> _check_previous_fig(True)

        """
        if isinstance(self.fig, Figure):
            self.figsize = [
                self.fig.get_figwidth(),
                self.fig.get_figheight(),
            ]
            self.fontsize = plt.rcParams["font.size"]
            try:
                self.nwin = self.fig.number  # type: ignore
            except AttributeError:
                warnings.warn(
                    "The figure is not associated to a window number",
                    UserWarning,
                )
                self.nwin = 1
            self.tight = self.fig.get_tight_layout()

        # Close the existing figure if it exists (and 'close' is enabled)
        if plt.fignum_exists(self.nwin) and close is True:
            plt.close(self.nwin)

    def create_figure(
        self, replace: bool, suptitle: str, suptitlesize: str
    ) -> None:
        """Function that creates the figure associated to an Image
        instance. It is called by default when the Image class is
        instantiated.

        Returns
        -------
        - None

        Parameters
        ----------
        - close: bool, default True
            If True, the existing figure with the same window number is closed.
        - fig (not optional): Figure | None, default None
            The figure instance. If not None, the figure is used (only if we
            need to associate an Image to an existing figure).
        - figsize: list[float], default [8,5]
            The figure size.
        - fontsize: int, default 17
            The font size.
        - nwin: int, default 1
            The window number.
        - suptitle: str, default None
            The super title of the figure.
        - suptitlesize: str | int, default 'large'
            The figure title size.
        - tight: bool, default True
            If True, the tight layout is used.

        ----

        Examples
        --------
        - Example #1: Create a new figure

            >>> _create_figure()

        - Example #2: Associate an Image to an existing figure

            >>> _create_figure(fig=fig)

        - Example #3: Create a new figure with different size and a figure title

            >>> _create_figure(suptitle="Super Title", figsize=[10, 5])

        - Example #4: Create a new figure with a specific window number

            >>> _create_figure(nwin=2)

        """
        # Create a new figure instance with the provided window number
        if self.fig is None or replace is True:
            self.fig = plt.figure(
                self.nwin,
                figsize=(self.figsize[0], self.figsize[1]),
            )
        plt.rcParams.update({"font.size": self.fontsize})

        # Suptitle
        if suptitle is not None:
            self.fig.suptitle(suptitle, fontsize=suptitlesize)

        # Tight layout
        if self.tight is True:
            self.fig.tight_layout()
