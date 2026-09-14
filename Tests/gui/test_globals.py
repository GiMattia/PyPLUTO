"""Test of the gui/globals.py file."""

from matplotlib import colormaps as cmaps

from pyPLUTO.gui import globals as gl


# The axis scales offered by the GUI are real matplotlib scales
def test_scales_are_valid():
    import matplotlib.scale as mscale

    for scale in gl.scales:
        assert scale in mscale.get_scale_names()


# The color scales are the ones accepted by the plotting routines
def test_vscales():
    assert gl.vscales == [
        "linear",
        "log",
        "symlog",
        "2slope",
        "power",
        "asinh",
    ]


# Every offered colormap exists in matplotlib
def test_colormaps_exist():
    for cmap in gl.cmaps_avail:
        assert cmap in list(cmaps)


# The colormaps are grouped by family, and 'All' holds the full list
def test_colormaps_divided():
    assert "All" in gl.cmaps_divided
    assert gl.cmaps_divided["All"] == gl.cmaps_avail


# Every colormap of every group is a known colormap
def test_colormap_groups_are_valid():
    for group, names in gl.cmaps_divided.items():
        for name in names:
            assert name in list(cmaps), f"{name} in group {group}"


# The file formats offered by the GUI are the ones pyPLUTO can read
def test_formats():
    assert gl.format_avail[0] == "None"
    for datatype in ["dbl", "flt", "vtk", "dbl.h5", "flt.h5", "tab"]:
        assert datatype in gl.format_avail
