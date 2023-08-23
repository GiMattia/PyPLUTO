import numpy              as np
import matplotlib         as mpl
import matplotlib.pyplot  as plt
import matplotlib.colors  as mcol
import matplotlib.lines   as mlines
import matplotlib.widgets as mwdg
import os                 as os
import sys                as sys
import tempfile           as tempfile

from mpl_toolkits.axes_grid1               import make_axes_locatable
from matplotlib.widgets                    import Slider
from matplotlib                            import rc
from pathlib                               import Path
from typing                                import List


#from mpl_toolkits.axes_grid1.inset_locator import InsetPosition
from scipy.interpolate                     import RectBivariateSpline
#from matplotlib                            import gridspec

if sys.version_info >= (3, 10):
    lintstr = str | List[str] | List[str | int]
    listr   = str | List[str]
else:
    from typing import Union
    lintstr = Union[str, List[str], List[Union[str, int]]]
    listr   = Union[str, List[str]]

from .h_pypluto import makelist