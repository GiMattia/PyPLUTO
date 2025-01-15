import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcol
import matplotlib.lines as mlines
import matplotlib.widgets as mwdg
import matplotlib.cm as cm
import matplotlib.animation as animation
import numpy as np
import numpy.ma as ma
import contourpy as cp
import pandas as pd

import glob
import os
import sys
import mmap
import tempfile
import struct
import shutil
import warnings
import traceback
import gc

from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.collections import PathCollection, QuadMesh
from matplotlib.widgets import Slider
from matplotlib import rc
from scipy.integrate import solve_ivp
from scipy.interpolate import RectBivariateSpline
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import map_coordinates
from pathlib import Path
from numpy.typing import NDArray
from matplotlib.figure import Figure, SubFigure
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection
from collections.abc import Callable, Mapping
from typing import Any
from itertools import islice

try:
    import h5py as h5py
except ImportError:
    pass

from .h_pypluto import makelist, check_par, color_warning, color_error
from .h_pypluto import find_session

# Append created methods to __all__
# __all__ = [name for name in globals()]
