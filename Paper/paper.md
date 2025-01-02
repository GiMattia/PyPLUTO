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

# Main Features

PyPLUTO is a package written in Python (version ≥ 3.10) with the additions of NumPy [@NUMPY2020], Matplotlib [@MATPLOTLIB_2007], SciPy [@SCIPY_2020], pandas [@PANDAS2020], h5py [@H5PY_2013] and PyQT6 [PYQT] (although the last two are optional). The package, which can be installed through pip, is made of mainly 3 classes:
• The `Load` class loads and manipulates the PLUTO output files containing fluid-related quantities.
• The `LoadPart` class loads and manipulates the PLUTO output files containing particle-related quantities.
• The `Image` class produces and handles the graphical windows and the plotting procedures.
Additionally, a separate `PyPLUTOApp` class launches a GUI able to load and plot 1D and 2D data in a single set of axes. PyPLUTO has been implemented to be supported by Windows, MacOS, and Linux, through both standard scripts and more interactive tools (e.g., IPython or Jupyter). The style guidelines follow the PEP8[^3] conventions for Python codes and focus on clarity and code readability.

[^3]: [https://peps.python.org/pep-0008/]

### Loading the Data

The variety of data formats obtainable from the PLUTO code, combined with the high level of output customization, has strongly hindered the development of packages that can consistently load every possible simulation outcome. The PLUTO code provides a variety of output data formats, including raw-binary and h5 (in both double and single precision), VTK, and simple ASCII files (the last ones only for  single-processor 1D and 2D data) for the fluid variables. Some of these formats are also used for particle data files. Additionally, the code also generates descriptor files (*‘.out’*) which contain relevant information regarding the grid structure and fluid variables.

## Acknowledgments
G. Mattia thanks L. Del Zanna for the valuable discussions on data visualization. The authors thank Simeon Doetsch for their insights on memory mapping techniques and Deniss Stepanovs and Antoine Strugarek for their contribution throughout the years to previous PyPLUTO versions. This project has received funding from the European Union’s Horizon Europe research and innovation programme under the Marie Skłodowska-Curie grant agreement No 101064953 (GR-PLUTO).

# References