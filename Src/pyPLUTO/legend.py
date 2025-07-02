from typing import Any

import matplotlib.lines as mlines
from matplotlib.axes import Axes

from .delegator import delegator
from .imagestate import ImageState
from .imagetools import ImageToolsManager
from .inspector import track_kwargs


@delegator("state")
class LegendManager:
    """LegendManager class. It provides methods to create and manage legends
    in the plots. It is designed to work with the Image class and allows for
    dynamic creation of legends based on the current state of the image.
    The class uses the ImageToolsManager to handle the display and plotting
    of the legends, and it provides methods to customize the appearance of
    the legends."""

    exposed_methods = ("legend",)

    def __init__(self, state: ImageState):
        """Initializes the LegendManager with the given state."""
        self.state = state
        self.ImageToolsManager = ImageToolsManager(state)

    @track_kwargs
    def legend(
        self,
        ax: Axes | None = None,
        check: bool = True,
        fromplot: bool = False,
        **kwargs: Any,
    ) -> None:
        """Creation of a legend referring to the current figure.
        If no labels are given, it shows the labels of all the plots in the
        figure, ordered by entry. If specific labels are given, it shows those
        ones.

        Returns
        -------
        - None

        Parameters
        ----------
        - ax: ax | int | None, default None
            The axis where to insert the legend. If None, the last considered
            axis will be used.
        - c: str, default self.color
            Determines the line color. If not defined, the program will loop
            over an array of 6 color which are different for the most common
            vision deficiencies.
        - edgecolor: list[str], default [None]
            Sets the edge color of the legend. The default value is black ('k').
        - fillstyle: {'full', 'left', 'right', 'bottom', 'top', 'none'},
            default 'full'
            Sets the marker filling. The default value is the fully filled
            marker ('full').
        - label: [str], default None
            Associates a label to each line. If not specified, the program will
            take the label which are already associated with the plot.
        - legalpha: float, default 0.8
            Sets the opacity of the legend.
        - legcols: int, default 1
            Sets the number of columns that the legend should have.
        - legpad: float, default 0.8
            Sets the space between the lines (or symbols) and the correspondibg
            text in the legend.
        - legpos: int | str, default 0
            Selects the legend location. If not specified the standard
            matplotlib legend function will find the most suitable location.
        - legsize: float, default fontsize
            Sets the fontsize of the legend. The default value is the default
            fontsize value.
        - legspace: float, default 2
            Sets the space between the legend columns, in font-size units.
        - ls: {'-', '--', '-.', ':', ' ', ect.}, default '-'
            Sets the linestyle. The choices available are the ones defined in
            the matplotlib package. Here are reported the most common ones.
        - lw: float, default 1.3
            Sets the linewidth of each line.
        - marker: {'o', 'v', '^', '<', '>', 'X', ' ', etc.}, default ' '
            Sets an optional symbol for every point. The default value is no
            marker (' ').
        - ms: float, default 5 (if label) or 1 (if not label)
            Sets the marker size from the default value of 5.0 (if label is
            given) or the marker scale from the default value of 1.0 (if not
            label).
        - mscale: float, default 1.0
            Sets the marker scale. The default value is 1.0.

        ----

        Examples
        --------
        - Example #1: create a standard legend

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes()
            >>> I.plot(x,y, ax = ax, label = 'label')
            >>> I.legend(ax)

        - Example #2: create a legend with custom labels

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x,y)
            >>> I.legend(label = 'y')

        - Example #3: create a double legend for four lines in a single plot

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x, y1, ls = '-', c = 'k')
            >>> I.plot(x, y2, ls = '-.', c = 'r')
            >>> I.plot(x, y3, ls = '-', c = 'r')
            >>> I.plot(x, y4, ls = '-.', c = 'k')
            >>> I.legend(legpos = 'lower left', ls = ['-','-'], c = ['k','r'],
            ... label = ['black lines', 'red lines'])
            >>> I.legend(legpos = 'lower right', ls = ['-','-.'],
            ... c = ['k', 'k'], label = ['continue', 'dotted'])
            >>> pp.show()

        """
        kwargs.pop("check", check)

        # Find figure and number of the axis
        ax, nax = self.ImageToolsManager.assign_ax(ax, **kwargs)
        self.ImageToolsManager.hide_text(nax, ax.texts)

        # Finds the legend parameters (position, columns, size, spacing and pad)
        self.state.legpos[nax] = kwargs.get("legpos", self.state.legpos[nax])
        self.state.legpar[nax][0] = kwargs.get(
            "legsize", self.state.legpar[nax][0]
        )
        self.state.legpar[nax][1] = kwargs.get(
            "legcols", self.state.legpar[nax][1]
        )
        self.state.legpar[nax][2] = kwargs.get(
            "legspace", self.state.legpar[nax][2]
        )
        self.state.legpar[nax][3] = kwargs.get(
            "legpad", self.state.legpar[nax][3]
        )
        self.state.legpar[nax][4] = kwargs.get(
            "legalpha", self.state.legpar[nax][4]
        )

        # Check if another unwanted legend is present and cancel it
        # (only when the legend is called from the plot function)
        if fromplot is True:
            lleg = ax.get_legend()
            if lleg is not None:
                lleg.remove()

        # Check is custom labels are on and plot the legend
        if kwargs.get("label") is not None:
            lab = (
                kwargs["label"]
                if isinstance(kwargs["label"], list)
                else [kwargs["label"]]
            )
            col = makelist(kwargs.get("c", ["k"]))
            ls = makelist(kwargs.get("ls", ["-"]))
            lw = makelist(kwargs.get("lw", [1.5]))
            mrk = makelist(kwargs.get("marker", [""]))
            ms = makelist(kwargs.get("ms", [5.0]))
            fls = makelist(kwargs.get("fillstyle", ["full"]))
            edgcol = makelist(kwargs.get("edgecolor", [None]))
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
                    )
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


def makelist(el: Any) -> list[Any]:
    """If the element is not a list, it converts it into a list.

    Returns
    -------
    - list[Any]
        The list of chosen elements.

    Parameters
    ----------
    - el (not optional): Any
        The element to be converted into a list.

    ----

    Examples
    --------
    - Example #1: element is a list

        >>> makelist([1,2,3])
        [1,2,3]

    - Example #2: element is not a list

        >>> makelist(1)
        [1]

    """
    # Return the element as a list
    return el if isinstance(el, list) else [el]
