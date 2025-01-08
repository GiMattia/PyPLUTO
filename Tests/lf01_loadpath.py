import pyPLUTO    as pp
import pytest

print(f"Testing the Load init and Path find ... ".ljust(50), end='')

# Check if raises erorr with wrong endianess
with pytest.raises(ValueError):
    D = pp.Load(path = "Test_load/single_file", text = False, endian = "wrong")

# Check if raises an error with wrong multiple keyword
with pytest.raises(TypeError, match = "Invalid data type. 'multiple' must be a boolean."):
    D = pp.Load(path = "Test_load/single_file", text = False, multiple = "wrong")

# Check if raises error when the path is not a non-empty string
with pytest.raises(TypeError, match = "Invalid data type. 'path' must be path or string"):
    D = pp.Load(path = 123, text = False)
with pytest.raises(ValueError, match = "'path' cannot be an empty string."):
    D = pp.Load(path = "", text = False)

# Check if raises an error if the path is not a directory
with pytest.raises(NotADirectoryError):
    D = pp.Load(path = "wrong", text = False)

print(" ---> \033[32mPASSED!\033[0m")
