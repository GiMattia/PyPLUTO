"""Functions to link Load data with astropy units."""

from typing import TYPE_CHECKING, Union

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    import astropy.units as u


def add_units(
    self,
    var: Union[str, NDArray],
    unit: Union[str, "u.UnitBase", "u.FunctionUnitBase"],
) -> "u.Quantity":
    """Link a variable with an astropy unit, returning a Quantity.

    Returns
    -------
    - quantity: astropy.units.Quantity
        The variable with the associated astropy unit.

    Parameters
    ----------
    - unit (not optional): str | astropy.units.UnitBase
        The astropy unit to associate with the variable. Can be either
        a string (e.g. ``'g/cm**3'``) or an astropy unit object
        (e.g. ``astropy.units.g / astropy.units.cm**3``).
    - var (not optional): str | NDArray
        The variable to link with the unit. Can be either a string
        corresponding to a ``Load`` attribute (e.g. ``'rho'``) or a
        numpy array.

    ----

    Examples
    --------
    - Example #1: Link the density with CGS units using a string name

        >>> rho_cgs = D.add_units('rho', 'g/cm**3')

    - Example #2: Link the velocity with CGS units using a numpy array

        >>> import astropy.units as u
        >>> vx1_cgs = D.add_units(D.vx1, u.cm / u.s)

    - Example #3: Link the pressure with CGS units using a unit string

        >>> prs_cgs = D.add_units('prs', 'dyn/cm**2')

    """
    try:
        import astropy.units as au
    except ImportError as exc:
        raise ImportError(
            "astropy is required for add_units. "
            "Install it with: pip install astropy"
        ) from exc

    # Resolve variable: if string, retrieve from self
    if isinstance(var, str):
        arr: NDArray = getattr(self, var)
    else:
        arr = np.asarray(var)

    # Resolve unit: if string, parse it
    if isinstance(unit, str):
        parsed_unit = au.Unit(unit)
    else:
        parsed_unit = unit

    return arr * parsed_unit
