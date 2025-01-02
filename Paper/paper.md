---
title: 'PyPLUTO: A Python Package for Loading and Plotting Data from the PLUTO Code'
tags:
  - Python
  - MHD
  - Numerical Simulations
  - Astrophysical Plamas
  - PLUTO Code

authors:
  - name: Giancarlo Mattia
    orcid: 0000-0000-0000-0000
    equal-contrib: true
    affiliation: 1

affiliations:
 - name: Max Planck ...
   index: 1

date: 03 January 2025
bibliography: paper.bib

---

# Summary

In recent years, numerical simulations have become indispensable for addressing complex astrophysical problems. The so-called MagnetoHydroDynamics (MHD) framework represents a key tool for investigating the dynamical evolution of astrophysical plasmas, which are described as a set of partial differential equations [@Chiuderi_Velli_2015] that enforce the conservation of mass, momentum, and energy, along with Maxwell’s equation for the evolution of the electromagnetic fields. Due to the high nonlinearity of the MHD equations (regardless of their specifications, e.g., classical/relativistic or ideal/resistive), a general analytical solution is precluded, making the numerical approach crucial. Numerical simulations usually end up producing large sets of data files and their scientific analysis leans on dedicated software designed for data visualization [@ViSit;@ParaView]. However, in order to encompass all of the code output features, specialized tools focusing on the numerical code may represent a more versatile and built-in tool. Here, we present PyPLUTO, a Python package tailored for efficient loading, manipulation, and visualization of outputs produced with the PLUTO[^1] code [@PLUTO_2007;@PLUTO_2012]. PyPLUTO uses memory mapping to optimize data loading and provides general routines for data manipulation and visualization. PyPLUTO also supports the particle modules of the PLUTO code, enabling users to load and visualize particles (such as cosmic rays [@Mignone2018], Lagrangian [@Vaidya2018], or dust [@MIGNONE2019] particles) from hybrid simulations. A dedicated Graphical User Interface (GUI) simplifies the generation of single-subplot figures, making PyPLUTO a powerful yet user-friendly toolkit for astrophysical data analysis.

[^1]: [https://plutocode.ph.unito.it]

# Statement of Need

The PLUTO code [@PLUTO_2007] is a widely used, freely distributed computational fluid dynamics code designed to solve the classical and (special) relativistic MHD equations in different geometries and spatial dimensions. The original code is written in C (while the upcoming GPU version provides a full C++ rewrite[^2]) and it contains several numerical methods adaptable to different contexts. Data post-processing is a crucial step in analyzing the results of any numerical simulation. PyPLUTO offers user-friendly methods to generate publication-quality plots with a high degree of customization. Despite its enhanced flexibility, PyPLUTO offers strong computational efficiency, enabling the rapid handling of large datasets typical of state-of-the-art numerical simulations. Through this balance between customization, performance, and ease of use, PyPLUTO represents a key tool to effectively communicate scientific results while minimizing the effort required for post-processing.

[^2]: [https://plutocode.ph.unito.it/pluto-gpu.html]

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
