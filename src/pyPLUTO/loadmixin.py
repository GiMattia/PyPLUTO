"""Mixin class for load fluid handling."""

from __future__ import annotations

import numpy as np

from pyPLUTO.baseloadmixin import BaseLoadMixin
from pyPLUTO.loadstate import LoadState


class LoadMixin(BaseLoadMixin[LoadState]):
    """Mixin class for load fluid handling.

    It provides properties and methods related to loading fluid data.
    """

    state: LoadState

    @property
    def defh(self) -> dict:
        """Get the defh attribute of the load state."""
        return self.state.defh

    @defh.setter
    def defh(self, value: dict) -> None:
        """Set the defh attribute of the load state."""
        self.state.defh = value

    @property
    def level(self) -> int:
        """Get the AMR refinement level."""
        return self.state.level

    @level.setter
    def level(self, value: int) -> None:
        """Set the AMR refinement level."""
        self.state.level = value

    @property
    def dx1(self) -> np.ndarray:
        """Get the dx1 attribute of the load state."""
        return self.state.dx1

    @dx1.setter
    def dx1(self, value: np.ndarray) -> None:
        """Set the dx1 attribute of the load state."""
        self.state.dx1 = value

    @property
    def dx2(self) -> np.ndarray:
        """Get the dx2 attribute of the load state."""
        return self.state.dx2

    @dx2.setter
    def dx2(self, value: np.ndarray) -> None:
        """Set the dx2 attribute of the load state."""
        self.state.dx2 = value

    @property
    def dx3(self) -> np.ndarray:
        """Get the dx3 attribute of the load state."""
        return self.state.dx3

    @dx3.setter
    def dx3(self, value: np.ndarray) -> None:
        """Set the dx3 attribute of the load state."""
        self.state.dx3 = value

    @property
    def full3D(self) -> bool:
        """Get the full3D attribute of the load state."""
        return self.state.full3D

    @full3D.setter
    def full3D(self, value: bool) -> None:
        """Set the full3D attribute of the load state."""
        self.state.full3D = value

    @property
    def geom(self) -> str:
        """Get the geom attribute of the load state."""
        return self.state.geom

    @geom.setter
    def geom(self, value: str) -> None:
        """Set the geom attribute of the load state."""
        self.state.geom = value

    @property
    def gridsize(self) -> int:
        """Get the gridsize attribute of the load state."""
        return self.state.gridsize

    @gridsize.setter
    def gridsize(self, value: int) -> None:
        """Set the gridsize attribute of the load state."""
        self.state.gridsize = value

    @property
    def gridsize_st1(self) -> int:
        """Get the gridsize_st1 attribute of the load state."""
        return self.state.gridsize_st1

    @gridsize_st1.setter
    def gridsize_st1(self, value: int) -> None:
        """Set the gridsize_st1 attribute of the load state."""
        self.state.gridsize_st1 = value

    @property
    def gridsize_st2(self) -> int:
        """Get the gridsize_st2 attribute of the load state."""
        return self.state.gridsize_st2

    @gridsize_st2.setter
    def gridsize_st2(self, value: int) -> None:
        """Set the gridsize_st2 attribute of the load state."""
        self.state.gridsize_st2 = value

    @property
    def gridsize_st3(self) -> int:
        """Get the gridsize_st3 attribute of the load state."""
        return self.state.gridsize_st3

    @gridsize_st3.setter
    def gridsize_st3(self, value: int) -> None:
        """Set the gridsize_st3 attribute of the load state."""
        self.state.gridsize_st3 = value

    @property
    def nshp_st1(self) -> int | tuple[int, ...] | None:
        """Get the nshp_st1 attribute of the load state."""
        return self.state.nshp_st1

    @nshp_st1.setter
    def nshp_st1(self, value: int | tuple[int, ...] | None) -> None:
        """Set the nshp_st1 attribute of the load state."""
        self.state.nshp_st1 = value

    @property
    def nshp_st2(self) -> tuple[int, ...] | None:
        """Get the nshp_st2 attribute of the load state."""
        return self.state.nshp_st2

    @nshp_st2.setter
    def nshp_st2(self, value: tuple[int, ...] | None) -> None:
        """Set the nshp_st2 attribute of the load state."""
        self.state.nshp_st2 = value

    @property
    def nshp_st3(self) -> tuple[int, ...] | None:
        """Get the nshp_st3 attribute of the load state."""
        return self.state.nshp_st3

    @nshp_st3.setter
    def nshp_st3(self, value: tuple[int, ...] | None) -> None:
        """Set the nshp_st3 attribute of the load state."""
        self.state.nshp_st3 = value

    @property
    def nx1(self) -> int:
        """Get the nx1 attribute of the load state."""
        return self.state.nx1

    @nx1.setter
    def nx1(self, value: int) -> None:
        """Set the nx1 attribute of the load state."""
        self.state.nx1 = value

    @property
    def nx2(self) -> int:
        """Get the nx2 attribute of the load state."""
        return self.state.nx2

    @nx2.setter
    def nx2(self, value: int) -> None:
        """Set the nx2 attribute of the load state."""
        self.state.nx2 = value

    @property
    def nx3(self) -> int:
        """Get the nx3 attribute of the load state."""
        return self.state.nx3

    @nx3.setter
    def nx3(self, value: int) -> None:
        """Set the nx3 attribute of the load state."""
        self.state.nx3 = value

    @property
    def plini(self) -> dict:
        """Get the plini attribute of the load state."""
        return self.state.plini

    @plini.setter
    def plini(self, value: dict) -> None:
        """Set the plini attribute of the load state."""
        self.state.plini = value

    @property
    def x1(self) -> np.ndarray:
        """Get the x1 attribute of the load state."""
        return self.state.x1

    @x1.setter
    def x1(self, value: np.ndarray) -> None:
        """Set the x1 attribute of the load state."""
        self.state.x1 = value

    @property
    def x1c(self) -> np.ndarray:
        """Get the x1c attribute of the load state."""
        return self.state.x1c

    @x1c.setter
    def x1c(self, value: np.ndarray) -> None:
        """Set the x1c attribute of the load state."""
        self.state.x1c = value

    @property
    def x1p(self) -> np.ndarray:
        """Get the x1p attribute of the load state."""
        return self.state.x1p

    @x1p.setter
    def x1p(self, value: np.ndarray) -> None:
        """Set the x1p attribute of the load state."""
        self.state.x1p = value

    @property
    def x1r(self) -> np.ndarray:
        """Get the x1r attribute of the load state."""
        return self.state.x1r

    @x1r.setter
    def x1r(self, value: np.ndarray) -> None:
        """Set the x1r attribute of the load state."""
        self.state.x1r = value

    @property
    def x1rc(self) -> np.ndarray:
        """Get the x1rc attribute of the load state."""
        return self.state.x1rc

    @x1rc.setter
    def x1rc(self, value: np.ndarray) -> None:
        """Set the x1rc attribute of the load state."""
        self.state.x1rc = value

    @property
    def x1rp(self) -> np.ndarray:
        """Get the x1rp attribute of the load state."""
        return self.state.x1rp

    @x1rp.setter
    def x1rp(self, value: np.ndarray) -> None:
        """Set the x1rp attribute of the load state."""
        self.state.x1rp = value

    @property
    def x1rt(self) -> np.ndarray:
        """Get the x1rt attribute of the load state."""
        return self.state.x1rt

    @x1rt.setter
    def x1rt(self, value: np.ndarray) -> None:
        """Set the x1rt attribute of the load state."""
        self.state.x1rt = value

    @property
    def x1t(self) -> np.ndarray:
        """Get the x1t attribute of the load state."""
        return self.state.x1t

    @x1t.setter
    def x1t(self, value: np.ndarray) -> None:
        """Set the x1t attribute of the load state."""
        self.state.x1t = value

    @property
    def x2(self) -> np.ndarray:
        """Get the x2 attribute of the load state."""
        return self.state.x2

    @x2.setter
    def x2(self, value: np.ndarray) -> None:
        """Set the x2 attribute of the load state."""
        self.state.x2 = value

    @property
    def x2c(self) -> np.ndarray:
        """Get the x2c attribute of the load state."""
        return self.state.x2c

    @x2c.setter
    def x2c(self, value: np.ndarray) -> None:
        """Set the x2c attribute of the load state."""
        self.state.x2c = value

    @property
    def x2p(self) -> np.ndarray:
        """Get the x2p attribute of the load state."""
        return self.state.x2p

    @x2p.setter
    def x2p(self, value: np.ndarray) -> None:
        """Set the x2p attribute of the load state."""
        self.state.x2p = value

    @property
    def x2r(self) -> np.ndarray:
        """Get the x2r attribute of the load state."""
        return self.state.x2r

    @x2r.setter
    def x2r(self, value: np.ndarray) -> None:
        """Set the x2r attribute of the load state."""
        self.state.x2r = value

    @property
    def x2rc(self) -> np.ndarray:
        """Get the x2rc attribute of the load state."""
        return self.state.x2rc

    @x2rc.setter
    def x2rc(self, value: np.ndarray) -> None:
        """Set the x2rc attribute of the load state."""
        self.state.x2rc = value

    @property
    def x2rp(self) -> np.ndarray:
        """Get the x2rp attribute of the load state."""
        return self.state.x2rp

    @x2rp.setter
    def x2rp(self, value: np.ndarray) -> None:
        """Set the x2rp attribute of the load state."""
        self.state.x2rp = value

    @property
    def x3(self) -> np.ndarray:
        """Get the x3 attribute of the load state."""
        return self.state.x3

    @x3.setter
    def x3(self, value: np.ndarray) -> None:
        """Set the x3 attribute of the load state."""
        self.state.x3 = value

    @property
    def x3c(self) -> np.ndarray:
        """Get the x3c attribute of the load state."""
        return self.state.x3c

    @x3c.setter
    def x3c(self, value: np.ndarray) -> None:
        """Set the x3c attribute of the load state."""
        self.state.x3c = value

    @property
    def x3r(self) -> np.ndarray:
        """Get the x3r attribute of the load state."""
        return self.state.x3r

    @x3r.setter
    def x3r(self, value: np.ndarray) -> None:
        """Set the x3r attribute of the load state."""
        self.state.x3r = value

    @property
    def x3rc(self) -> np.ndarray:
        """Get the x3rc attribute of the load state."""
        return self.state.x3rc

    @x3rc.setter
    def x3rc(self, value: np.ndarray) -> None:
        """Set the x3rc attribute of the load state."""
        self.state.x3rc = value

    @property
    def x3rt(self) -> np.ndarray:
        """Get the x3rt attribute of the load state."""
        return self.state.x3rt

    @x3rt.setter
    def x3rt(self, value: np.ndarray) -> None:
        """Set the x3rt attribute of the load state."""
        self.state.x3rt = value

    @property
    def x3t(self) -> np.ndarray:
        """Get the x3t attribute of the load state."""
        return self.state.x3t

    @x3t.setter
    def x3t(self, value: np.ndarray) -> None:
        """Set the x3t attribute of the load state."""
        self.state.x3t = value

    @property
    def alpha(self) -> np.ndarray:
        """Get the alpha attribute of the load state."""
        return self.state.alpha

    @alpha.setter
    def alpha(self, value: np.ndarray) -> None:
        """Set the alpha attribute of the load state."""
        self.state.alpha = value

    @property
    def shift1(self) -> np.ndarray:
        """Get the shift1 attribute of the load state."""
        return self.state.shift1

    @shift1.setter
    def shift1(self, value: np.ndarray) -> None:
        """Set the shift1 attribute of the load state."""
        self.state.shift1 = value

    @property
    def shift2(self) -> np.ndarray:
        """Get the shift2 attribute of the load state."""
        return self.state.shift2

    @shift2.setter
    def shift2(self, value: np.ndarray) -> None:
        """Set the shift2 attribute of the load state."""
        self.state.shift2 = value

    @property
    def shift3(self) -> np.ndarray:
        """Get the shift3 attribute of the load state."""
        return self.state.shift3

    @shift3.setter
    def shift3(self, value: np.ndarray) -> None:
        """Set the shift3 attribute of the load state."""
        self.state.shift3 = value

    @property
    def gcov11(self) -> np.ndarray:
        """Get the gcov11 attribute of the load state."""
        return self.state.gcov11

    @gcov11.setter
    def gcov11(self, value: np.ndarray) -> None:
        """Set the gcov11 attribute of the load state."""
        self.state.gcov11 = value

    @property
    def gcov22(self) -> np.ndarray:
        """Get the gcov22 attribute of the load state."""
        return self.state.gcov22

    @gcov22.setter
    def gcov11(self, value: np.ndarray) -> None:
        """Set the gcov22 attribute of the load state."""
        self.state.gcov22 = value

    @property
    def gcov33(self) -> np.ndarray:
        """Get the gcov33 attribute of the load state."""
        return self.state.gcov33

    @gcov33.setter
    def gcov33(self, value: np.ndarray) -> None:
        """Set the gcov33 attribute of the load state."""
        self.state.gcov33 = value

    @property
    def gcov12(self) -> np.ndarray:
        """Get the gcov12 attribute of the load state."""
        return self.state.gcov12

    @gcov12.setter
    def gcov12(self, value: np.ndarray) -> None:
        """Set the gcov12 attribute of the load state."""
        self.state.gcov12 = value

    @property
    def gcov13(self) -> np.ndarray:
        """Get the gcov13 attribute of the load state."""
        return self.state.gcov13

    @gcov13.setter
    def gcov13(self, value: np.ndarray) -> None:
        """Set the gcov13 attribute of the load state."""
        self.state.gcov13 = value

    @property
    def gcov23(self) -> np.ndarray:
        """Get the gcov23 attribute of the load state."""
        return self.state.gcov23

    @gcov23.setter
    def gcov23(self, value: np.ndarray) -> None:
        """Set the gcov23 attribute of the load state."""
        self.state.gcov23 = value
