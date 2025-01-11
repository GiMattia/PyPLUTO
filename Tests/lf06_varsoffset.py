import pyPLUTO as pp
import numpy as np
import numpy.testing as npt
import pytest

print(f"Testing the Load offset finding method ... ".ljust(50), end='')

size = 128*128
size_vtk0 = 1271
size_vtkm = 1282
size_dh50 = 3680
size_vtkh = 40
varslist = ["rho","vx1","vx2","vx3","prs"]

# Test single file, dbl output
D = pp.Load(path = "Test_load/single_file", text = False)
for num, var in enumerate(varslist):
    assert D._offset[var] == size*num*8

# Test multiple files, dbl output
D = pp.Load(path = "Test_load/multiple_files", text = False)
assert D._offset["prs"] == 0

# Test single file, vtk output (+ descriptor files)
D = pp.Load(path = "Test_load/single_file", datatype = 'vtk', text = False)
for num, var in enumerate(varslist):
    assert D._offset[var] == size_vtk0 + num*(size_vtkh + size*4)

# Test single file, vtk output (standalone)
D = pp.Load(path = "Test_load/single_file", datatype = 'vtk', text = False, alone = True)
for num, var in enumerate(varslist):
    assert D._offset[var] == size_vtk0 + num*(size_vtkh + size*4)

# Test single file, vtk output (+ descriptor files)
D = pp.Load(path = "Test_load/multiple_files", datatype = 'vtk', text = False)
assert D._offset['prs'] == size_vtkm

# Test single file, vtk output (standalone)
D = pp.Load(path = "Test_load/multiple_files", datatype = 'vtk', text = False, alone = True)
var = list(D._offset.keys())[0]
assert D._offset[var] == size_vtkm

# Test dbl.h5 output
D = pp.Load(path = "Test_load/single_file", datatype = 'dbl.h5', text = False)
for num, var in enumerate(varslist):
    assert D._offset[var] == size_dh50 + num*(size*8) + (0 if num == 0 else 2048)

print(" ---> \033[32mPASSED!\033[0m")
