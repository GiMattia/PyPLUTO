# PyPLUTO: A Python Package for Loading and Plotting Data from the PLUTO Code
## Summary
PyPLUTO is a Python library which loads and plots the data obtain from the
PLUTO code simulations. The aim of this package is to simplify some non-trivial
python routines in order to quickly recover effective plots that are suited for
scientific publications.

## Statement of Need
The PLUTO code is a widely used, open-source, computational fluid dynamics
code developed at the Torino Astronomical Observatory (Tofani et al. 1998)
and designed to solve the equations of hydrodynamics and magnetohydrodynamics
in a arbitrary number of dimensions. The code is written in C and provides
a great flexibility in terms of the numerical methods used to solve the
equations and the physics implemented.

The post-processing of the data is a crucial step in the analysis of the
results of any numerical simulation. The PLUTO code provides a Python
interface to load the data (Mignone et al. 2007) but it does not provide
any routine to plot the data. The aim of this package is to fill this gap
by providing a simple way to load and plot the data from the PLUTO code
simulations.

## Description
The package is written in Python and uses the `numpy` (Van der Walt et al.
2011) and `matplotlib` (Hunter 2007) libraries to load and plot the data.
The package is designed to be easy to use and provides a simple interface
to load the data and to plot the data in a variety of formats.

The package is composed of two main classes: `pluto.Plot` and `pluto.Load`.
The `pluto.Load` class is used to load the data from the PLUTO code
simulations and the `pluto.Plot` class is used to plot the data loaded
with the `pluto.Load` class.

The `pluto.Load` class provides methods to load the data from the PLUTO
code simulations in a variety of formats, including the binary format
used by the PLUTO code. The class also provides methods to extract the
physical quantities from the data loaded.

The `pluto.Plot` class provides methods to plot the data loaded with the
`pluto.Load` class. The class provides methods to plot the data in a
variety of formats, including 1D, 2D and 3D plots.

## Features
The package provides the following features:

*   Load the data from the PLUTO code simulations in a variety of formats
*   Extract the physical quantities from the data loaded
*   Plot the data loaded in a variety of formats

## Examples
The package comes with a variety of examples that show how to use the
package to load and plot the data from the PLUTO code simulations. The
examples are provided in the `examples` directory of the package.

## Acknowledgments
This project is supported by the European Research Council (ERC) under the
European Union's Horizon 2020 research and innovation programme (grant
agreement No 815559).

## References

Hunter J. D. (2007). Matplotlib: A 2D graphics environment. Computing in
Science & Engineering, 9(3), 90-95.

Mignone A., Bodo G., Massaglia S., Matsakos T., Tesileanu O., Zanni C.,
Ferrari A. (2007). PLUTO: A Code for Fl uid Dynamics in Astrophysical
Environments. The Astrophysical Journal Supplement Series, 170(1), 228-242.

Tofani G., Galeotti P., Bodo G., Massaglia S. (1998). PLUTO: A Code for
Fl uid Dynamics in Astrophysical Environments. In Astronomical Data
Analysis Software and Systems VII (Vol. 145, p. 282).

Van der Walt S., Colbert S. C., Varoquaux G. (2011). The NumPy array: a
structure for efficient numerical computation. Computing in Science &
Engineering, 13(2), 22-30.
