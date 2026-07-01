import marimo

__generated_with = "0.23.9"
app = marimo.App(width="medium")


@app.cell
def _():
    """Speed test for rastra."""
    import importlib
    import timeit

    import pyPLUTO as pp

    rastra = importlib.import_module("rastra")
    return pp, rastra, timeit


@app.cell
def _(pp, rastra, timeit):
    # Set the relative path to the data folder
    data_path = "../Examples/Test_Problems/RMHD/KH"

    # Load data
    Data = pp.Load(path=data_path)

    # Creating the image and the subplot axes (to have two secondary plots)
    Image = pp.Image(
        figsize=[10.5, 10],
        suptitle="Test 07 - RMHD Kelvin-Helmholtz instability test",
        nwin=7,
    )
    Image.create_axes(right=0.55)
    Image.create_axes(nrow=2, hspace=[0.003], left=0.67)

    # Plotting the data
    Image.display(
        Data.rho,
        x1=Data.x1,
        x2=Data.x2,
        title="Density",
        aspect="equal",
        ax=0,
        shading="gouraud",
        xtitle=r"$x$",
        ytitle=r"$y$",
        cpos="right",
    )

    try:
        t0 = timeit.default_timer()
        lines2 = rastra.find_fieldlines(
            Data,
            Data.Bx1,
            Data.Bx2,
            x1=Data.x1,
            x2=Data.x2,
            y0=[0.0, 0.1, -0.1, 0.25, -0.25],
            x0=[0.5, 0.5, 0.5, 0.5, 0.5],
            order="RK45",
            maxstep=0.001,
            numsteps=10000,
        )
        t_rastra = timeit.default_timer() - t0
        print(f"[test07] rastra find_fieldlines: {t_rastra:.6f} s")
    except ImportError:
        print("[test07] rastra not available.")

    # Find and plot the field lines
    t0 = timeit.default_timer()
    lines = Data.find_fieldlines(
        Data.Bx1,
        Data.Bx2,
        x1=Data.x1,
        x2=Data.x2,
        y0=[0.0, 0.1, -0.1, 0.25, -0.25],
        x0=[0.5, 0.5, 0.5, 0.5, 0.5],
        order="RK45",
        maxstep=0.001,
        numsteps=10000,
    )
    t_scipy = timeit.default_timer() - t0
    print(f"[test07] PyPLUTO    find_fieldlines: {t_scipy:.6f} s")

    for _, line in enumerate(lines):
        Image.plot(line[0], line[1], ax=0, c="k")

    # Open the kh.dat file and store the variables
    analysis = Data.read_file("kh.dat")

    # Add text in the axes
    Image.text(r"$\langle v_y^2\rangle$", ax=1, x=0.05)
    Image.text(r"$v_{y, MAX}^2$", ax=2, x=0.05)

    # Plot the velocity from the kh.dat file.
    Image.plot(
        analysis["time"],
        analysis["vy2"],
        ax=1,
        c="k",
        yscale="log",
        xtickslabels=None,
    )
    Image.plot(
        analysis["time"],
        analysis["maxvy"],
        ax=2,
        c="k",
        yscale="log",
        xtitle=r"$t$",
    )


if __name__ == "__main__":
    app.run()
