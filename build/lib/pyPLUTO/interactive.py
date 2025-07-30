import inspect
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.collections import Collection, QuadMesh
from matplotlib.lines import Line2D
from matplotlib.widgets import Slider
from numpy.typing import NDArray

from .delegator import delegator
from .display import DisplayManager
from .imagestate import ImageState
from .imagetools import ImageToolsManager
from .inspector import track_kwargs
from .plot import PlotManager


@delegator("state")
class InteractiveManager:
    """InteractiveManager class. It provides methods to create interactive
    plots with sliders to change the data. It is designed to work with fluid
    variables and allows for dynamic visualization of data as a function of
    time. The class uses the DisplayManager and PlotManager to handle the
    display and plotting of the data, respectively."""

    exposed_methods = (
        "animate",
        "interactive",
    )

    def __init__(self, state: ImageState):
        """Initializes the InteractiveManager with the given state."""
        self.state = state
        self.DisplayManager = DisplayManager(state)
        self.ImageToolsManager = ImageToolsManager(state)

        self.PlotManager = PlotManager(state)
        self.anim_pcm: Collection | Line2D | None = None
        self.labslider: list[str | float] | None = None
        self.anim_ax: Axes | None = None
        self.anim_var: dict[str, NDArray[Any]] | NDArray[Any] | None = None
        self.animkeys: NDArray[Any] | None = None
        self.nsld: int = 0
        self.lenlab: int = 0
        self.limfix: bool = True
        self.slider: Slider | None = None

    @track_kwargs
    def interactive(
        self,
        varx: dict[str, NDArray[Any]] | NDArray[Any],
        vary: dict[str, NDArray[Any]] | None = None,
        check: bool = True,
        limfix: bool = True,
        labslider: list[str | float] | None = None,
        **kwargs: Any,
    ) -> None:
        """Creates an interactive plot with a slider to change the data.
        Warning: it works only with the fluid variables.

        Returns
        -------
        - None

        Parameters
        ----------
        - varx (not optional): array_like
            The x-axis variable.
        - vary: array_like, default None
            The y-axis variable.
        - ax: Axes, default None
            The axes instance.
        - labslider: str, default None
            The label of the slider.
        - limfix: bool, default True
            If True, the colorbar limits are fixed through the entire animation.
        - **kwargs: Any
            Other parameters to pass used in the plot or display functions.
        - vmin: float, default None
            The minimum value of the data.
        - vmax: float, default None
            The maximum value of the data.

        ----

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
        kwargs.pop("check", check)

        # Store the variable x. If vary is None, it is set to varx
        if vary is None:
            if isinstance(varx, dict):
                self.anim_var = varx
                scrh = np.asarray(list(varx.keys()))[0]
                splt = np.ndim(varx[scrh])
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
        ax, _ = self.ImageToolsManager.assign_ax(
            kwargs.pop("ax", None), **kwargs, tight=False
        )

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
        if splt == 2:
            self.limfix = limfix
            vmin = (
                min(np.nanmin(array) for array in self.anim_var.values())
                if limfix is True
                else np.nanmin(self.anim_var[self.animkeys[0]])
            )
            vmax = (
                max(np.nanmax(array) for array in self.anim_var.values())
                if limfix is True
                else np.nanmax(self.anim_var[self.animkeys[0]])
            )
            vmin = kwargs.pop("vmin", vmin)
            vmax = kwargs.pop("vmax", vmax)

            # Display the data if it is 2D
            self.DisplayManager.display(
                self.anim_var[self.animkeys[0]],
                ax=ax,
                vmin=vmin,
                vmax=vmax,
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
                **kwargs,
            )
            self.anim_pcm = ax.get_lines()[0]

    def update_slider(self, i: float) -> Iterable[Artist]:
        """Updates the data in the interactive plot.

        Returns
        -------
        - None

        Parameters
        ----------
        - i  (not optional): int
            The slider index.

        ----

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
        if np.ndim(var) == 2:
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
        """Updates both the plot and the slider value during animation.

        Returns
        -------
        - None


        Parameters
        ----------
        - i (not optional): int
            The current frame index.

        ----

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
        """Displays the animation interactively.

        Returns
        -------
        - None

        Parameters
        ----------
        - frames: int, default None
            The number of frames in the animation.
        - gifname: str, default None
            The name of the GIF file.
        - interval: int, default 500
            The interval between frames in milliseconds.
        - updateslider: bool, default True
            If True, the slider is shown and updated with each frame.

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
