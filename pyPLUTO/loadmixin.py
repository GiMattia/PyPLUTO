"""Mixin class for load fluid handling."""

from typing import Any

from numpy.typing import NDArray

from .baseloadmixin import BaseLoadMixin
from .loadstate import LoadState


class LoadMixin(BaseLoadMixin):
    """Mixin class for load fluid handling.

    It provides properties and methods related to loading fluid data.
    """

    # pylint: disable=too-many-public-methods

    state: LoadState

    @property
    def dim(self) -> int:
        """Get the dim attribute of the load state."""
        return self.state.dim

    @dim.setter
    def dim(self, value: int) -> None:
        """Set the dim attribute of the load state."""
        self.state.dim = value

    @property
    def dx1(self) -> NDArray[Any]:
        """Get the dx1 attribute of the load state."""
        return self.state.dx1

    @dx1.setter
    def dx1(self, value: NDArray[Any]) -> None:
        """Set the dx1 attribute of the load state."""
        self.state.dx1 = value

    @property
    def dx2(self) -> NDArray[Any]:
        """Get the dx2 attribute of the load state."""
        return self.state.dx2

    @dx2.setter
    def dx2(self, value: NDArray[Any]) -> None:
        """Set the dx2 attribute of the load state."""
        self.state.dx2 = value

    @property
    def dx3(self) -> NDArray[Any]:
        """Get the dx3 attribute of the load state."""
        return self.state.dx3

    @dx3.setter
    def dx3(self, value: NDArray[Any]) -> None:
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
    def nshp(self) -> int | tuple[int, ...]:
        """Get the nshp attribute of the load state."""
        return self.state.nshp

    @nshp.setter
    def nshp(self, value: int | tuple[int, ...]) -> None:
        """Set the nshp attribute of the load state."""
        self.state.nshp = value

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
    def x1(self) -> NDArray[Any]:
        """Get the x1 attribute of the load state."""
        return self.state.x1

    @x1.setter
    def x1(self, value: NDArray[Any]) -> None:
        """Set the x1 attribute of the load state."""
        self.state.x1 = value

    @property
    def x1c(self) -> NDArray[Any]:
        """Get the x1c attribute of the load state."""
        return self.state.x1c

    @x1c.setter
    def x1c(self, value: NDArray[Any]) -> None:
        """Set the x1c attribute of the load state."""
        self.state.x1c = value

    @property
    def x1p(self) -> NDArray[Any]:
        """Get the x1p attribute of the load state."""
        return self.state.x1p

    @x1p.setter
    def x1p(self, value: NDArray[Any]) -> None:
        """Set the x1p attribute of the load state."""
        self.state.x1p = value

    @property
    def x1r(self) -> NDArray[Any]:
        """Get the x1r attribute of the load state."""
        return self.state.x1r

    @x1r.setter
    def x1r(self, value: NDArray[Any]) -> None:
        """Set the x1r attribute of the load state."""
        self.state.x1r = value

    @property
    def x1rc(self) -> NDArray[Any]:
        """Get the x1rc attribute of the load state."""
        return self.state.x1rc

    @x1rc.setter
    def x1rc(self, value: NDArray[Any]) -> None:
        """Set the x1rc cattribute of the load state."""
        self.state.x1rc = value

    @property
    def x1rp(self) -> NDArray[Any]:
        """Get the x1rp attribute of the load state."""
        return self.state.x1rp

    @x1rp.setter
    def x1rp(self, value: NDArray[Any]) -> None:
        """Set the x1rp attribute of the load state."""
        self.state.x1rp = value

    @property
    def x1rt(self) -> NDArray[Any]:
        """Get the x1rt attribute of the load state."""
        return self.state.x1rt

    @x1rt.setter
    def x1rt(self, value: NDArray[Any]) -> None:
        """Set the x1rt attribute of the load state."""
        self.state.x1rt = value

    @property
    def x1t(self) -> NDArray[Any]:
        """Get the x1t attribute of the load state."""
        return self.state.x1t

    @x1t.setter
    def x1t(self, value: NDArray[Any]) -> None:
        """Set the x1t attribute of the load state."""
        self.state.x1t = value

    @property
    def x2(self) -> NDArray[Any]:
        """Get the x2 attribute of the load state."""
        return self.state.x2

    @x2.setter
    def x2(self, value: NDArray[Any]) -> None:
        """Set the x2 attribute of the load state."""
        self.state.x2 = value

    @property
    def x2c(self) -> NDArray[Any]:
        """Get the x2c attribute of the load state."""
        return self.state.x2c

    @x2c.setter
    def x2c(self, value: NDArray[Any]) -> None:
        """Set the x2c attribute of the load state."""
        self.state.x2c = value

    @property
    def x2p(self) -> NDArray[Any]:
        """Get the x2p attribute of the load state."""
        return self.state.x2p

    @x2p.setter
    def x2p(self, value: NDArray[Any]) -> None:
        """Set the x2p attribute of the load state."""
        self.state.x2p = value

    @property
    def x2r(self) -> NDArray[Any]:
        """Get the x2r attribute of the load state."""
        return self.state.x2r

    @x2r.setter
    def x2r(self, value: NDArray[Any]) -> None:
        """Set the x2r attribute of the load state."""
        self.state.x2r = value

    @property
    def x2rc(self) -> NDArray[Any]:
        """Get the x2rc attribute of the load state."""
        return self.state.x2rc

    @x2rc.setter
    def x2rc(self, value: NDArray[Any]) -> None:
        """Set the x2rc attribute of the load state."""
        self.state.x2rc = value

    @property
    def x2rp(self) -> NDArray[Any]:
        """Get the x2rp attribute of the load state."""
        return self.state.x2rp

    @x2rp.setter
    def x2rp(self, value: NDArray[Any]) -> None:
        """Set the x2rp attribute of the load state."""
        self.state.x2rp = value

    @property
    def x3(self) -> NDArray[Any]:
        """Get the x3 attribute of the load state."""
        return self.state.x3

    @x3.setter
    def x3(self, value: NDArray[Any]) -> None:
        """Set the x3 attribute of the load state."""
        self.state.x3 = value

    @property
    def x3c(self) -> NDArray[Any]:
        """Get the x3c attribute of the load state."""
        return self.state.x3c

    @x3c.setter
    def x3c(self, value: NDArray[Any]) -> None:
        """Set the x3c attribute of the load state."""
        self.state.x3c = value

    @property
    def x3r(self) -> NDArray[Any]:
        """Get the x3r attribute of the load state."""
        return self.state.x3r

    @x3r.setter
    def x3r(self, value: NDArray[Any]) -> None:
        """Set the x3r attribute of the load state."""
        self.state.x3r = value

    @property
    def x3rc(self) -> NDArray[Any]:
        """Get the x3rc attribute of the load state."""
        return self.state.x3rc

    @x3rc.setter
    def x3rc(self, value: NDArray[Any]) -> None:
        """Set the x3rc attribute of the load state."""
        self.state.x3rc = value

    @property
    def x3rt(self) -> NDArray[Any]:
        """Get the x3rt attribute of the load state."""
        return self.state.x3rt

    @x3rt.setter
    def x3rt(self, value: NDArray[Any]) -> None:
        """Set the x3rt attribute of the load state."""
        self.state.x3rt = value

    @property
    def x3t(self) -> NDArray[Any]:
        """Get the x3t attribute of the load state."""
        return self.state.x3t

    @x3t.setter
    def x3t(self, value: NDArray[Any]) -> None:
        """Set the x3t attribute of the load state."""
        self.state.x3t = value
