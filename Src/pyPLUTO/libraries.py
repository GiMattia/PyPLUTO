import gc
import glob
import mmap
import re
import os
import shutil
import struct
import sys
import tempfile
import traceback
import warnings
from collections.abc import Callable, Mapping
from itertools import islice
from pathlib import Path
from typing import Any

import contourpy as cp
import matplotlib as mpl
import matplotlib.animation as animation
import matplotlib.cm as cm
import matplotlib.colors as mcol
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import matplotlib.widgets as mwdg
import numpy as np
import numpy.ma as ma
import pandas as pd
from matplotlib import rc
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection, PathCollection, QuadMesh
from matplotlib.figure import Figure, SubFigure
from matplotlib.widgets import Slider
from mpl_toolkits.axes_grid1 import make_axes_locatable
from numpy.typing import NDArray
from scipy.integrate import solve_ivp
from scipy.interpolate import RectBivariateSpline, RegularGridInterpolator
from scipy.ndimage import map_coordinates

try:
    import h5py as h5py
except ImportError:
    pass

from .h_pypluto import check_par, color_error, color_warning, find_session, makelist

# Append created methods to __all__
# __all__ = [name for name in globals()]
