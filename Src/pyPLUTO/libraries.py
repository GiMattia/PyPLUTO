import numpy              as np
import numpy.ma           as ma
import matplotlib         as mpl
import matplotlib.pyplot  as plt
import matplotlib.colors  as mcol
import matplotlib.lines   as mlines
import matplotlib.widgets as mwdg
import matplotlib.cm      as cm
import pandas             as pd

import glob
import os
import sys
import tempfile
import struct
import shutil
import warnings

try:
    import h5py           as h5py
except ImportError:
    pass

from mpl_toolkits.axes_grid1               import make_axes_locatable
from matplotlib.widgets                    import Slider
from matplotlib                            import rc
from pathlib                               import Path
from numpy.typing                          import NDArray
from matplotlib.figure                     import Figure, SubFigure
from matplotlib.axes                       import Axes
from typing                                import Callable, Mapping, Any, Type
from itertools                             import islice

#from mpl_toolkits.axes_grid1.inset_locator import InsetPosition
#from scipy.interpolate                     import RectBivariateSpline
#from matplotlib                            import gridspec

warnings.simplefilter('always', DeprecationWarning)
    
from .h_pypluto import makelist, _check_par