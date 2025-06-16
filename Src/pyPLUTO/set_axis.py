from typing import Any

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from .delegator import delegator
from .imagestate import ImageState
from .inspector import track_kwargs


@delegator("state")
class AxisManager:

    exposed_methods = ("set_axis",)

    def __init__(self, state: ImageState) -> None:

        self.state = state

    @track_kwargs
    def set_axis(
        self, ax: Axes | None = None, check: bool = True, **kwargs: Any
    ) -> None:
        """Customization of a single subplot axis. Properties such as the
        range, scale and aspect of each subplot should be customized here.

        Returns
        -------
        - None

        Parameters
        ----------
        - alpha: float, default 1.0
            Sets the opacity of the plot, where 1.0 means total opaque and 0.0
            means total transparent.
        - aspect: {'auto', 'equal', float}, default 'auto'
            Sets the aspect ratio of the plot. The 'auto' keyword is the default
            option (most likely the plot will be squared). The 'equal' keyword
            will set the same scaling for x and y. A float will fix the ratio
            between the y-scale and the x-scale (1.0 is the same as 'equal').
        - ax: ax object, default None
            The axis to customize. If None the current axis will be selected.
        - fontsize: float, default 17.0
            Sets the fontsize for all the axis components (only for the current
            axis).
        - grid: bool | string, default False
            Enables/disables the grid on the plot. If True it enables both axes
            grids. If 'x' or 'y' it enables only the x or y axis grid.
        - labelsize: float, default fontsize
            Sets the labels fontsize (which is the same for both labels).
            The default value corresponds to the value of the keyword
            'fontsize'.
        - minorticks: str, default None
            If not None enables the minor ticks on the plot (for both grid
            axes).
        - sharex: Matplotlib axis | False, default False
            Shares the x-axis with another axis.
        - sharey: Matplotlib axis | False, default False
            Shares the y-axis with another axis.
        - ticksdir: {'in', 'out'}, default 'in'
            Sets the ticks direction. The default option is 'in'.
        - tickssize: float | bool, default True
            Sets the ticks fontsize (which is the same for both grid axes).
            The default value corresponds to the value of the keyword
            'fontsize'.
        - title: str, default None
            Places the title of the plot on top of it.
        - titlepad: float, default 8.0
            Sets the distance between the title and the top of the plot
        - titlesize: float, default fontsize
            Sets the title fontsize. The default value corresponds to the value
            of the keyword 'fontsize'.
        - xrange: [float, float], default [0,1]
            Sets the range in the x-direction. If not defined the code will
            compute the range while plotting the data.
        - xscale: {'linear','log'}, default 'linear'
            If enabled (and different from True), sets automatically the scale
            on the x-axis. Data in log scale should be used with the keyword
            'log', while data in linear scale should be used with the keyword
            'linear'.
        - xticks: {[float], None, True}, default True
            If enabled (and different from True), sets manually ticks on
            x-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - xtickslabels: {[str], None, True}, default True
            If enabled (and different from True), sets manually the ticks
            labels on the x-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels should
            always correspond to fixed ticks.
        - xtitle: str, default None
            Sets and places the label of the x-axis.
        - yrange: [float, float], default [0,1]
            Sets the range in the y-direction. If not defined the code will
            compute the range while plotting the data.
        - yscale: {'linear','log'}, default 'linear'
            If enabled (and different from True), sets automatically the scale
            on the y-axis. Data in log scale should be used with the keyword
            'log', while data in linear scale should be used with the keyword
            'linear'.
        - yticks: {[float], None, True}, default True
            If enabled (and different from True), sets manually ticks on
            y-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - ytickslabels: {[str], None, True}, default True
            If enabled (and different from True), sets manually the ticks
            labels on the y-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels should
            always correspond to fixed ticks.
        - ytitle: str, default None
            Sets and places the label of the y-axis.


        Notes
        -----
        - A function which sets seprartely the maximum and the minimum value in
            both x- and y- directions is needed.

        ----

        Examples
        --------
        - Example #1: create an axis and set title and labels on both axes

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes()
            >>> I.set_axis(title = 'Title', titlesize = 30.0, xtitle = 'x-axis',
            ... ytitle = 'y-axis')

        - Example #2: create an axis, remove the ticks for the x-axis and
            set manually the ticks for the y-axis

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes()
            >>> I.set_axis(ax, xticks = None, yrange = [-1.0,1.0],
            ... yticks = [-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8])

        - Example #3: create two axes and invert the direction of the ticks in
            the first one

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes(right = 0.7)
            >>> ax = I.create_axes(left = 0.8)
            >>> I.set_axis(ax = ax[0], ticksdir = 'out')

        - Example #4: create a 2x2 grid with axes labels and customed ticks

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes(ncol = 2, nrow = 2)
            >>> for i in [0,1,2,3]:
            ...     I.set_axis(ax = ax[i], xtitle = 'x-axis',
            ...     ytitle = 'y-title',
            ...     xticks = [0.25,0.5,0.75], yticks = [0.25,0.5,0.75],
            ...     xtickslabels = ['1/4','1/2','3/4'])

        """
        # Set fontsize
        self.state.fontsize = kwargs.get("fontsize", self.state.fontsize)
        plt.rcParams.update({"font.size": self.state.fontsize})

        # Add create_axes just in case
        # ax = self.mediator.create_axes(ncol=1, nrow=1, check=False, **kwargs)

        # Take last axis if not specified
        ax, nax = self.assign_ax(ax, **kwargs)

        if ax is None:
            raise ValueError("No axis can be set!")

        # Set aspect ratio
        if not kwargs.get("aspect", True):
            ax.set_aspect(kwargs["aspect"])

        # Set xrange and yrange
        if kwargs.get("xrange") is not None:
            self.mediator.set_xrange(ax, nax, kwargs["xrange"], 3, "pippo")
        if kwargs.get("yrange") is not None:
            self.mediator.set_yrange(ax, nax, kwargs["yrange"], 3)

        # Set title and axes labels
        if kwargs.get("title") is not None:
            ax.set_title(
                kwargs["title"],
                fontsize=kwargs.get("titlesize", self.state.fontsize),
                pad=kwargs.get("titlepad", 8.0),
            )

    def assign_ax(
        self, ax: Axes | list[Axes] | None, **kwargs: Any
    ) -> tuple[Axes, int]:
        """Sets the axes of the figure where the plot/feature should go.
        If no axis is present, an axis is created. If the axis is
        present but no axis is seletced, the last axis is selected.

        Returns
        -------
        - ax: ax | list[ax] | int | None
            The selected set of axes.
        - nax: int
            The number of the selected set of axes.

        Parameters
        ----------
        - ax (not optional): ax | int | list[ax] | None
            The selected set of axes.
        - **kwargs: Any
            The keyword arguments to be passed to the create_axes function
            (not written here since is not public method).

        Notes
        -----
        - None

        ----

        Examples
        --------
        - Example #1: Set the axes of the figure

            >>> _assign_ax(ax, **kwargs)

        - Example #2: Set the axes of the figure (no axis selected)

            >>> _assign_ax(None, **kwargs)

        - Example #3: Set the axes of the figure (axis is a list)

            >>> _assign_ax([ax], **kwargs)

        """
        # Check if the axis is None and no axis is present (and create one)
        if ax is None and len(self.state.ax) == 0:
            ax = self.mediator.create_axes(
                ncol=1, nrow=1, check=False, **kwargs
            )

        # Check if the axis is None and an axis is present (and select the last one,
        # the current axis if it belongs to the one saved in the figure or the last
        # one saved
        elif ax is None and len(self.state.ax) > 0:
            if self.state.fig is None:
                raise ValueError("No figure is present.")
            ax = (
                self.state.fig.gca()
                if self.state.fig.gca() in self.state.ax
                else self.state.ax[-1]
            )

        # Check if the axis is a list and select the first element
        elif isinstance(ax, list):
            ax = ax[0]

        # Check if the axis is an int, and select the corresponding axis from
        # the list of axes
        elif isinstance(ax, int):
            ax = self.state.ax[ax]

        # If none of the previous cases is satisfied assert that ax is an axis
        if not isinstance(ax, Axes):
            raise ValueError("The provided axis is not valid.")

        # Get the figure associated to the axes
        fig = ax.get_figure()

        # Check if the figure is the same as the one in the class
        if fig != self.state.fig:
            text = "The provided axis does not belong to the expected figure."
            raise ValueError(text)

        # Find the number of the axes and return it
        nax = self.state.ax.index(ax)

        # Return the axis and its index
        return ax, nax
