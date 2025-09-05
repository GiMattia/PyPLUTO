---
title: 'PyPLUTO: a Data Analysis Python Package for the PLUTO Code'
tags:
  - Astronomy
  - Python
  - MagnetoHydroDynamics
  - Computational Astrophysics
  - Data Visualization

authors:
  - name: Giancarlo Mattia
    orcid: 0000-0003-1454-6226
    affiliation: 1, 2

  - name: Daniele Crocco
    orcid: 0009-0001-4284-9446
    affiliation: 3

  - name: David Melon Fuksman
    orcid: 0000-0002-1697-6433
    affiliation: 1

  - name: Matteo Bugli
    orcid: 0000-0002-7834-0422
    affiliation: 3, 4, 5,6

  - name: Vittoria Berta
    orcid: 0000-0001-6305-6931
    affiliation: 3

  - name: Eleonora Puzzoni
    orcid: 0009-0009-5314-348X
    affiliation: 7

  - name: Andrea Mignone
    orcid: 0000-0002-8352-6635
    affiliation: 3, 6

  - name: Bhargav Vaidya
    orcid: 0000-0001-5424-0059
    affiliation: 8

affiliations:
 - name: Max Planck Institut für Astronomie, Königstuhl 17, Heidelberg, 69117, Germany
   index: 1

 - name: INFN, Sezione di Firenze, Via G. Sansone 1, Sesto Fiorentino (FI), 50019, Italy
   index: 2

 - name: Dipartimento di Fisica, Università di Torino, Via P. Giuria 1, Torino, 10125, Italy
   index: 3

 - name: Institut d’Astrophysique de Paris, UMR 7095, CNRS & Sorbonne Université, 98bis boulevard Arago, 75014 Paris, France
   index: 4

 - name: Université Paris-Saclay, Université Paris Cité, CEA, CNRS, AIM, Gif-sur-Yvette, 91191, France
   index: 5

 - name: INFN, Sezione di Torino, Via P. Giuria 1, Torino, 10125, Italy
   index: 6

 - name: Observatoire de la Côte d’Azur, Laboratoire Lagrange, Bd de l’Observatoire, CS 34229, 06304 Nice cedex 4, France
   index: 7

 - name: Department of Astronomy, Astrophysics and Space Engineering, Indian Institute of Technology, Khandwa Road, Simrol, Indore, 453552, India
   index: 8

date: 16 January 2025
bibliography: paper.bib

---

# Summary

