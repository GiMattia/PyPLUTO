"""Pytest configuration for the CodSpeed benchmarks."""

import os

# Enforce a non-GUI backend so benchmarks do not depend on a display.
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib

matplotlib.use("Agg")
