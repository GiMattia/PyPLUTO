import time

import numpy as np
import numpy.testing as npt

import pyPLUTO as pp


def ideal_solution(D, h5lone):

    if h5lone:
        X, Y = D.x1, D.x2
        print(X)
        Yx = 0.5 * (D.x2r[:, 1:] + D.x2r[:, :-1])
        Xy = 0.5 * (D.x1r[1:,] + D.x1r[:-1,])
    else:
        X, Y = np.meshgrid(D.x1, D.x2, indexing="ij")
        _, Yx = np.meshgrid(D.x1r, D.x2, indexing="ij")
        Xy, _ = np.meshgrid(D.x1, D.x2r, indexing="ij")

    x1r = np.linspace(0, 6.28318530717959, 9)
    x2r = np.linspace(0, 6.28318530717959, 11)
    x1 = 0.5 * (x1r[:-1] + x1r[1:])
    x2 = 0.5 * (x2r[:-1] + x2r[1:])

    x, y = np.meshgrid(x1, x2, indexing="ij")
    _, yx = np.meshgrid(x1r, x2, indexing="ij")
    xy, _ = np.meshgrid(x1, x2r, indexing="ij")
    npt.assert_allclose(X, x)
    npt.assert_allclose(Y, y)
    npt.assert_allclose(Yx, yx)
    npt.assert_allclose(Xy, xy)

    ex = {}
    ex["rho"] = 25.0 / 9.0
    ex["vx1"] = -np.sin(Y)
    ex["vx2"] = np.sin(X)
    ex["vx3"] = 0.0
    ex["Bx1"] = -np.sin(Y)
    ex["Bx2"] = np.sin(2.0 * X)
    ex["Bx3"] = 0.0
    ex["Ax3"] = np.cos(Y) + 0.5 * np.cos(2.0 * X)
    ex["prs"] = 5.0 / 3.0
    ex["Bx1s"] = -np.sin(Yx)
    ex["Bx2s"] = np.sin(2.0 * Xy)
    ex["v2"] = ex["vx1"] ** 2 + ex["vx2"] ** 2 + ex["vx3"] ** 2
    return ex


def load_and_check(dtype, path):
    D = pp.Newload(datatype=dtype, path=path, text=False)
    h5lone = bool(D.format in {"dbl.h5", "flt.h5"} and D.alone)
    ex = ideal_solution(D, h5lone)
    for var in D.d_info["varslist"][D.nout]:
        npt.assert_allclose(
            getattr(D.state, var), ex[var], rtol=1e-5, atol=1e-5
        )
    return D


def bench(dtype, path, number=20):
    t0 = time.perf_counter()
    for _ in range(number):
        D = load_and_check(dtype, path)
    t1 = time.perf_counter()
    return (t1 - t0) / number


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

NUMBER = 1

for label, path, dtypes in groups:
    for dtype in dtypes:
        print(f"{label:20s}  {dtype:7s}  ")
        avg = bench(dtype, path, number=NUMBER)
        print(f"{avg:.6e} s/run")