In recent years, numerical simulations have become indispensable for addressing complex astrophysical problems. The so-called magnetohydrodynamics (MHD) framework represents a key tool for investigating the dynamical evolution of astrophysical plasmas. This formalism consists of a set of partial differential equations [@Chiuderi_Velli_2015] that enforce the conservation of mass, momentum, and energy, along with Maxwell’s equation for the evolution of the electromagnetic fields. Due to the high nonlinearity of the MHD equations (regardless of their specifications, e.g., classical/relativistic or ideal/resistive), a general analytical solution is not possible, making numerical approaches crucial. Numerical simulations usually produce large sets of data files and their scientific analysis relies on dedicated software tools designed for data visualization [@ViSit;@ParaView]. However, to encompass all code output features, specialized tools focusing on the numerical code may represent a more versatile and integrated solution. Here, we present PyPLUTO, a Python package tailored for efficient loading, manipulation, and visualization of outputs produced with the [PLUTO code](https://plutocode.ph.unito.it) [@PLUTO_2007;@PLUTO_2012]. PyPLUTO uses memory mapping to optimize data loading and provides general routines for data manipulation and visualization. PyPLUTO also supports the particle modules of the PLUTO code, enabling users to load and visualize particles, such as cosmic rays [@Mignone2018], Lagrangian [@Vaidya2018], or dust [@MIGNONE2019] particles, from hybrid simulations. A dedicated Graphical User Interface (GUI, shown in Fig. \ref{fig1}) simplifies the generation of single-subplot figures, making PyPLUTO a powerful yet user-friendly toolkit for astrophysical data analysis.

![Interactive visualization of shock tube test results (i.e., density, pressure, and velocity profiles) with the GUI. \label{fig1}](pyplutogui.png)

# Statement of Need

The PLUTO code [@PLUTO_2007] is a widely used, freely distributed computational fluid dynamics code designed to solve the classical and (special) relativistic MHD equations in different geometries and spatial dimensions. The original code is written in C (while the upcoming GPU version provides a full [C++ rewrite](https://plutocode.ph.unito.it/pluto-gpu.html)) and it contains several numerical methods adaptable to different contexts. Data post-processing is a crucial step in analyzing the results of any numerical simulation. Other packages addressing related needs (e.g., [plutoplot](https://github.com/Simske/plutoplot)) provide valuable functionality for working with PLUTO data, including loading and visualization. However, they may not support all data formats or offer integration for tasks like data manipulation and advanced plotting.
In this work, we present PyPLUTO, a Python package designed to load, manipulate, and visualize efficiently the output from the PLUTO code.
While a previous version of PyPLUTO is [available](https://github.com/coolastro/pyPLUTO), the package presented here is a complete rewrite hosted at a [new repository](https://github.com/GiMattia/PyPLUTO).
The package retains its core strengths while offering user-friendly methods for generating publication-quality plots with high customization. In addition to its enhanced flexibility, PyPLUTO offers strong computational efficiency, enabling the rapid handling of large datasets typical of state-of-the-art numerical simulations. Through this balance between customization, performance, and ease of use, PyPLUTO represents a key tool to effectively communicate scientific results while minimizing the effort required for post-processing.

# Main Features

PyPLUTO is a package written in Python (version $\geq$ 3.10) with the additions of NumPy [@NUMPY2020], Matplotlib [@MATPLOTLIB_2007], SciPy [@SCIPY_2020], pandas [@PANDAS2020], h5py [@H5PY_2013] and [PyQT6](https://www.riverbankcomputing.com/software/pyqt/intro) (although the last two are optional). The package, which can be installed through pip, primarily consists of three main classes:

• The `Load` class loads and manipulates the PLUTO output files containing fluid-related quantities.

• The `LoadPart` class loads and manipulates the PLUTO output files containing particle-related quantities.

• The `Image` class produces and handles the graphical windows and the plotting procedures.

Additionally, a separate `PyPLUTOApp` class launches a GUI able to load and plot 1D and 2D data in a single set of axes. PyPLUTO has been implemented to be supported by Windows, MacOS, and Linux, through both standard scripts and more interactive tools (e.g., IPython or Jupyter). The style guidelines follow the [PEP8](https://peps.python.org/pep-0008/) conventions for Python codes enforced through the Black package [@Langa2020], and focus on clarity and code readability.
Finally, by leveraging the capabilities of the [sphinx package](http://sphinx-doc.org/sphinx.pdf), PyPLUTO features extensive docstrings, providing a useful reference for both users and developers.

# Benchmark Examples

PyPLUTO provides a set of benchmarks immediately accessible after installing the package. These consist of test problems that can be applied to relevant astrophysical applications and showcase the full range of PyPLUTO’s features. Here we report two examples demonstrating the package’s capabilities.

### Disk-planet Interaction {#diskplanet}
This test simulates the interaction of a planet embedded in a disk [@Mignone_etal_2012] and represents an ideal scenario for understanding the formation and evolution of planetary systems. In particular, the formation of spiral density waves and disk gaps represent some key observational signatures of planet formation and planet-disk interaction [@MelonFuksman2021;@Muley2024a]. In the left panel of Fig. \ref{fig2}, we show an adaptation of Figure 10 of [@Mignone_etal_2012], featuring two separate zoom-ins around the planet’s location.

• The first zoom (upper-right subplot) shows an enlarged view of the density distribution using the same color map and logarithmic scale as the global plot.

• The second zoom (lower-left subplot) highlights the changes in toroidal velocity due to the presence of the planet by employing a different color map (to enhance the sign change) and a linear color scale.

These zoomed views offer deeper insights into the physical processes at play and demonstrate the utility of PyPLUTO for analyzing complex astrophysical systems.

### Particles Accelerated near an X-point {#xpoint}
This test problem examines particle acceleration near an X-type magnetic reconnection region [@Puzzoni2021]. In the last decades, magnetic reconnection [@Mattiaetal2023;@Buglietal2024;@Mattiaetal2024] has proven to be a key physical process to explain the population of non-thermal particles in solar flares, relativistic outflows, and neutron star magnetospheres. This sort of test provides valuable insights into particle acceleration mechanisms in high-energy astrophysical environments by enabling the investigation of particle trajectories and
energy distribution near the X-point.

In the right panel of Fig. \ref{fig2} we show an adaptation of the top panel of Figures 13-14 from [@Mignone2018]. The main plot displays the distribution of test particles, color-coded by their velocity magnitudes, with magnetic field lines overlaid as solid and dashed lines. The inset panel shows the energy spectrum at the initial ($t = 0$, in blue) and final ($t = 100$, in red) time. In this scenario, the absence of a guide field ($\vec{E} \cdot \vec{B} = 0$), results in a symmetric distribution along the y-axis from the combined effects of the gradient, curvature, and $\vec{E} \times \vec{B}$ drifts in the vicinity of the X-point, where the electric field is the strongest.
This plot provides a clear visual representation of particle motion and energy changes, demonstrating how PyPLUTO can be used to investigate complex phenomena such as particle acceleration in astrophysical sources.

![Left panel: example of inset zooms of the planet region of the disk-planet test problem. The main plot and the right zoom show the density on a logarithmic scale, while the left zoom highlights the toroidal velocity on a linear scale. Right panel: example of an X-point region with magnetic field lines overlaid (as contour lines of the vector potential, solid lines). The main plot shows the test-particle distribution, color-coded by velocity magnitudes, while the inset plot displays the particle energy spectrum at the beginning (in blue) and end (in red) of the simulation. \label{fig2}](pyplutotests.png)

# Ongoing research using PyPLUTO

Research applicable with PyPLUTO includes the development of numerical algorithms [@MattiaMignone2022;@Bertaetal2024;@MelonFuksman2025] and numerical simulations of astrophysical objects, such as jets [@MattiaFendt2022;@Mattiaetal2023;@Mattiaetal2024;@Costa2025;@Sciaccaluge2025], star clusters [@Harer2025], and protoplanetary disks [@MelonFuksman2024a;@MelonFuksman2024b], as well as physical processes, such as particle acceleration [@Wangetal2024] and magnetic reconnection [@Buglietal2024].

# Conclusion and Future Perspectives

The PyPLUTO package is designed as a powerful yet flexible tool to facilitate the data analysis and visualization of the output from PLUTO simulations, focusing on user-friendliness while allowing the necessary customization to produce publication-quality figures. To overcome current limitations and further enhance the package’s capabilities, particular focus will be devoted to:

• introducing specific routines for rendering 3D data to provide users with tools for visualizing volumetric data;

• supporting interactive visualization and comparison of multiple simulation outputs, allowing the users to track temporal evolution directly with the GUI;

• expanding the graphical interface to support particle data, including dynamic visualization of particle distributions and trajectories;

Alongside these improvements, PyPLUTO development will focus on encompassing the latest features of the PLUTO code, such as new Adaptive Mesh Refinement strategies and extensions to more general metric tensors. PyPLUTO is a public package that can be downloaded alongside the [CPU and GPU versions of the PLUTO code](https://gitlab.com/PLUTO-code/gPLUTO). Regular updates will be released with improvements and bug fixes. Additionally, a [repository](https://github.com/GiMattia/PyPLUTO) containing the PyPLUTO development versions will be available for users who wish to exploit the code’s latest features in advance.

# Acknowledgments

G. Mattia thanks L. Del Zanna and M. Flock for the discussions on data visualization and the Data Science Department of the Max Planck Institute for Astronomy for helping with Python and Matplotlib.
The authors thank Simeon Doetsch for their insights on memory mapping techniques and Deniss Stepanovs and Antoine Strugarek for their contribution throughout the years to previous PyPLUTO versions.
The authors thank Agnese Costa, Alberto Sciaccaluga, Alessio Suriano, Asmita Bhandare, Dhruv Muley, Dipanjan Mukherjee, Jieshuang Wang, Jacksen Narvaez, Lucia Haerer, Prakruti Sudarshan, Stefano Truzzi, and Stella Boula for testing the module while still under full rewrite.
M. Bugli acknowledges the support of the French Agence Nationale de la Recherche (ANR), under grant ANR-24-ERCS-0006 (project BlackJET).
This project has received funding from the European Union's Horizon Europe research and innovation programme under the Marie Skłodowska-Curie grant agreement No 101064953 (GR-PLUTO).

# References
