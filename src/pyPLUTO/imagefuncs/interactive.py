"""Interactive functions for image manipulation and display."""

from __future__ import annotations

import inspect
from collections.abc import Iterable
from pathlib import Path
from typing import Unpack

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.collections import Collection, QuadMesh
from matplotlib.lines import Line2D
from matplotlib.widgets import Slider

from pyPLUTO.imagefuncs.display import DisplayManager
from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.plot import PlotManager
from pyPLUTO.imagekwargs import DisplayKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs


class InteractiveManager(ImageMixin):
    """InteractiveManager class.

    It provides methods to create interactive plots with sliders to change the
    data. It is designed to work with fluid variables and allows for dynamic
    visualization of data as a function of time. The class uses the
    DisplayManager and PlotManager to handle the display and plotting of the
    data, respectively.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the InteractiveManager with the given state."""
        self.state = state
        self.DisplayManager = DisplayManager(state)
        self.ImageToolsManager = ImageToolsManager(state)

        self.PlotManager = PlotManager(state)
        self.anim_pcm: Collection | Line2D | None = None
        self.labslider: list[str | float] | None = None
        self.anim_ax: Axes | None = None
        self.anim_var: dict[str, np.ndarray] | np.ndarray
        self.animkeys: np.ndarray | None = None
        self.nsld: int = 0
        self.lenlab: int = 0
        self.limfix: bool = True
        self.slider: Slider | None = None
        self.two_dim: int = 2

    @track_kwargs
    def interactive(
        self,
        varx: dict[str, np.ndarray] | np.ndarray,
        vary: dict[str, np.ndarray] | None = None,
        limfix: bool = True,
        labslider: list[str | float] | None = None,
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[DisplayKwargs],
    ) -> None:
        """Create an interactive plot with a slider to change the data.

        Warning: it works only with the fluid variables.

        Parameters
        ----------
        - alpha: float, default 1.0
            Sets the opacity of the plot, where 1.0 is fully opaque and 0.0 is
            fully transparent.
        - aspect: 'auto' | 'equal' | float, default 'auto'
            Sets the aspect ratio of the plot. The 'auto' keyword is the
            default option. The 'equal' keyword sets the same scaling for x and
            y. A float fixes the ratio between the y-scale and the x-scale (1.0
            is the same as 'equal').
        - ax: ax | int | None, default None
            The axis where to plot. If None, the last considered axis will be
            used.
        - bottom: float, default varies
            The bottom limit of the axis / axes set. For the figure layout it
            is the space from the bottom border to the plot (default 0.1); for
            an inset zoom it is the bottom position of the inset (default 0.6 +
            height).
        - c: str, default self.color
            Determines the color. If not defined, the program will loop over an
            array of 6 colors which are different for the most common vision
            deficiencies.
        - clabel: str, default None
            Sets the label of the colorbar.
        - cmap: str, default 'hot'
            Selects the colormap. Some useful colormaps are: plasma, magma,
            seismic. Please avoid colormaps like jet or rainbow, which are not
            perceptively uniform and not suited for people with vision
            deficiencies.
        - cpad: float, default 0.07
            Fraction of original axes between colorbar and the axes (in axes
            units).
        - cpos: {'top','bottom','left','right'}, default None
            Enables the colorbar and sets its position. If not defined, no
            colorbar is shown.
        - cscale: {'linear','log','symlog','twoslope'}, default 'linear'
            Sets the colorbar scale. Default is the linear ('norm') scale.
        - cticks: {[float], None}, default None
            If enabled (and different from None), sets manually the ticks on
            the colorbar.
        - ctickslabels: str, default None
            If enabled, sets manually ticks labels on the colorbar.
        - edgecolor: list[str], default [None]
            Sets the edge color of the legend. The default value is black
            ('k').
        - extend: {'neither','both','min','max'}, default 'neither'
            Sets the extension of the triangular colorbar extension.
        - extendrect: bool, default False
            If True, the colorbar extension will be triangular.
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
        - grid: bool | string, default False
            Enables/disables the grid on the plot. If True it enables both axes
            grids. If 'x' or 'y' it enables only the x- or y-axis grid.
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
        - labelsize: float, default fontsize
            Sets the labels fontsize (which is the same for both labels). The
            default value corresponds to the value of the keyword 'fontsize'.
        - labslider: str, default None
            The label of the slider.
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
        - limfix: bool, default True
            If True, the colorbar limits are fixed through the entire
            animation.
        - lint: bool, default None
            If True, enables linear interpolation between frames in the
            interactive plot.
        - ls: {'-', '--', '-.', ':', ' ', etc.}, default '-'
            Sets the linestyle. The choices available are the ones defined in
            the matplotlib package.
        - lw: float, default 1.3
            Sets the linewidth.
        - marker: {'o', 'v', '^', '<', '>', 'X', ' ', etc.}, default ' '
            Sets an optional symbol for every point. The default value is no
            marker (' ').
        - minorticks: str, default None
            If not None enables the minor ticks on the plot (for both grid
            axes).
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
        - shading: {'flat', 'nearest', 'auto', 'gouraud'}, default 'auto'
            The shading between the grid points. If not defined, the shading
            will be one between 'flat' and 'nearest' depending on the size of
            the x, y and z arrays. The 'flat' shading works only if, given a
            NxM z-array, the x- and y-arrays have sizes of, respectively, N+1
            and M+1. All the other shadings require a N x-array and a M
            y-array.
        - sharex: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the x-axis between the subplots.
        - sharey: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the y-axis between the subplots.
        - suptitle: str, default None
            Creates a figure title over all the subplots.
        - ticksdir: {'in', 'out'}, default 'in'
            Sets the ticks direction. The default option is 'in'.
        - tickssize: float | bool, default True
            Sets the ticks fontsize (which is the same for both grid axes). The
            default value corresponds to the value of the keyword 'fontsize'.
        - tight: bool, default True
            Enables/disables tight layout options for the figure. In case of a
            highly customized plot (e.g. ratios or space between rows and
            columns) the option is set by default to False since that option
            would not be available for standard matplotlib functions.
        - title: str, default None
            Places the title of the plot on top of it.
        - titlepad: float, default 8.0
            Sets the distance between the title and the top of the plot.
        - titlesize: float, default fontsize
            Sets the title fontsize. The default value corresponds to the value
            of the keyword 'fontsize'.
        - top: float, default varies
            The top limit of the axis / axes set. For the figure layout it is
            the space from the top border to the plot (default 0.9); for an
            inset zoom it is the top position of the inset (default bottom +
            height).
        - transpose: True/False, default False
            Transposes the variable matrix. Use is not recommended if not
            really necessary (e.g. in case of highly customized variables and
            plots).
        - tresh: float, default max(abs(vmin),vmax)*0.01
            Sets the threshold for the colormap (used with composite
            colorscales such as twoslope or symlog).
        - varx (not optional): array_like
            The x-axis variable.
        - vary: array_like, default None
            The y-axis variable.
        - vmax: float
            The maximum value of the variable to be computed / plotted.
        - vmin: float
            The minimum value of the variable to be computed / plotted.
        - wratio: [float], default [1.0]
            Ratio between the columns of the plot. The default is that every
            plot column has the same width.
        - wspace: [float], default []
            The space between plot columns (in figure units). If not enough or
            too many spaces are considered, the program will remove the excess
            and fill the lacks with [0.1].
        - x1: np.ndarray, default 'Default'
            The x-axis array. If not defined, a default array will be
            generated.
        - x2: np.ndarray, default 'Default'
            The y-axis array. If not defined, a default array will be
            generated.
        - xlabelpad: float, default 4.0
            The padding between the x-axis label and the axis.
        - xrange: [float, float], default 'Default'
            Sets the range in the x-direction. If not defined, the range is
            computed automatically from the x-array.
        - xscale: {'linear','log'}, default 'linear'
            If enabled (and different from 'Default'), sets automatically the
            scale on the x-axis. Data in log scale should be used with the
            keyword 'log', while data in linear scale should be used with the
            keyword 'linear'.
        - xticks: list[float] | None | bool, default True
            If enabled (and different from True), sets manually ticks on the
            x-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - xtickslabels: list[str] | None | bool, default True
            If enabled (and different from True), sets manually the ticks
            labels on the x-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels
            should always correspond to fixed ticks.
        - xtitle: str, default None
            Sets and places the label of the x-axis.
        - xtresh: float
            The threshold parameter for the x-axis symlog/asinh scale.
        - ylabelpad: float, default 4.0
            The padding between the y-axis label and the axis.
        - yrange: [float, float], default 'Default'
            Sets the range in the y-direction. If not defined, the range is
            computed automatically from the y-array.
        - yscale: {'linear','log'}, default 'linear'
            If enabled (and different from 'Default'), sets automatically the
            scale on the y-axis. Data in log scale should be used with the
            keyword 'log', while data in linear scale should be used with the
            keyword 'linear'.
        - yticks: list[float] | None | bool, default True
            If enabled (and different from True), sets manually ticks on the
            y-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - ytickslabels: list[str] | None | bool, default True
            If enabled (and different from True), sets manually the ticks
            labels on the y-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels
            should always correspond to fixed ticks.
        - ytitle: str, default None
            Sets and places the label of the y-axis.
        - ytresh: float
            The threshold parameter for the y-axis symlog/asinh scale.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Create an interactive 2D plot

            >>> import pyPLUTO as pp
            >>> D = pp.Load("all")
            >>> I = pp.Image()
            >>> I.interactive(
            ...     D.rho, x1=D.x1, x2=D.x2, cpos="right", vmin=0, vmax=1.0
            ... )
            >>> pp.show()

        - Example #2: Create an interactive 1D plot with a composite variable

            >>> import pyPLUTO as pp
            >>> import numpy as np
            >>> D = pp.Load("all")
            >>> pp.Image().interactive(D.x1, np.sqrt(D.vx1**2 + D.vx2**2))
            >>> pp.show()

        """
        # Store the variable x. If vary is None, it is set to varx
        if vary is None:
            if isinstance(varx, dict):
                self.anim_var = varx
            else:
                raise ValueError("varx must be a dictionary")

        else:
            self.anim_var = vary

        # Store the variable to animate
        self.animkeys = np.sort(np.asarray(list(self.anim_var.keys())))
        self.nsld = len(self.animkeys)
        nsld = self.nsld - 1
        self.lenlab = len(str(self.animkeys[-1]))

        # Check the number of dimensions
        splt = np.ndim(self.anim_var[self.animkeys[0]])

        # Set or create figure and axes (to test)
        # Set or create figure and axes
        kwargs["tight"] = False
        ax, _ = self.ImageToolsManager.assign_ax(ax, _check=False, **kwargs)

        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )

        self.anim_ax = ax

        # Position the slider
        pos_slider = ax.get_position()
        pos_x0 = pos_slider.x0 * (1.5 + 0.2 * (self.lenlab - 2))
        pos_x1 = pos_slider.x1 * 0.95 - pos_x0

        # Adjust the lower part of the position by increasing the 'y0' value
        if "xtitle" in kwargs:
            new_pos = (
                pos_slider.x0,
                pos_slider.y0 + 0.07,
                pos_slider.width,
                pos_slider.height - 0.07,
            )

            # Apply the new position
            ax.set_position(new_pos)

        sliderax = self.state.fig.add_axes((pos_x0, 0.02, pos_x1, 0.04))

        # Create the slider
        if labslider is not None:
            self.labslider = labslider
            label = labslider[0]
        else:
            self.labslider = None
            label = f"nout = {self.animkeys[0]:0{self.lenlab}d}"
        self.slider = Slider(
            sliderax,
            label=str(label),
            valmin=0,
            valmax=nsld,
            valinit=0,
            valstep=1,
            valfmt="%d",
        )
        self.slider.on_changed(self.update_slider)

        # Display the data
        if splt == self.two_dim:
            self.limfix = limfix
            vmin = (
                min(
                    float(np.nanmin(np.asarray(array)))
                    for array in self.anim_var.values()
                )
                if limfix is True
                else np.nanmin(self.anim_var[self.animkeys[0]])
            )
            vmax = (
                max(
                    float(np.nanmax(np.asarray(array)))
                    for array in self.anim_var.values()
                )
                if limfix is True
                else np.nanmax(self.anim_var[self.animkeys[0]])
            )
            kwargs["vmin"] = kwargs.pop("vmin", vmin)
            kwargs["vmax"] = kwargs.pop("vmax", vmax)

            # Display the data if it is 2D
            self.DisplayManager.display(
                self.anim_var[self.animkeys[0]],
                ax=ax,
                **kwargs,
            )
            self.anim_pcm = ax.collections[0]
        else:
            var = np.array(self.anim_var[self.animkeys[0]].tolist())
            if isinstance(varx, dict):
                varx = np.array(range(len(var)))

            # Plot the data if it is 1D
            self.PlotManager.plot(
                varx,
                var,
                ax=ax,
                _check=False,
                **kwargs,
            )
            self.anim_pcm = ax.get_lines()[0]

    def update_slider(self, i: float) -> Iterable[Artist]:
        """Update the data in the interactive plot.

        Parameters
        ----------
        - i  (not optional): int
            The slider index.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Update the data in the interactive plot

            >>> _update_slider(1)

        """
        # Update the data
        if self.animkeys is None or self.anim_var is None:
            raise ValueError(
                "No data is present. Please create an interactive plot first."
            )

        if self.slider is None:
            raise ValueError(
                "No slider is present. Please create an interactive plot first."
            )
        idx = int(i)
        var = self.anim_var[self.animkeys[idx]]
        if np.ndim(var) == self.two_dim:
            if not isinstance(self.anim_pcm, QuadMesh):
                raise ValueError(
                    "The current plot is not a 2D plot. "
                    "Please use a 2D variable."
                )
            # Update the data array if it is 2D
            self.anim_pcm.set_array(var.T.ravel())

            # Update vmin and vmax dynamically
            if self.limfix is False:
                self.anim_pcm.set_clim(
                    self.anim_var[self.animkeys[idx]].min(),
                    self.anim_var[self.animkeys[idx]].max(),
                )

        elif np.ndim(var) == 1:
            if not isinstance(self.anim_pcm, Line2D):
                raise ValueError(
                    "The current plot is not a 1D plot. "
                    "Please use a 1D variable."
                )
            # Update the data array if it is 1D
            self.anim_pcm.set_ydata(var)

        if isinstance(self.labslider, list):
            self.slider.label.set_text(str(self.labslider[idx]))
        else:
            self.slider.label.set_text(
                f"nout = {self.animkeys[idx]:0{self.lenlab}d}"
            )

        # Update the plot
        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )
        self.state.fig.canvas.draw()

        # End of the function
        return ()

    def update_both(self, i: float) -> Iterable[Artist]:
        """Update both the plot and the slider value during animation.

        Parameters
        ----------
        - i (not optional): int
            The current frame index.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Update the data in the interactive plot

            >>> _update_slider(1)

        """
        if self.slider is None:
            raise ValueError(
                "No slider is present. Please create an interactive plot first."
            )
        # Update the plot with the current frame
        self.update_slider(i)

        # Update the slider's position visually
        self.slider.set_val(i)

        # End of the function
        return ()

    def animate(
        self,
        gifname: str | None = None,
        frames: int | None = None,
        interval: int = 500,
        updateslider: bool = True,
        script_relative: bool = False,
    ) -> None:
        """Display the animation interactively.

        Parameters
        ----------
        - frames: int, default None
            The number of frames in the animation.
        - gifname: str, default None
            The name of the GIF file.
        - interval: int, default 500
            The interval between frames in milliseconds.
        - script_relative: bool, default False
            If True, the image is saved in the same directory as the script
            calling this method. If False, the image is saved in the current
            working directory.
        - updateslider: bool, default True
            If True, the slider is shown and updated with each frame.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Display the animation

            >>> animate()

        - Example #2: Display the animation with a specific number of frames

            >>> animate(frames=[0, 1, 2], interval=300)

        """
        # Choose the frames
        frames = self.nsld if frames is None else frames

        update = self.update_both if updateslider else self.update_slider

        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )

        # Create the animation
        ani = animation.FuncAnimation(
            self.state.fig, update, frames=frames, interval=interval
        )

        if gifname is not None:
            out_path = Path(gifname)

            if script_relative and not out_path.is_absolute():
                # Find the path of the script calling this method
                caller_file = Path(inspect.stack()[1].filename).resolve()
                base_dir = caller_file.parent
                out_path = base_dir / out_path

            # Save as GIF
            ani.save(out_path)

            plt.close(self.state.fig)

        else:
            # Display the animation
            plt.show()
