import time

import numpy as np
import numpy.testing as npt

import pyPLUTO as pp


def ideal_solution(D, h5lone):

    if h5lone:
        X, Y, Z = D.x1, D.x2, D.x3
        Yx = 0.25 * (
            D.x2r[:, 1:, 1:]
            + D.x2r[:, :-1, :-1]
            + D.x2r[:, 1:, :-1]
            + D.x2r[:, :-1, 1:]
        )
        Zx = 0.25 * (
            D.x3r[:, 1:, 1:]
            + D.x3r[:, :-1, :-1]
            + D.x3r[:, 1:, :-1]
            + D.x3r[:, :-1, 1:]
        )

        Xy = 0.25 * (
            D.x1r[1:, :, 1:]
            + D.x1r[:-1, :, :-1]
            + D.x1r[1:, :, :-1]
            + D.x1r[:-1, :, 1:]
        )

        Zy = 0.25 * (
            D.x3r[1:, :, 1:]
            + D.x3r[:-1, :, :-1]
            + D.x3r[1:, :, :-1]
            + D.x3r[:-1, :, 1:]
        )

        Xz = 0.25 * (
            D.x1r[1:, 1:, :]
            + D.x1r[:-1, :-1, :]
            + D.x1r[1:, :-1, :]
            + D.x1r[:-1, 1:, :]
        )

        Yz = 0.25 * (
            D.x2r[1:, 1:, :]
            + D.x2r[:-1, :-1, :]
            + D.x2r[1:, :-1, :]
            + D.x2r[:-1, 1:, :]
        )

    else:
        X, Y, Z = np.meshgrid(D.x1, D.x2, D.x3, indexing="ij")
        _, Yx, Zx = np.meshgrid(D.x1r, D.x2, D.x3, indexing="ij")
        Xy, _, Zy = np.meshgrid(D.x1, D.x2r, D.x3, indexing="ij")
        Xz, Yz, _ = np.meshgrid(D.x1, D.x2, D.x3r, indexing="ij")

    x1r = np.linspace(0, 6.28318530717959, 9)
    x2r = np.linspace(0, 6.28318530717959, 11)
    x3r = np.linspace(0, 6.28318530717959, 13)
    x1 = 0.5 * (x1r[:-1] + x1r[1:])
    x2 = 0.5 * (x2r[:-1] + x2r[1:])
    x3 = 0.5 * (x3r[:-1] + x3r[1:])

    x, y, z = np.meshgrid(x1, x2, x3, indexing="ij")
    _, yx, zx = np.meshgrid(x1r, x2, x3, indexing="ij")
    xy, _, zy = np.meshgrid(x1, x2r, x3, indexing="ij")
    xz, yz, _ = np.meshgrid(x1, x2, x3r, indexing="ij")
    npt.assert_allclose(X, x)
    npt.assert_allclose(Y, y)
    npt.assert_allclose(Z, z)
    npt.assert_allclose(Yx, yx)
    npt.assert_allclose(Xy, xy)
    npt.assert_allclose(Zx, zx)
    npt.assert_allclose(Zy, zy)
    npt.assert_allclose(Yz, yz)
    npt.assert_allclose(Xz, xz)

    c0 = 0.8

    ex = {}
    ex["rho"] = 25.0 / 9.0
    ex["vx1"] = 0.0
    ex["vx2"] = -np.sin(Z)
    ex["vx3"] = np.sin(Y)
    ex["Bx1"] = c0 * (np.sin(Y) + np.sin(Z))
    ex["Bx2"] = c0 * (-2.0 * np.sin(2.0 * Z) + np.sin(X))
    ex["Bx3"] = c0 * (np.sin(X) + np.sin(Y))
    ex["prs"] = 5.0 / 3.0
    ex["Bx1s"] = c0 * (np.sin(Yx) + np.sin(Zx))
    ex["Bx2s"] = c0 * (-2.0 * np.sin(2.0 * Zy) + np.sin(Xy))
    ex["Bx3s"] = c0 * (np.sin(Xz) + np.sin(Yz))
    ex["v2"] = ex["vx1"] ** 2 + ex["vx2"] ** 2 + ex["vx3"] ** 2
    return ex


def load_and_check(dtype, path):
    D = pp.Newload(datatype=dtype, path=path, text=False)
    h5lone = bool(D.datatype in {"dbl.h5", "flt.h5"} and D.alone)
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
        ["dbl", "flt", "vtk", "dbl.h5", "flt.h5"],
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
