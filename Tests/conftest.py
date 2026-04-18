"""Pytest configuration for test stability across CI environments."""

import os

# Enforce a non-GUI backend so tests do not depend on system Tcl/Tk packages.
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib

matplotlib.use("Agg")
