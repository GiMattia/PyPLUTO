import pyPLUTO as pp
import numpy as np
import numpy.testing as npt
import pytest

print(f"Testing the Load data loading method ... ".ljust(50), end='')

# Compute exact solution
nx1, nx2 = 128, 128
exact_vars = {}

exact_vals = { "rho": [0.138, 0.5323, 0.5323, 1.5],
               "vx1": [1.206, 1.206,  0.0,    0.0],
               "vx2": [1.206, 0.0,    1.206,  0.0],
               "vx3": [0.0,   0.0,    0.0,    0.0],
               "prs": [0.029, 0.3,    0.3,    1.5]}

slices = [ (slice(0, nx1//2+1), slice(0, nx2//2+1)),
           (slice(0, nx1//2+1), slice(nx2//2, nx2)),
           (slice(nx1//2, nx1), slice(0, nx2//2+1)),
           (slice(nx1//2, nx1), slice(nx2//2, nx2))]

for i, var  in enumerate(["rho", "vx1", "vx2", "vx3", "prs"]):
    array = np.zeros((nx1, nx2))
    for j, sl in enumerate(slices):
        array[sl] = exact_vals[var][j]
    exact_vars[var] = array

varslist = ["rho","vx1","vx2","vx3","prs"]


# Test single file, dbl output
D = pp.Load(0,path = "Test_load/single_file", text = False)
for num, var in enumerate(varslist):
    npt.assert_array_equal(getattr(D,var), exact_vars[var])

# Test multiple files, dbl output
D = pp.Load(0,path = "Test_load/multiple_files", text = False)
for num, var in enumerate(varslist):
    npt.assert_array_equal(getattr(D,var), exact_vars[var])

# Test single file, vtk output
D = pp.Load(0,path = "Test_load/single_file", datatype = "vtk", text = False)
for num, var in enumerate(varslist):
    npt.assert_allclose(getattr(D,var), exact_vars[var])

# Test multiple files, vtk output
D = pp.Load(0,path = "Test_load/multiple_files", datatype = "vtk", text = False)
for num, var in enumerate(varslist):
    npt.assert_allclose(getattr(D,var), exact_vars[var])

# Test dbl.h5 output
D = pp.Load(0,path = "Test_load/single_file", datatype = "dbl.h5", text = False)
for num, var in enumerate(varslist):
    npt.assert_array_equal(getattr(D,var), exact_vars[var])

# Test dbl.h5 output
D = pp.Load(0,path = "Test_load/single_file", datatype = "flt.h5", text = False)
for num, var in enumerate(varslist):
    npt.assert_allclose(getattr(D,var), exact_vars[var])


# Test single file, tab output
D = pp.Load(0,path = "Test_load/single_file", datatype = "tab", text = False)
for num, var in enumerate(varslist):
    npt.assert_allclose(getattr(D,var), exact_vars[var])

# Test single file, vtk output (standalone)
D = pp.Load(0,path = "Test_load/single_file", datatype = "vtk", text = False, alone = True)
for num, var in enumerate(varslist):
    npt.assert_allclose(getattr(D,var), exact_vars[var])

# Test multiple files, vtk output (standalone)
D = pp.Load(0,path = "Test_load/multiple_files", datatype = "vtk", text = False, alone = True)
for num, var in enumerate(varslist):
    npt.assert_allclose(getattr(D,var), exact_vars[var])

# Test dbl.h5 output (standalone)
warn = ("The geometry is unknown, therefore the grid spacing has not been "
        "computed. \nFor a more accurate grid analysis, the loading with "
        "the .out file is recommended.\n")

with pytest.warns(UserWarning, match=warn):
    D = pp.Load(path = "Test_load/single_file", text = False, datatype = "dbl.h5", alone = True)
for num, var in enumerate(varslist):
    npt.assert_array_equal(getattr(D,var), exact_vars[var])

# Test flt.h5 output (standalone)
with pytest.warns(UserWarning, match=warn):
    D = pp.Load(path = "Test_load/single_file", text = False, datatype = "flt.h5", alone = True)
for num, var in enumerate(varslist):
    npt.assert_allclose(getattr(D,var), exact_vars[var])

# Test single file, tab output (standalone)
vars_conversion = {"rho": "var0",
                   "vx1": "var1",
                   "vx2": "var2",
                   "vx3": "var3",
                   "prs": "var4"}

D = pp.Load(0,path = "Test_load/single_file", datatype = "tab", text = False, alone = True)
for num, var in enumerate(varslist):
    npt.assert_allclose(getattr(D,vars_conversion[var]), exact_vars[var])

# Test single file, tab output (1D)
rho = np.array([1]*200 + [0.125]*200)
prs = np.array([1]*200 + [0.1]*200)

D = pp.Load(0,path = "Test_load/multiple_outputs", datatype = "tab", text = False)
npt.assert_allclose(D.rho, rho)
npt.assert_allclose(D.prs, prs)

# Test muptiple outputs
D = pp.Load([0,1],path = "Test_load/multiple_outputs", datatype = "dbl", text = False)
assert(isinstance(D.rho, dict))
assert(list(D.rho.keys()) == [0,1])
npt.assert_allclose(D.rho[0], rho)

print(" ---> \033[32mPASSED!\033[0m")
