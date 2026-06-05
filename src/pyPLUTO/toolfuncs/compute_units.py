"""Compute normalization unit scales and build the variable→unit mapping."""

import math
import re
from pathlib import Path
from typing import Any

import astropy.units as u

from pyPLUTO.baseloadstate import BaseLoadState
from pyPLUTO.loadmixin import BaseLoadMixin


class UnitManager(BaseLoadMixin):
    """Resolve normalization scales and build the variable→astropy-unit map."""

    def __init__(self, state: BaseLoadState) -> None:
        """Initialize the unit manager with the given load state."""
        self.state = state

    def _units_from_log(self) -> dict[str, float]:
        """Read normalization scales from PLUTO log text headers.

        Takes the first number on each row (CGS value).
        """
        pathdir = Path(getattr(self.state, "pathdir", "."))
        candidates = [pathdir / "pluto.0.log"]
        candidates.extend(sorted(pathdir.glob("*.log")))

        field_map = {
            "Density": "UNIT_DENSITY",
            "Pressure": "UNIT_PRESSURE",
            "Velocity": "UNIT_VELOCITY",
            "Length": "UNIT_LENGTH",
            "Temperature": "UNIT_TEMPERATURE",
            "Time": "UNIT_TIME",
            "Mag Field": "UNIT_MAGFIELD",
        }
        parsed: dict[str, float] = {}
        num_re = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")
        section_re = re.compile(r"^\s*(?:>)?\s*Normalization\s+Units\s*:\s*$")
        row_re = re.compile(r"^\s*\[(?P<name>[^\]]+)\]\s*:\s*(?P<rest>.+)$")

        for filepath in candidates:
            if not filepath.exists() or not filepath.is_file():
                continue
            try:
                with filepath.open(encoding="utf-8", errors="ignore") as fh:
                    lines = [next(fh, "") for _ in range(200)]
            except OSError:
                continue

            in_section = False
            found_row = False
            for line in lines:
                if not in_section and section_re.match(line):
                    in_section = True
                    continue
                if not in_section:
                    continue

                match = row_re.match(line)
                if not match:
                    if line.strip() == "":
                        if not found_row:
                            continue
                        break
                    continue

                name = match.group("name").strip()
                if name not in field_map:
                    continue
                num_match = num_re.search(match.group("rest"))
                if num_match is None:
                    continue
                found_row = True
                parsed[field_map[name]] = float(num_match.group(0))

            if parsed:
                break

        return parsed

    def _units_from_userdef(self) -> dict[str, float]:
        """Read normalization scales from user-defined overrides.

        Accepts both plain floats and astropy Quantities (converted to CGS).
        """
        userdef = getattr(self.state, "unit_userdef", {}) or {}
        units: dict[str, float] = {}
        all_keys = (
            "UNIT_DENSITY",
            "UNIT_LENGTH",
            "UNIT_VELOCITY",
            "UNIT_PRESSURE",
            "UNIT_TIME",
            "UNIT_TEMPERATURE",
            "UNIT_MAGFIELD",
        )
        for key in all_keys:
            if key not in userdef:
                continue
            val = userdef[key]
            try:
                if isinstance(val, u.Quantity):
                    units[key] = float(val.cgs.value)
                    continue
            except ImportError:
                pass
            units[key] = float(val)
        return units

    def _units_from_defh(self) -> dict[str, float]:
        """Read unit scales stored directly in state.defh as UNIT_* keys."""
        defh = getattr(self.state, "defh", {}) or {}
        all_keys = (
            "UNIT_DENSITY",
            "UNIT_LENGTH",
            "UNIT_VELOCITY",
            "UNIT_PRESSURE",
            "UNIT_TIME",
            "UNIT_TEMPERATURE",
            "UNIT_MAGFIELD",
        )
        return {key: float(defh[key]) for key in all_keys if key in defh}

    def _physics_defaults(self, physics: str) -> dict[str, float]:
        """Return placeholder base scales for the given PHYSICS module."""
        _dispatch: dict[str, dict[str, float]] = {}
        _fallback: dict[str, float] = {
            "UNIT_DENSITY": 1.0,
            "UNIT_LENGTH": 1.0,
            "UNIT_VELOCITY": 1.0,
        }
        return _dispatch.get(physics, _fallback)

    def _classical_mhd_defaults(self) -> dict[str, float]:
        """Return placeholder base scales as last-resort fallback."""
        return {
            "UNIT_DENSITY": 1.0,
            "UNIT_LENGTH": 1.0,
            "UNIT_VELOCITY": 1.0,
        }

    def _derive_units_from_base(
        self, scales: dict[str, float]
    ) -> dict[str, float]:
        """Fill missing derived unit scales from the three base units.

        Only called when the log file did not already supply the derived units.
        UNIT_TEMPERATURE is not derived here (composite: T = T0 * prs/rho/mu).
        """
        rho0 = scales.get("UNIT_DENSITY", 1.0)
        l0 = scales.get("UNIT_LENGTH", 1.0)
        v0 = scales.get("UNIT_VELOCITY", 1.0)

        if "UNIT_TIME" not in scales:
            scales["UNIT_TIME"] = l0 / v0
        if "UNIT_PRESSURE" not in scales:
            scales["UNIT_PRESSURE"] = rho0 * v0**2
        if "UNIT_MAGFIELD" not in scales:
            scales["UNIT_MAGFIELD"] = math.sqrt(4.0 * math.pi * rho0) * v0

        return scales

    def _resolve_base_scales(self) -> dict[str, float]:
        """Build the full set of unit scales via the priority chain.

        Priority: user-defined → log → defh → physics module → classical MHD.
        Any units not supplied by higher-priority sources are derived from the
        three base scales (rho0, l0, v0).
        """
        user_units = self._units_from_userdef()
        log_units = self._units_from_log()
        defh_units = self._units_from_defh()

        physics = str(
            (getattr(self.state, "defh", {}) or {}).get("PHYSICS", "")
        ).strip()
        physics_units = self._physics_defaults(physics) if physics else {}

        resolved: dict[str, float] = {}
        for source in (user_units, log_units, defh_units, physics_units):
            for key, val in source.items():
                if key not in resolved:
                    resolved[key] = val

        for key, val in self._classical_mhd_defaults().items():
            if key not in resolved:
                resolved[key] = val

        return self._derive_units_from_base(resolved)

    def _make_units_dict(self) -> dict[str, Any]:
        """Build a mapping from variable names to pre-computed astropy units."""
        scales = self._resolve_base_scales()
        self.state.unit_base = dict(scales)

        rho0 = scales["UNIT_DENSITY"]
        l0 = scales["UNIT_LENGTH"]
        v0 = scales["UNIT_VELOCITY"]
        t0 = scales["UNIT_TIME"]
        prs0 = scales["UNIT_PRESSURE"]
        b0 = scales["UNIT_MAGFIELD"]

        velocity_unit = v0 * u.cm / u.s
        length_unit = l0 * u.cm
        bfield_unit = b0 * u.Gauss

        units: dict[str, Any] = {
            "rho": rho0 * u.g / u.cm**3,
            "prs": prs0 * u.dyne / u.cm**2,
            "vx1": velocity_unit,
            "vx2": velocity_unit,
            "vx3": velocity_unit,
            "vel1": velocity_unit,
            "vel2": velocity_unit,
            "vel3": velocity_unit,
            "Bx1": bfield_unit,
            "Bx2": bfield_unit,
            "Bx3": bfield_unit,
            "x1": length_unit,
            "x2": length_unit,
            "x3": length_unit,
            "dx1": length_unit,
            "dx2": length_unit,
            "dx3": length_unit,
            "ntime": t0 * u.s,
        }
        return units
