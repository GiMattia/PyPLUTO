from typing import Any

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from .delegator import delegator
from .imagestate import ImageState
from .inspect_kwargs import track_kwargs


@delegator("state")
class AxesManager:

    @track_kwargs
    def __init__(self, state: ImageState, **kwargs: Any) -> None:
        self.state = state

    @track_kwargs
    def create_axes(
        self, ncol: int = 1, nrow: int = 1, check: bool = True, **kwargs: Any
    ) -> Axes | None:
        """Creation of a set of axes using add_subplot from the matplotlib
        library.

        If additional parameters (like the figure limits or the spacing)
        are given, the plots are located using set_position.
        The spacing and the ratio between the plots can be given by hand.
        In case only few custom options are given, the code computes the rest
        (but gives a small warning); in case no custom option is given, the axes
        are located through the standard methods of matplotlib.

        If more axes are created in the figure, the list of all axes is
        returned, otherwise the single axis is returned.

        Returns
        -------
        - The list of axes (if more axes are in the figure) or the axis
        (if only one axis is present)

        Parameters
        ----------
        - bottom: float, default 0.1
            The space from the bottom border to the last row of plots.
        - figsize: [float, float], default [6*sqrt(ncol),5*sqrt(nrow)]
            Sets the figure size. The default value is computed from the number
            of rows and columns.
        - fontsize: float, default 17.0
            Sets the fontsize for all the axes.
        - hratio: [float], default [1.0]
            Ratio between the rows of the plot. The default is that every plot
            row has the same height.
        - hspace: [float], default []
            The space between plot rows (in figure units). If not enough or
            too many spaces are considered, the program will remove the excess
            and fill the lacks with [0.1].
        - left: float, default 0.125
            The space from the left border to the leftmost column of plots.
        - ncol: int, default 1
            The number of columns of subplots.
        - nrow: int, default 1
            The number of rows of subplots.
        - proj: str, default None
            Custom projection for the plot (e.g. 3D). Recommended only if
            needed.
            WARNING: pyPLUTO does not support 3D plotting for now, only 3D axes.
            The 3D plot feature will be available in future releases.
        - right: float, default 0.9
            The space from the right border to the rightmost column of plots.
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
        - top: float, default 0.9
            The space from the top border to the first row of plots.
        - wratio: [float], default [1.0]
            Ratio between the columns of the plot. The default is that every
            plot column has the same width.
        - wspace: [float], default []
            The space between plot columns (in figure units). If not enough or
            too many spaces are considered, the program will remove the excess
            and fill the lacks with [0.1].

        Notes
        -----
        - The subplot_mosaic method of matplotlib will be implemented in future
        releases.
        - This method may return None in the future releases
        - Sharex and sharey will follow a different implementation in future
        releases

        ----

        Examples
        --------
        - Example #1: create a simple grid of 2 columns and 2 rows on a new
          figure

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes(ncol = 2, nrow = 2)

        - Example #2: create a grid of 2 columns with the first one having half
          the width of the second one

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes(ncol = 2, wratio = [0.5,1])

        - Example #3: create a grid of 2 rows with a lot of blank space between
          them

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes(nrow = 2, hspace = [0.5])

        - Example #4: create a 2x2 grid with a fifth image on the right side

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes(ncol = 2, nrow = 2, right = 0.7)
            >>> ax = I.create_axes(left = 0.75)

        """
        # Change fontsize if requested
        if "fontsize" in kwargs:
            plt.rcParams.update({"font.size": kwargs["fontsize"]})
        print("Axes created! LOL")
        return None
