import pyPLUTO    as pp
import pytest

print(f"Testing the Load format finding ... ".ljust(50), end='')

# Format not given (single file), finding dbl
D = pp.Load(path = "Test_load/single_file", text = False)
assert D.format == "dbl"

# Format not given (single file), finding vtk
D = pp.Load(path = "Test_load/single_file/vtk", text = False)
assert D.format == "vtk"

# Given format (single file), alone = False
for format in ["dbl","flt","vtk","dbl.h5","flt.h5"]:
    D = pp.Load(path = "Test_load/single_file", text = False, datatype = format)
    assert D.format == format

# Given format (single file), alone = True
D = pp.Load(path = "Test_load/single_file", text = False, datatype = 'vtk', alone = True)
assert D.format == 'vtk'

# dbl.h5 and flt.h5 should raise a warning
warn = ("The geometry is unknown, therefore the grid spacing has not been "
        "computed. \nFor a more accurate grid analysis, the loading with "
        "the .out file is recommended.\n")
for format in ["dbl.h5","flt.h5"]:
    with pytest.warns(UserWarning, match=warn):
        D = pp.Load(path = "Test_load/single_file", text = False, datatype = format, alone = True)
        assert D.format == format

# Format not given (multiple files), finding dbl
D = pp.Load(path = "Test_load/multiple_files", text = False)
assert D.format == "dbl"

# Format not given (multiple files), finding vtk
D = pp.Load(path = "Test_load/multiple_files/vtk", text = False)
assert D.format == "vtk"

# Given format (multiple files), alone = False
for format in ["dbl","flt","vtk"]:
    D = pp.Load(path = "Test_load/multiple_files", text = False, datatype = format)
    assert D.format == format

# Given format (multiple files), alone = True
D = pp.Load(path = "Test_load/multiple_files", text = False, datatype = 'vtk', alone = True)
assert D.format == 'vtk'

# Check if raises error if the format is wrong
with pytest.raises(ValueError):
    D = pp.Load(path = "Test_load/single_file", text = False, datatype = "wrong")

# Check if raises an error if there is no good format
with pytest.raises(FileNotFoundError):
    D = pp.Load(text = False)

# Check if raises error if the selected format does not exist
with pytest.raises(FileNotFoundError):
    D = pp.Load(path = "Test_load/multiple_files", text = False, datatype = "dbl.h5")

print(" ---> \033[32mPASSED!\033[0m")
