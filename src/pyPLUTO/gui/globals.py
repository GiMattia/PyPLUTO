"""Contains global variables for the GUI."""

import matplotlib.scale as mscale
from matplotlib import colormaps as cmaps

scale = list(mscale.get_scale_names())
scales = [scale[i] for i in [3, 4, 6, 0]]
vscales = ["linear", "log", "symlog", "2slope", "power", "asinh"]

cmaps_list = list(cmaps)
cmaps_avail0 = [cmaps_list[2], *cmaps_list[0:2], *cmaps_list[3:83]]
cmaps_avail = [cmap for cmap in cmaps_avail0 if cmap in cmaps_list]

cmaps_divided = {
    "All": cmaps_avail,
    "Uniform": ["plasma", "viridis", "inferno", "magma", "cividis"],
    "Sequential": [
        "Greys",
        "Purples",
        "Blues",
        "Greens",
        "Oranges",
        "Reds",
        "YlOrBr",
        "YlOrRd",
        "OrRd",
        "PuRd",
        "RdPu",
        "BuPu",
        "GnBu",
        "PuBu",
        "YlGnBu",
        "PuBuGn",
        "BuGn",
        "YlGn",
    ],
    "Sequential (2)": [
        "binary",
        "gist_yarg",
        "gist_gray",
        "gray",
        "bone",
        "pink",
        "spring",
        "summer",
        "autumn",
        "winter",
        "cool",
        "Wistia",
        "hot",
        "afmhot",
        "gist_heat",
        "copper",
    ],
    "Diverging": [
        "PiYG",
        "PRGn",
        "BrBG",
        "PuOr",
        "RdGy",
        "RdBu",
        "RdYlBu",
        "RdYlGn",
        "Spectral",
        "coolwarm",
        "bwr",
        "seismic",
        "berlin",
        "managua",
        "vanimo",
    ],
    "Cyclic": ["twilight", "twilight_shifted", "hsv"],
    "Qualitative": [
        "Pastel1",
        "Pastel2",
        "Paired",
        "Accent",
        "Dark2",
        "Set1",
        "Set2",
        "Set3",
        "tab10",
        "tab20",
        "tab20b",
        "tab20c",
    ],
    "Miscellaneous": [
        "flag",
        "prism",
        "ocean",
        "gist_earth",
        "terrain",
        "gist_stern",
        "gnuplot",
        "gnuplot2",
        "CMRmap",
        "cubehelix",
        "brg",
        "gist_rainbow",
        "rainbow",
        "jet",
        "turbo",
        "nipy_spectral",
        "gist_ncar",
    ],
}

format_avail = ["None", "dbl", "flt", "vtk", "dbl.h5", "flt.h5", "hdf5", "tab"]
