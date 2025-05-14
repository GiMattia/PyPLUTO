# figure_new.py
import shutil
import warnings
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt

from .delegator import delegator
from .imagestate import ImageState
from .inspect_kwargs import track_kwargs


@delegator("state")
class FigureManager:

    @track_kwargs
    def __init__(self, state: ImageState, **kwargs: Any) -> None:
        self.state = state

        # Extract specific kwargs for colorlines, with defaults if not provided
        if "numcolor" in kwargs:
            warnings.warn(
                "numcolor is deprecated. Use numcolors instead.",
                DeprecationWarning,
            )

        fontweight = kwargs.pop("fontweight", "normal")
        numcolors = kwargs.pop("numcolor", 10)  # To remove in the future!!!
        numcolors = kwargs.pop("numcolors", numcolors)
        withblack = kwargs.pop("withblack", False)
        withwhite = kwargs.pop("withwhite", False)

        self._setup_style()
        self.color = self._choose_colorlines(numcolors, withblack, withwhite)
        self._assign_LaTeX(fontweight)

    def _setup_style(self) -> None:
        try:
            plt.style.use(self.state.style)
        except OSError:
            warn = f"Warning: Style '{self.state.style}' not found. \
                Switching to 'default'"
            warnings.warn(warn, UserWarning)
            self.state.style = "default"

    def _choose_colorlines(
        self, numcolors: int, withblack: bool, withwhite: bool
    ) -> list[str]:
        """Chooses the colors for the lines. Depending on the number of colors
        and the option 'oldcolor', the colors are:

        - black, red, blue, cyan, green, orange (oldcolor = True)
        - a new list of colors (oldcolor = False, default)

        Both color lists are suited for all types of color vision deficiencies.

        Returns
        -------
        - colors: list[str]
            The list of colors for the lines.

        Parameters
        ----------
        - numcolors: int, default 10
            The number of colors.
        - oldcolor : bool, default False
            If True, the old colors are used.
        - withblack: bool, default False
            If True, the black color is used as first color.
        - withwhite: bool default False
            If True, the white color is used as first color.

        Notes
        -----
        - The withblack and withwhite options are only used if oldcolor = False
            and they cannot be used together (priority goes to black).

        ----

        Examples
        --------
        - Example #1: oldcolor = True

            >>> _choose_colorlines(6, True)

        - Example #2: oldcolor = False, withblack = True

            >>> _choose_colorlines(6, False, True)

        - Example #3: 12 colors, oldcolor = False, withwhite = True

            >>> _choose_colorlines(12, False, False, True)

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

    def _assign_LaTeX(self, fontweight: str) -> None:
        """Sets the LaTeX conditions. The option 'pgf' requires XeLaTeX and
        should be used only to get vectorial figures with minimal file size.

        Returns
        -------
        - None

        Parameters
        ----------
        - LaTeX (not optional): bool | str
            The LaTeX option. Is True is selected, the default LaTeX font is used.
            If 'pgf' is selected, the pgf backend is used to save pdf figures with
            minimal file size. If XeLaTeX is not installed and the 'pgf' option is
            selected, the LaTeX option True is used as backup strategy.

        Notes
        -----
        - None

        ----

        Examples
        --------
        - Example #1: LaTeX option True

            >>> _assign_LaTeX(True)

        - Example #2: LaTeX option 'pgf'

            >>> _assign_LaTeX('pgf')

        """
        # LaTeX option 'pgf' (requires XeLaTeX)
        if self.state.LaTeX == "pgf" and not shutil.which("latex"):
            warn = "LaTeX not installed, switching to LaTeX = True"
            warnings.warn(warn, UserWarning)
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
                    }
                )

            # If errors occur, the LaTeX option True is used and a warning
            # message is displayed
            except ImportError:
                warn = "The pgf backend is not available, reverting to True\n"
                warnings.warn(warn, UserWarning)
                self.state.LaTeX = True

        # LaTeX option True: default LaTeX font
        if self.state.LaTeX is True:
            try:
                mpl.rcParams["mathtext.fontset"] = "stix"
                mpl.rcParams["font.family"] = "STIXGeneral"
            except ImportError:
                warn = "The LaTeX = True option is not available."
                warnings.warn(warn, UserWarning)

        # End of the function
