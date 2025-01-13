import pyPLUTO    as pp
import pytest

print(f"Testing the LoadPart format finding ... ".ljust(50), end='')

# Format not given finding dbl
D = pp.LoadPart(path = "Test_load/particles_cr", text = False)
assert D.format == "dbl"

# Format not given (single file), finding vtk
D = pp.LoadPart(path = "Test_load/particles_cr/vtk", text = False)
assert D.format == "vtk"

# Given format (single file)
for format in ["dbl","flt","vtk"]:
    D = pp.LoadPart(path = "Test_load/particles_cr", text = False, datatype = format)
    assert D.format == format

# Check if raises error if the format is wrong
with pytest.raises(ValueError):
    D = pp.LoadPart(path = "Test_load/particles_cr", text = False, datatype = "wrong")

# Check if raises an error if there is no good format
with pytest.raises(FileNotFoundError):
    D = pp.LoadPart(text = False)

# Check if raises error if the selected format does not exist
with pytest.raises(FileNotFoundError):
    D = pp.LoadPart(path = "Test_load/particles_cr/vtk", text = False, datatype = "dbl")

print(" ---> \033[32mPASSED!\033[0m")
