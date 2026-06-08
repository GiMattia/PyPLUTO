"""Find-lines utilities manager."""

from __future__ import annotations

import logging
from typing import Unpack

import contourpy as cp
import matplotlib.colors as mcol
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

from pyPLUTO.loadkwargs import FindContourKwargs, FindFieldlinesKwargs
from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState
from pyPLUTO.toolfuncs.loadtools import LoadToolsManager
from pyPLUTO.utils.inspector import track_kwargs

logger = logging.getLogger(__name__)


class FindLinesManager(LoadMixin):
    """Manager for field-line and contour helpers."""

    def __init__(self, state: LoadState) -> None:
        """Initialize the field-line manager and the underlying tools manager.

        Parameters
        ----------
        - state: LoadState
            The load state object providing grid arrays and dataset variables.

        Returns
        -------
        - None

        """
        self.state = state
        self.LoadToolsManager = LoadToolsManager(state)

    @staticmethod
    def _vector_field(
        _t: float,
        y: np.ndarray,
        var1: np.ndarray,
        var2: np.ndarray,
        xc: np.ndarray,
        yc: np.ndarray,
    ) -> list[np.ndarray]:
        """Compute vector field interpolation at position y.

        Parameters
        ----------
        - _t: float
            The time.
        - y: np.ndarray
            The position.
        - var1: np.ndarray
            The first vector component.
        - var2: np.ndarray
            The second vector component.
        - xc: np.ndarray
            The x-coordinates of the grid.
        - yc: np.ndarray
            The y-coordinates of the grid.

        Returns
        -------
        - list[np.ndarray]
            The interpolated vector field.

        """
        x, y = y

        i0 = np.abs(x - xc).argmin()
        j0 = np.abs(y - yc).argmin()

        scrh_ux = np.interp(x, xc, var1[:, j0])
        scrh_uy = np.interp(y, yc, var1[i0])
        scrh_vx = np.interp(x, xc, var2[:, j0])
        scrh_vy = np.interp(y, yc, var2[i0])

        qx = scrh_ux + scrh_uy - var1[i0, j0]
        qy = scrh_vx + scrh_vy - var2[i0, j0]

        return [qx, qy]

    @track_kwargs
    def find_fieldlines(
        self,
        var1: str | np.ndarray,
        var2: str | np.ndarray,
        x0: list | float | None = None,
        y0: list | float | None = None,
        x1: np.ndarray | None = None,
        x2: np.ndarray | None = None,
        text: bool = False,
        _check: bool = True,
        **kwargs: Unpack[FindFieldlinesKwargs],
    ) -> list:
        """Find field lines using the vector field.

        The field lines are computed by interpolating the variables var1 and
        var2 at the footpoints x0 and y0. Different integration algorithms are
        available, based on the method solve_ivp of the scipy package.

        Parameters
        ----------
        - atol: float, default 1e-6
            The absolute tolerance for the integration.
        - closed: bool, default True
            If True, it checks if the line is closed on itself.
        - ctol: float, default 1e-6
            The absolute tolerance for line closing on itself.
        - dense: bool, default False
            If True, the grid is dense (dense=True) or sparse (dense=False).
        - maxstep: float, default 100*step
            The maximum step size for the integration.
        - minstep: float, default 0.05*step
            The minimum step size for the integration
            (only used if order is LSODA).
        - numsteps: int, default 16384
            The maximum number of steps for the integration.
        - order: str, default 'RK45'
            The integration method. Available options are:
            'RK45', 'RK23', 'DOP853', 'Radau', 'BDF', 'LSODA'.
        - rtol: float, default 1e-6
            The relative tolerance for the integration.
        - step: float, default
          abs(min((xend-xbeg)/self.nx1, (yend-ybeg)/self.nx2))
            The initial step size for the integration.
        - text: bool, default False
            If True some additional information is printed.
        - transpose: True/False, default False
            Transposes the variable matrix. Use is not recommended if not
            really necessary (e.g. in case of highly customized variables and
            plots).
        - var1 (not optional): str | np.ndarray
            The first variable to be interpolated.
        - var2 (not optional): str | np.ndarray
            The second variable to be interpolated.
        - x0: list
            The x coordinates of the footpoints.
        - x1: np.ndarray | list | None, default self.x1
            The x coordinates of the grid.
        - x2: np.ndarray | list | None, default self.x2
            The y coordinates of the grid.
        - y0: list
            The y coordinates of the footpoints.

        Returns
        -------
        - linelist: list
            A list of lists containing the coordinates of the field lines.
            The strcuture of the list is [[x1, y1], [x2, y2], ...] where
            x1, y1, x2, y2 are numpy arrays representing the coordinates of
            the field lines.

        Examples
        --------
        - Example #1: Find field lines using the vector field

            >>> find_fieldlines(var1, var2, x0, y0)

        - Example #2: Find field lines using two strings 'Bx1' and 'Bx2'

            >>> find_fieldlines("Bx1", "Bx2", x0, y0)

        - Example #3: Find field lines using two variables and two footpoints

            >>> find_fieldlines(var1, var2, [x1, x2], [y1, y2])

        """
        varx = self.LoadToolsManager.check_var(
            var1,
            kwargs.get("transpose", False),
        )
        vary = self.LoadToolsManager.check_var(
            var2,
            kwargs.get("transpose", False),
        )

        xc = x1 if x1 is not None else self.x1
        yc = x2 if x2 is not None else self.x2

        if x0 is None or y0 is None:
            raise ValueError(
                "Footpoints not provided. Please provide footpoints!",
            )

        x0 = list(np.atleast_1d(x0))
        y0 = list(np.atleast_1d(y0))

        xbeg = xc[0] - 0.51 * (xc[1] - xc[0])
        xend = xc[-1] + 0.51 * (xc[-1] - xc[-2])
        ybeg = yc[0] - 0.51 * (yc[1] - yc[0])
        yend = yc[-1] + 0.51 * (yc[-1] - yc[-2])

        rtol = kwargs.get("rtol", 1.0e-3)
        atol = kwargs.get("atol", 1.0e-6)
        ctol = kwargs.get("ctol", 1.0e-6)
        order = kwargs.get("order", "RK45")
        dense = kwargs.get("dense", False)

        step = np.abs(
            kwargs.get(
                "step",
                min((xend - xbeg) / self.nx1, (yend - ybeg) / self.nx2),
            ),
        )

        maxstep = kwargs.get("maxstep", 100 * step)
        numstep = int(kwargs.get("numsteps", 16384))
        tfin = maxstep * numstep

        def system(t: float, y: np.ndarray) -> list[np.ndarray]:
            """Evaluate the ODE  rhs by interpolating the vector field."""
            return self._vector_field(t, y, varx, vary, xc, yc)

        def outside_domain(t: float, y: np.ndarray) -> float:
            """Return 0 (terminal) when the integrator leaves the domain."""
            if y[0] < xbeg or y[0] > xend or y[1] < ybeg or y[1] > yend:
                return 0
            return 1

        def close_to_start(t: float, y: np.ndarray) -> float:
            """Return 0 when the integrator returns near the seed point."""
            dist_0 = np.linalg.norm(y - np.asarray(self.init_pos))
            if dist_0 < ctol and t > maxstep:
                self.loop_dom = True
                return 0
            self.oldpos = list(y)
            return 1

        def max_num_steps(t: float, y: np.ndarray) -> float:
            """Return 0 when the allowed step count is exceeded."""
            self.stepnum += 1
            if self.stepnum > numstep:
                return 0
            return 1

        close_to_start.terminal = kwargs.get("closed", True) is True  # type: ignore
        close_to_start.direction = 0  # type: ignore

        outside_domain.terminal = True  # type: ignore
        outside_domain.direction = 0  # type: ignore

        max_num_steps.terminal = True  # type: ignore
        max_num_steps.direction = 0  # type: ignore

        lines_list = []
        linekwargs = {}

        if order == "LSODA":
            linekwargs["minstep"] = kwargs.get("minstep", 0.05 * step)

        for ind, xp in enumerate(x0):
            self.loop_dom = False
            yp = y0[ind]
            self.init_pos = [xp, yp]
            self.oldpos = [xp, yp]
            self.stepnum = 0
            t_span = (0, tfin)

            sol_forward = solve_ivp(
                system,
                t_span,
                [xp, yp],
                method=order,
                events=[outside_domain, max_num_steps, close_to_start],
                rtol=rtol,
                atol=atol,
                max_step=maxstep,
                first_step=step,
                dense_output=dense,
                **linekwargs,
            )

            numstep = 0 if self.loop_dom is True else numstep

            forw_steps = self.stepnum
            self.init_pos = [
                sol_forward.y.T[:, 0][-1],
                sol_forward.y.T[:, 1][-1],
            ]
            self.stepnum = 0
            t_span = (0, -tfin)

            sol_backward = solve_ivp(
                system,
                t_span,
                [xp, yp],
                method=order,
                events=[outside_domain, max_num_steps, close_to_start],
                rtol=rtol,
                atol=atol,
                max_step=maxstep,
                first_step=step,
                dense_output=dense,
                **linekwargs,
            )

            x_line = np.vstack((sol_backward.y.T[::-1], sol_forward.y.T))[:, 0]
            y_line = np.vstack((sol_backward.y.T[::-1], sol_forward.y.T))[:, 1]

            if self.loop_dom is True:
                x_line = np.append(x_line, x_line[0])
                y_line = np.append(y_line, y_line[0])

            if text is True:
                logger.debug("Line with footpoint at x = %s and y = %s", xp, yp)
                logger.debug(
                    "Final integration time forward:  %s",
                    sol_forward.t[-1],
                )
                logger.debug(
                    "Final integration time backward: %s",
                    sol_backward.t[-1],
                )
                logger.debug("Final step number forward:       %s", forw_steps)
                logger.debug(
                    "Final step number backward:      %s",
                    self.stepnum,
                )

            if len(x_line) > 1:
                lines_list.append([x_line, y_line])

        for method_name in ["init_pos", "stepnum", "out_dom", "oldpos"]:
            if method_name in self.__class__.__dict__:
                delattr(self.__class__, method_name)

        return lines_list

    @track_kwargs
    def find_contour(
        self,
        var: str | np.ndarray,
        _check: bool = True,
        **kwargs: Unpack[FindContourKwargs],
    ) -> list:
        """Generate contour lines for a given variable.

        Parameters
        ----------
        - levels: int | np.ndarray, default 10
            The levels of number of levels or the list of levels for the
            contours. If an integer is provided, the levels are generated using
            a linear or logarithmic scale. If an array is provided, the levels
            are taken from the array.
        - levelscale: str, default 'linear'
            The scale of the levels. Available options are 'linear' and
            'logarithmic'.
        - line_cmap: str, default 'k'
            The colormap to use to associate each level with a color.
            The colormap can also be a color, which is used for all the levels.
            If not provided, all the lines are associated with the color black.
        - transpose: True/False, default False
            Transposes the variable matrix. Use is not recommended if not
            really necessary (e.g. in case of highly customized variables and
            plots).
        - var (not optional): str | np.ndarray
            The variable to plot. If a string is provided, the variable is taken
            from the dataset.
        - vmax: float
            The maximum value of the variable to be computed / plotted.
        - vmin: float
            The minimum value of the variable to be computed / plotted.
        - x1: np.ndarray, default self.x1
            The x1 coordinates. If the geometry is non-Cartesian, the x1
            cartesian coordinates are taken from the dataset.
        - x2: np.ndarray, default self.x2
            The x2 coordinates. If the geometry is non-Cartesian, the x2
            cartesian coordinates are taken from the dataset.

        Returns
        -------
        - lines_list: list
            List of contour lines. The strcuture of the list is
            [[x1, y1], [x2, y2], ...] where x1, y1, x2, y2 are numpy arrays
            representing the coordinates of the field lines.

        Examples
        --------
        - Example #1: Generate contour lines for a given variable.

            >>> lines_list = find_contour(var)

        - Example #2: Generate contour lines for a given variable and
            coordinates.

            >>> lines_list = find_contour(var, x1=x1, x2=x2)

        - Example #3: Generate contour lines for a given variable and
            coordinates with a logarithmic scale.

            >>> lines_list = find_contour(var, x1=x1, x2=x2,
            >>> ... levelscale='logarithmic')

        - Example #4: Generate contour lines for a given variable and
            coordinates with a logarithmic scale and a colormap.

            >>> lines_list = find_contour(var, x1=x1, x2=x2,
            >>> ... levelscale='logarithmic', line_cmap='jet')

        """
        var = self.LoadToolsManager.check_var(
            var,
            kwargs.get("transpose", False),
        ).T

        if self.geom == "SPHERICAL":
            x1 = self.x1p
            x2 = self.x2p
        elif self.geom == "POLAR" and self.nx2 == 1:
            x1 = self.x1
            x2 = self.x3
        elif self.geom == "POLAR":
            x1 = self.x1c
            x2 = self.x2c
        else:
            x1 = self.x1
            x2 = self.x2

        x1 = kwargs.get("x1", x1)
        x2 = kwargs.get("x2", x2)

        vmin = kwargs.get("vmin", np.nanmin(var))
        vmax = kwargs.get("vmax", np.nanmax(var))

        levels = kwargs.get("levels", 10)
        levelscale = kwargs.get("levelscale", "linear")

        if isinstance(levels, int):
            levels = (
                np.linspace(vmin, vmax, levels)
                if levelscale == "linear"
                else np.logspace(np.log10(vmin), np.log10(vmax), levels)
            )

        if isinstance(levels, float):
            levels = [levels]

        if "line_cmap" in kwargs:
            cmap_val = kwargs.get("line_cmap")
            if cmap_val is None:
                cmap = mcol.ListedColormap(["k"])
            else:
                try:
                    cmap = plt.get_cmap(cmap_val)
                except (ValueError, TypeError):
                    cmap = mcol.ListedColormap(cmap_val)
        else:
            cmap = mcol.ListedColormap(["k"])

        lines_list = []

        cont_gen = cp.contour_generator(x1, x2, var, name="serial")
        for indx, level in enumerate(levels):
            contour = cont_gen.lines(level)
            for line in contour:
                line_arr = np.asarray(line)
                x_c = line_arr[:, 0]
                y_c = line_arr[:, 1]
                col = (
                    cmap(indx / (len(levels) - 1))
                    if "line_cmap" in kwargs
                    else "k"
                )

                if len(line_arr) > 1:
                    lines_list.append([x_c, y_c, col])

        return lines_list
