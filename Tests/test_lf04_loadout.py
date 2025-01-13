import pyPLUTO as pp
import numpy as np
import numpy.testing as npt
import pytest
def test_load_descriptor_reading_method():
    print(f"Testing the Load descriptor reading method ... ".ljust(50), end='')

    outlist = np.linspace(0,4,5,dtype = 'int')
    timelist = np.linspace(0,0.2, 5)

    # Test the dbl.out file when only last output is loaded
    D = pp.Load(path = "Test_load/multiple_outputs", text = False)

    typefile = ["single_file"]
    endianess = ["<"]
    binformat = ['<f8']
    varslist = ["rho","vx1","vx2","vx3","prs"]
    endpath = [".0004.dbl"]

    npt.assert_array_equal(D.outlist, outlist)
    npt.assert_allclose(D.timelist, timelist, atol = 0.001) # Higher tolerance due to how the PLUTO ouput is generated
    assert D.nout == 4
    assert D.ntime == 0.2
    assert D._d_info["typefile"] == typefile
    assert D._d_info["endianess"] == endianess
    assert D._d_info["binformat"] == binformat
    assert D._d_info["endpath"] == endpath
    npt.assert_array_equal(D._d_info["varslist"], [varslist])

    # Test the dbl.out file when two outputs are loaded
    D = pp.Load([0, 'last'], path = "Test_load/multiple_outputs", text = False, endian = "little")

    endpath = [".0000.dbl",".0004.dbl"]

    npt.assert_array_equal(D.outlist, outlist)
    npt.assert_allclose(D.timelist, timelist, atol = 0.001) # Higher tolerance due to how the PLUTO ouput is generated
    npt.assert_array_equal(D.nout, [0,4])
    npt.assert_allclose(D.ntime, [0,0.2])
    npt.assert_array_equal(D._d_info["typefile"], typefile*2)
    npt.assert_array_equal(D._d_info["endianess"], endianess*2)
    npt.assert_array_equal(D._d_info["binformat"], binformat*2)
    npt.assert_array_equal(D._d_info["endpath"], endpath)
    npt.assert_array_equal(D._d_info["varslist"], [varslist,varslist])

    # Test the vtk.out file when only last output is loaded
    D = pp.Load(path = "Test_load/multiple_outputs", text = False, datatype = "vtk")

    endianess = [">"]
    binformat = ['>f4']
    endpath = [".0004.vtk"]

    npt.assert_array_equal(D.outlist, outlist)
    npt.assert_allclose(D.timelist, timelist, atol = 0.001) # Higher tolerance due to how the PLUTO ouput is generated
    assert D.nout == 4
    assert D.ntime == 0.2
    assert D._d_info["typefile"] == typefile
    assert D._d_info["endianess"] == endianess
    assert D._d_info["binformat"] == binformat
    assert D._d_info["endpath"] == endpath
    npt.assert_array_equal(D._d_info["varslist"], [varslist])

    # Test the vtk.out file when only last output is loaded
    D = pp.Load(path = "Test_load/multiple_outputs", text = False, datatype = "tab")

    endianess = ["<"]
    binformat = ['<f4']
    endpath = [".0004.tab"]

    npt.assert_array_equal(D.outlist, outlist)
    npt.assert_allclose(D.timelist, timelist, atol = 0.001) # Higher tolerance due to how the PLUTO ouput is generated
    assert D.nout == 4
    assert D.ntime == 0.2
    assert D._d_info["typefile"] == typefile
    assert D._d_info["endianess"] == endianess
    assert D._d_info["binformat"] == binformat
    assert D._d_info["endpath"] == endpath
    npt.assert_array_equal(D._d_info["varslist"], [varslist])

    print(" ---> \033[32mPASSED!\033[0m")
