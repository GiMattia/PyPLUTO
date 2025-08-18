import matplotlib.pyplot as plt
import numpy as np

import pyPLUTO as pp

I = pp.Image(figsize=[11.7, 5])
I.create_axes(
    ncol=4,
    wratio=[1, 0.1, 1, 0.1],
    wspace=[0.01, 0.15, 0.01],
    left=0.07,
    right=0.93,
    bottom=0.15,
)


D = pp.Load(path="../Examples/Test_Problems/HD/Disk_Planet")

I.display(
    0.594 * D.rho,
    x1=5.2 * D.x1rc,
    x2=5.2 * D.x2rc,
    cscale="log",
    title="Test 06 - HD Disk-planet test",
    aspect="equal",
    ax=0,
    # vmin=0.1,
    xtitle=r"$x\;[\mathrm{au}]$",
    ytitle=r"$y\;[\mathrm{au}]$",
    xticks=[-10, -5, 0, 5, 10],
    yticks=[-10, -5, 0, 5, 10],
    xrange=[-13, 13],
    yrange=[-13, 13],
)

omega = 2.0 * np.pi / np.sqrt(D.x1)

I.zoom(
    xrange=[5.2 * 0.9, 5.2 * 1.1],
    yrange=[-5.2 * 0.1, 5.2 * 0.1],
    ax=0,
    aspect="equal",
    pos=[0.74, 0.95, 0.7, 0.9],
)

I.zoom(
    var=4.743 * (D.vx2 - omega[:, np.newaxis]),
    xrange=[5.2 * 0.9, 5.2 * 1.1],
    yrange=[-5.2 * 0.1, 5.2 * 0.1],
    pos=[0.07, 0.27, 0.17, 0.4],
    cpos="bottom",
    cmap="RdBu",
    cscale="linear",
    vmin=-5.5,
    vmax=5.5,
    ax=0,
    aspect="equal",
    titlesize=13,
    title=r"$v_\phi - \Omega R\;[\mathrm{km}/\mathrm{s}]$",
)

I.colorbar(cax=1, axs=0, clabel=r"$\rho\;[\mathrm{g}/\mathrm{m}^3]$")
plt.gcf().gca().xaxis.set_tick_params(labelsize=13)

D = pp.Load(path="../Examples/Test_Problems/Particles/CR/Xpoint")
Dp_i = pp.LoadPart(
    0, path="../Examples/Test_Problems/Particles/CR/Xpoint", datatype="vtk"
)
Dp_f = pp.LoadPart(
    path="../Examples/Test_Problems/Particles/CR/Xpoint", datatype="vtk"
)


def compute_gamma(dp):
    return np.sqrt(1 + dp.vx1**2 + dp.vx2**2 + dp.vx3**2)


gl_final = compute_gamma(Dp_f)
indx_final = np.argsort(gl_final)

# --- Plot contour of Ax3 ---
I.contour(
    D.Ax3,
    x1=D.x1 / 1000,
    x2=D.x2 / 1000,
    levels=20,
    ax=2,
    aspect="equal",
    c="silver",
)

# --- Plot particle positions ---
pcm = I.scatter(
    Dp_f.x1[indx_final] / 1000,
    Dp_f.x2[indx_final] / 1000,
    vmin=0,
    vmax=40,
    c=gl_final[indx_final],
    cmap=plt.get_cmap("YlOrRd", 8),
    ms=10,
    ax=2,
    title="Test 11 - Particles CR X-point test",
    xrange=[-3.5, 3.5],
    yrange=[-3.5, 3.5],
    xticks=[-3, -2, -1, 0, 1, 2, 3],
    yticks=[-3, -2, -1, 0, 1, 2, 3],
    xtitle=r"$x\;[10^3\mathrm{v_A}/\mathrm{\Omega_L}]$",
    ytitle=r"$y\;[10^3\mathrm{v_A}/\mathrm{\Omega_L}]$",
)

I.colorbar(cax=3, pcm=pcm, clabel=r"$\Gamma$")

I.create_axes(left=0.65, right=0.8, bottom=0.25, top=0.43)

for Dp, label in [(Dp_i, "t = 0"), (Dp_f, "t = 100")]:
    gl = compute_gamma(Dp)
    hist, bins = Dp.spectrum(gl, density=False)

    I.plot(
        bins,
        hist,
        ax=6,
        xscale="log",
        yscale="log",
        xrange=[1, 50],
        yrange=[1, 1.0e8],
        label=label,
        fontsize=13,
        xtitle=r"$\Gamma$",
        ytitle=r"$dN/d\Gamma$",
    )

I.legend(ax=6, legpos=0, legsize=10, legalpha=0.25)
I.ax[6].patch.set_alpha(0.75)


I.savefig("pyplutotests.png")
