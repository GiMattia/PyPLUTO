import pyPLUTO as pp
import numpy as np
import numpy.testing as npt
import pytest

print(f"Testing the LoadPart offset finding method ... ".ljust(50), end='')

varslist = ['points', 'Identity', 'tinj', 'Color', 'Four-Velocity']
offsets_vtk = {'points': 104,
               'Identity': 65719,
               'tinj': 82146,
               'Color': 98574,
               'Four-Velocity': 114989}

# Test CR particles, dbl output
D = pp.LoadPart(path = "Test_load/particles_cr", text = False)
assert D._offset["tot"] == 390

# Test CR particles, flt output
D = pp.LoadPart(path = "Test_load/particles_cr", text = False, datatype = "flt")
assert D._offset["tot"] == 379

# Test CR particles, vtk output
D = pp.LoadPart(path = "Test_load/particles_cr", text = False, datatype = "vtk")
for var in varslist:
    assert D._offset[var] == offsets_vtk[var]

print(" ---> \033[32mPASSED!\033[0m")
