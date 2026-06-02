"""Find-lines utilities manager."""

from typing import Any

import contourpy as cp
import matplotlib.colors as mcol
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

from pyPLUTO.h_pypluto import makelist
from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState
from pyPLUTO.toolfuncs.loadtools import LoadToolsManager
from pyPLUTO.utils.inspector import track_kwargs


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

    def _check_var(
        self, var: str | NDArray, transpose: bool = False
    ) -> np.ndarray:
        """Return a variable from input array or dataset key."""
        return self.LoadToolsManager.check_var(var, transpose)

    @staticmethod
    def _vector_field(
        t: float,
        y: np.ndarray,
        var1: np.ndarray,
        var2: np.ndarray,
        xc: np.ndarray,
        yc: np.ndarray,
    ) -> list[np.ndarray]:
        """Compute vector field interpolation at position y."""
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
        **kwargs: Any,
    ) -> list:
        """Find field lines from two vector components."""
        varx = self._check_var(var1, kwargs.get("transpose", False))
        vary = self._check_var(var2, kwargs.get("transpose", False))

        xc = x1 if x1 is not None else self.x1
        yc = x2 if x2 is not None else self.x2

        if x0 is None or y0 is None:
            raise ValueError(
                "Footpoints not provided. Please provide footpoints!"
            )

        x0 = makelist(x0)
        y0 = makelist(y0)

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
                "step", min((xend - xbeg) / self.nx1, (yend - ybeg) / self.nx2)
            )
        )

        maxstep = kwargs.get("maxstep", 100 * step)
        numstep = int(kwargs.get("numsteps", 16384))
        tfin = maxstep * numstep

        def system(t, y):
            """Evaluate the ODE right-hand side by interpolating the vector field."""
            return self._vector_field(t, y, varx, vary, xc, yc)

        def outside_domain(t, y):
            """Return 0 (terminal) when the integrator leaves the domain."""
            if y[0] < xbeg or y[0] > xend or y[1] < ybeg or y[1] > yend:
                return 0
            return 1

        def close_to_start(t, y):
            """Return 0 (terminal) when the integrator returns near the seed point."""
            dist_0 = np.linalg.norm(y - np.asarray(self.init_pos))
            if dist_0 < ctol and t > maxstep:
                self.loop_dom = True
                return 0
            self.oldpos = y
            return 1

        def max_num_steps(t, y):
            """Return 0 (terminal) when the allowed step count is exceeded."""
            self.stepnum += 1
            if self.stepnum > numstep:
                return 0
            return 1

        close_to_start.terminal = (
            True if kwargs.get("close", True) is True else False
        )
        close_to_start.direction = 0

        outside_domain.terminal = True
        outside_domain.direction = 0

        max_num_steps.terminal = True
        max_num_steps.direction = 0

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
                print("Line with footpoint at x = ", xp, " and y = ", yp)
                print("Final integration time forward:  ", sol_forward.t[-1])
                print("Final integration time backward: ", sol_backward.t[-1])
                print("Final step number forward:       ", forw_steps)
                print("Final step number backward:      ", self.stepnum)

            if len(x_line) > 1:
                lines_list.append([x_line, y_line])

        for method_name in ["init_pos", "stepnum", "out_dom", "oldpos"]:
            if method_name in self.__class__.__dict__:
                delattr(self.__class__, method_name)

        return lines_list

    @track_kwargs
    def find_contour(self, var: str | np.ndarray, **kwargs: Any) -> list:
        """Generate contour lines for a given variable."""
        var = self._check_var(var, kwargs.get("transpose", False)).T

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

        if "cmap" in kwargs:
            cmap_val = kwargs.get("cmap")
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
                x_c = line[:, 0]
                y_c = line[:, 1]
                col = (
                    cmap(indx / (len(levels) - 1)) if "cmap" in kwargs else "k"
                )

                if len(line) > 1:
                    lines_list.append([x_c, y_c, col])

        return lines_list
