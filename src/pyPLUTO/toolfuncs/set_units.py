"""Attach and detach astropy units on loaded variables."""

from collections.abc import Iterable

from pyPLUTO.baseloadstate import BaseLoadState
from pyPLUTO.loadmixin import BaseLoadMixin

__all__ = ["SetUnitsManager"]


_TIME_VARS: tuple[str, ...] = ("ntime", "timelist")


class SetUnitsManager(BaseLoadMixin):
    """Attach and detach astropy units on variables stored in state."""

    def __init__(self, state: BaseLoadState) -> None:
        self.state = state

    def _resolve_unit_vars(
        self,
        var: str | Iterable[str] | bool | None = None,
        skip_units: str | Iterable[str] | None = None,
    ) -> tuple[list[str], bool]:
        """Resolve variable selection for unit attach/detach operations."""

        def _to_list(value: str | Iterable[str] | bool | None) -> list[str]:
            if value is None or value is True:
                return []
            if isinstance(value, str):
                return [value]
            if isinstance(value, Iterable):
                return [str(v) for v in value]
            raise TypeError(
                "var must be None, True, a string, or an iterable of strings."
            )

        explicit = not (var is None or var is True)
        selected = (
            _to_list(var)
            if explicit
            else [
                name
                for name in (*self.state.d_vars, *_TIME_VARS)
                if name in self.state.units and hasattr(self.state, name)
            ]
        )

        if skip_units is None:
            excluded: set[str] = set()
        elif isinstance(skip_units, str):
            excluded = {skip_units}
        elif isinstance(skip_units, Iterable):
            excluded = {str(v) for v in skip_units}
        else:
            raise TypeError(
                "skip_units must be None, a string, or an iterable of strings."
            )

        ordered = [name for name in selected if name not in excluded]
        return ordered, explicit

    def to_astropy_units(
        self,
        var: str | Iterable[str] | bool | None = None,
        skip_units: str | Iterable[str] | None = None,
    ) -> None:
        """Attach astropy units to selected variables in place."""
        selected, explicit = self._resolve_unit_vars(
            var=var, skip_units=skip_units
        )

        for name in selected:
            if not hasattr(self.state, name):
                if explicit:
                    raise KeyError(f"No known unit for variable '{name}'")
                continue
            if name not in self.state.units:
                if explicit:
                    raise KeyError(f"No known unit for variable '{name}'")
                continue
            if name in self.state.unit_attached:
                continue
            setattr(
                self.state,
                name,
                getattr(self.state, name) * self.state.units[name],
            )
            self.state.unit_attached.add(name)

    def to_code_units(
        self,
        var: str | Iterable[str] | bool | None = None,
        skip_units: str | Iterable[str] | None = None,
    ) -> None:
        """Convert selected astropy Quantity variables back to code units."""
        selected, explicit = self._resolve_unit_vars(
            var=var, skip_units=skip_units
        )
        if not explicit:
            selected = [
                name for name in selected if name in self.state.unit_attached
            ]

        for name in selected:
            if name not in self.state.units:
                if explicit:
                    raise KeyError(f"No known unit for variable '{name}'")
                continue
            if not hasattr(self.state, name):
                continue
            arr = getattr(self.state, name)
            if hasattr(arr, "unit") and hasattr(arr, "value"):
                arr_code = (arr / self.state.units[name]).decompose().value
                setattr(self.state, name, arr_code)
                self.state.unit_attached.discard(name)
