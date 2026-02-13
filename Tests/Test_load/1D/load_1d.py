import numpy as np
import numpy.testing as npt

import pyPLUTO as pp


def ideal_solution(D, time=None):
    ex = {}
    ntime = D.ntime if time is None else time
    ex["rho"] = 1.0 + 0.5 * np.sin(2 * np.pi * D.x1 + ntime)
    ex["vx1"] = np.sin(2 * np.pi * D.x1 + ntime)
    ex["vx2"] = np.cos(2 * np.pi * D.x1 + ntime)
    ex["vx3"] = np.atan(10.0 * (D.x1 - 0.5) / (1.0 + 3.0 * ntime))
    ex["prs"] = 1.0 + 0.5 * np.cos(2 * np.pi * D.x1 + ntime)
    ex["v2"] = ex["vx1"] ** 2 + ex["vx2"] ** 2 + ex["vx3"] ** 2
    ex["cs"] = np.sqrt(ex["prs"] / ex["rho"])
    return ex


cases = ((), (0,), (1,), (2,), (3,), ("last",), (-1,))

for i, case in enumerate(cases):
    for type in ["dbl", "flt", "vtk", "dbl.h5", "flt.h5"]:
        print("Descriptor single case ", case, type)
        D = pp.Newload(*case, datatype=type, path="single_file/descriptor")
        ex = ideal_solution(D)
        for var in D.d_info["varslist"][D.nout]:
            num = getattr(D, var)
            npt.assert_allclose(num, ex[var], rtol=1.0e-5, atol=1.0e-5)
    for type in ["dbl", "flt", "vtk"]:
        print("Descriptor multiple case ", case, type)
        D = pp.Newload(*case, datatype=type, path="multiple_files/descriptor")
        ex = ideal_solution(D)
        for var in D.d_info["varslist"][D.nout]:
            num = getattr(D, var)
            npt.assert_allclose(num, ex[var], rtol=1.0e-5, atol=1.0e-5)
