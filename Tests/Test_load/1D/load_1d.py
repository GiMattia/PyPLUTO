import time
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


def load_and_check(case, dtype, path):
    D = pp.Newload(*case, datatype=dtype, path=path, text=False)
    ex = ideal_solution(D)
    for var in D.d_info["varslist"][D.nout]:
        # print(f"Checking variable: {var}")
        npt.assert_allclose(
            getattr(D.state, var), ex[var], rtol=1e-5, atol=1e-5
        )
    return D


def bench(case, dtype, path, number=20):
    t0 = time.perf_counter()
    for _ in range(number):
        D = load_and_check(case, dtype, path)
    t1 = time.perf_counter()
    return (t1 - t0) / number


cases = ((), (1,), (2,), (3,), ("last",), (-1,))

groups = [
    (
        "Descriptor single",
        "single_file/descriptor",
        ["dbl", "flt", "vtk", "dbl.h5", "flt.h5", "tab"],
    ),
    ("Descriptor multiple", "multiple_files/descriptor", ["dbl", "flt", "vtk"]),
    ("Alone single", "single_file/alone", ["vtk", "dbl.h5", "flt.h5"]),
    ("Alone multiple", "multiple_files/alone", ["vtk"]),
]

NUMBER = 1000

for case in cases:
    print(f"\nCASE {case}")
    print("-" * 72)
    for label, path, dtypes in groups:
        for dtype in dtypes:
            print(f"{label:20s}  {dtype:7s}  ")
            avg = bench(case, dtype, path, number=NUMBER)
            print(f"{avg:.6e} s/run")
