"""LegendManager class."""

from __future__ import annotations

from typing import Unpack, cast

import matplotlib.lines as mlines
import numpy as np
from matplotlib.axes import Axes
from matplotlib.typing import MarkerType

from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagekwargs import LegendKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs


class LegendManager(ImageMixin):
    """LegendManager class.

    It provides methods to create and manage legends
    in the plots. It is designed to work with the Image class and allows for
    dynamic creation of legends based on the current state of the image.
    The class uses the ImageToolsManager to handle the display and plotting
    of the legends, and it provides methods to customize the appearance of
    the legends.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the LegendManager with the given state."""
        self.state = state
        self.ImageToolsManager = ImageToolsManager(state)

    @track_kwargs
    def legend(
        self,
        ax: Axes | int | None = None,
        fromplot: bool = False,
        _check: bool = True,
        **kwargs: Unpack[LegendKwargs],
    ) -> None:
        """Creation of a legend referring to the current figure.

        If no labels are given, it shows the labels of all the plots in the
        figure, ordered by entry. If specific labels are given, it shows those.

        Parameters
        ----------
        - ax: ax | int | None, default None
            The axis where to insert the legend. If None, the last considered
            axis will be used.
        - bottom: float, default varies
            The bottom limit of the axis / axes set. For the figure layout it
            is the space from the bottom border to the plot (default 0.1); for
            an inset zoom it is the bottom position of the inset (default 0.6 +
            height).
        - c: str, default self.color
            Determines the color. If not defined, the program will loop
            over an array of 6 colors which are different for the most common
            vision deficiencies.
        - edgecolor: list[str], default [None]
            Sets the edge color of the legend. The default value is black
            ('k').
        - figsize: list[float], default varies
            Sets the figure size. The default is [6*sqrt(ncol), 5*sqrt(nrow)],
            computed from the number of rows and columns (or [8,5] for a single
            plot).
        - fillstyle: {'full', 'left', 'right', 'bottom', 'top', 'none'},
            default 'full'
            Sets the marker filling. The default value is the fully filled
            marker ('full').
        - fontsize: float, default 17.0
            Sets the fontsize for all the axis components.
        - fromplot: bool, default False
            If True, the legend will be created from the plot elements.
        - hratio: [float], default [1.0]
            Ratio between the rows of the plot. The default is that every plot
            row has the same height.
        - hspace: [float], default []
            The space between plot rows (in figure units). If not enough or too
            many spaces are considered, the program will remove the excess and
            fill the lacks with [0.1].
        - label: str, default None
            Associates a label to the plot, used for the creation of the
            legend.
        - left: float, default varies
            The left limit of the axis / axes set. For the figure layout it is
            the space from the left border to the plot (default 0.125); for an
            inset zoom it is the left position of the inset (default 0.6).
        - legalpha: float, default 0.8
            Sets the opacity of the legend.
        - legcols: int, default 1
            Sets the number of columns that the legend should have.
        - legpad: float, default 0.8
            Sets the space between the lines (or symbols) and the corresponding
            text in the legend.
        - legpos: int | str, default None
            If defined, creates a legend at the specified location.
        - legsize: float, default fontsize
            Sets the fontsize of the legend. The default value is the default
            fontsize value.
        - legspace: float, default 2
            Sets the space between the legend columns, in font-size units.
        - ls: {'-', '--', '-.', ':', ' ', etc.}, default '-'
            Sets the linestyle. The choices available are the ones defined in
            the matplotlib package.
        - lw: float, default 1.3
            Sets the linewidth.
        - marker: str | list[str | MarkerType] | MarkerType, default ' '
            Sets an optional symbol for every point. The default value is no
            marker (' '). A list can be used to cycle through different markers
            for each legend entry.
        - ms: float, default 3
            Sets the marker size.
        - mscale: float, default 1.0
            Sets the marker scale. The default value is 1.0.
        - ncol: int, default 1
            The number of columns of subplots.
        - nrow: int, default 1
            The number of rows of subplots.
        - proj: str, default None
            Custom projection for the plot (e.g. 3D). Recommended only if
            needed. WARNING: pyPLUTO does not support 3D plotting for now, only
            3D axes. The 3D plot feature will be available in future releases.
        - right: float, default varies
            The right limit of the axis / axes set. For the figure layout it is
            the space from the right border to the plot (default 0.9); for an
            inset zoom it is the right position of the inset (default left +
            0.15).
        - sharex: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the x-axis between the subplots.
        - sharey: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the y-axis between the subplots.
        - suptitle: str, default None
            Creates a figure title over all the subplots.
        - tight: bool, default True
            Enables/disables tight layout options for the figure. In case of a
            highly customized plot (e.g. ratios or space between rows and
            columns) the option is set by default to False since that option
            would not be available for standard matplotlib functions.
        - top: float, default varies
            The top limit of the axis / axes set. For the figure layout it is
            the space from the top border to the plot (default 0.9); for an
            inset zoom it is the top position of the inset (default bottom +
            height).
        - wratio: [float], default [1.0]
            Ratio between the columns of the plot. The default is that every
            plot column has the same width.
        - wspace: [float], default []
            The space between plot columns (in figure units). If not enough or
            too many spaces are considered, the program will remove the excess
            and fill the lacks with [0.1].

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: create a standard legend

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes()
            >>> I.plot(x, y, ax=ax, label="label")
            >>> I.legend(ax)

        - Example #2: create a legend with custom labels

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x, y)
            >>> I.legend(label="y")

        - Example #3: create a double legend for four lines in a single plot

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x, y1, ls="-", c="k")
            >>> I.plot(x, y2, ls="-.", c="r")
            >>> I.plot(x, y3, ls="-", c="r")
            >>> I.plot(x, y4, ls="-.", c="k")
            >>> I.legend(
            ...     legpos="lower left",
            ...     ls=["-", "-"],
            ...     c=["k", "r"],
            ...     label=["black lines", "red lines"],
            ... )
            >>> I.legend(
            ...     legpos="lower right",
            ...     ls=["-", "-."],
            ...     c=["k", "k"],
            ...     label=["continue", "dotted"],
            ... )
            >>> pp.show()

        """
        # Find figure and number of the axis
        ax, nax = self.ImageToolsManager.assign_ax(ax, _check=False, **kwargs)
        self.ImageToolsManager.hide_text(nax, ax.texts)

        # Finds the legend parameters (position, columns, size, spacing and pad)
        self.state.legpos[nax] = kwargs.get("legpos", self.state.legpos[nax])
        self.state.legpar[nax][0] = kwargs.get(
            "legsize",
            self.state.legpar[nax][0],
        )
        self.state.legpar[nax][1] = kwargs.get(
            "legcols",
            self.state.legpar[nax][1],
        )
        self.state.legpar[nax][2] = kwargs.get(
            "legspace",
            self.state.legpar[nax][2],
        )
        self.state.legpar[nax][3] = kwargs.get(
            "legpad",
            self.state.legpar[nax][3],
        )
        self.state.legpar[nax][4] = kwargs.get(
            "legalpha",
            self.state.legpar[nax][4],
        )

        # Check if another unwanted legend is present and cancel it
        # (only when the legend is called from the plot function)
        if fromplot is True:
            lleg = ax.get_legend()
            if lleg is not None:
                lleg.remove()

        # Check is custom labels are on and plot the legend
        if (label := kwargs.get("label")) is not None:
            lab = label if isinstance(label, list) else [label]
            col = list(np.atleast_1d(kwargs.get("c", ["k"])))
            ls = list(np.atleast_1d(kwargs.get("ls", ["-"])))
            lw = list(np.atleast_1d(kwargs.get("lw", [1.5])))
            raw_mrk = kwargs.get("marker", [""])
            mrk: list[MarkerType] = cast(
                "list[MarkerType]",
                raw_mrk if isinstance(raw_mrk, list) else [raw_mrk],
            )
            ms = list(np.atleast_1d(kwargs.get("ms", [5.0])))
            fls = list(np.atleast_1d(kwargs.get("fillstyle", ["full"])))
            edgcol = list(np.atleast_1d(kwargs.get("edgecolor", ["none"])))
            lines = []
            # Create the list of lines
            for i, val in enumerate(lab):
                lines.append(
                    mlines.Line2D(
                        [],
                        [],
                        label=val,
                        color=col[i % len(col)],
                        ls=ls[i % len(ls)],
                        lw=lw[i % len(lw)],
                        marker=mrk[i % len(mrk)],
                        ms=ms[i % len(ms)],
                        fillstyle=fls[i % len(fls)],
                        markeredgecolor=edgcol[i % len(edgcol)],
                    ),
                )
            # Create the legend
            legg = ax.legend(
                handles=lines,
                loc=self.state.legpos[nax],
                fontsize=self.state.legpar[nax][0],
                ncol=self.state.legpar[nax][1],
                columnspacing=self.state.legpar[nax][2],
                handletextpad=self.state.legpar[nax][3],
                framealpha=self.state.legpar[nax][4],
            )
        else:
            # Set the markerscale
            mscale = kwargs.get("mscale", 1.0)
            # Create the legend
            legg = ax.legend(
                loc=self.state.legpos[nax],
                fontsize=self.state.legpar[nax][0],
                ncol=self.state.legpar[nax][1],
                columnspacing=self.state.legpar[nax][2],
                handletextpad=self.state.legpar[nax][3],
                framealpha=self.state.legpar[nax][4],
                markerscale=mscale,
            )

        # Add the legend to the axis
        ax.add_artist(legg)

        # End of the function
