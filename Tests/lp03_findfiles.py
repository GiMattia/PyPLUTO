import pyPLUTO as pp
import numpy as np
import numpy.testing as npt
import pytest

print(f"Testing the LoadPart file finding method ... ".ljust(50), end='')

# Test with particles CR
D = pp.LoadPart(path = "Test_load/particles_cr", datatype = 'vtk', text = False)

outlist = [0]
typefile = ["single_file"]
endianess = [">"]
binformat = ['>f4']
endpath = [".0000.vtk"]
varslist = ['points', 'Identity', 'tinj', 'Color', 'Four-Velocity']

npt.assert_array_equal(D.outlist, outlist)
assert D.nout == 0
assert D._d_info["typefile"] == typefile
assert D._d_info["endianess"] == endianess
assert D._d_info["endpath"] == endpath
npt.assert_array_equal(D._d_info["varslist"], [varslist])


print(" ---> \033[32mPASSED!\033[0m")
