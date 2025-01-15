# PyPLUTO
![GitHub release](https://img.shields.io/github/v/release/GiMattia/PyPLUTO?include_prereleases&label=Github%20Release)
![PyPI](https://img.shields.io/pypi/v/PyPLUTO)
[![Documentation](https://readthedocs.org/projects/PyPLUTO/badge/?version=latest)](https://PyPLUTO.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![License: GPL-3.0-only](https://img.shields.io/badge/license-GPLv3-blue)](https://opensource.org/license/gpl-3-0)
<!-- [![Arxiv](https://img.shields.io/badge/)](https://doi.org/) -->

[![Windows Tests](https://github.com/GiMattia/PyPLUTO/actions/workflows/test_windows.yml/badge.svg)](https://github.com/GiMattia/PyPLUTO/actions/workflows/test_windows.yml)
[![MacOS Tests](https://github.com/GiMattia/PyPLUTO/actions/workflows/test_macos.yml/badge.svg)](https://github.com/GiMattia/PyPLUTO/actions/workflows/test_macos.yml)
[![Linux Tests](https://github.com/GiMattia/PyPLUTO/actions/workflows/test_linux.yml/badge.svg)](https://github.com/GiMattia/PyPLUTO/actions/workflows/test_linux.yml)

PyPLUTO is a Python library which loads and plots the data obtain from the
PLUTO code simulations.
The aim of this package is to simplify some non-trivial python routines in order
to quickly recover effective plots that are suited for scientific publications.

The package is designed to be used in both an interactive environment like
ipython shell or Jupyter notebook and standard Python scripts.

The package is structured as follow:

- the Load class is used to load the data from the PLUTO simulation fluid files.
- the Loadpart class is used to load the data from the PLUTO simulation particle files.
- the Image class is used to visualize the loaded data.
- additional functions (e.g., to save the images) are included in the package.

The package includes a set of examples in the `Tests` directory.

The package is tested on Python 3.10 (and newer versions) and with the following dependencies:

- `numpy >= 1.19`
- `matplotlib >= 3.3`
- `scipy`
- `pandas`
- `h5py` (optional)
- `PyQt6` (optional)

The package is provided with a `LICENSE` file which contains the license terms.

The package is provided with an exstensive documentation in the `Docs` directory.

## Installation Instructions

To install the PyPLUTO package, you can use the following methods:

### Installation with pip

The easiest way to install PyPLUTO is through pip. Open your terminal and run the following command:

```bash
pip install -e ./
```

Ensure that you are using Python 3.10 or newer, as the package is compatible from this version onwards.

### Installation without pip

If you need to install the package without pip, you can do so by navigating to the source directory and using the `setup.py` file. Run the commands below:

```bash
cd Src
python setup.py install
```

This method allows installation in a non-editable mode, and it is recommended to use a virtual environment to avoid conflicts with other packages.

## Quick Start

```python
import pyPLUTO as pp
```

Simulations can be loaded by just providing the path to the simulation directory. The last output (if not specific
file is selected) is automatically found, as well as the available PLUTO file in the selected folder.

```python
D = pp.Load()
print(D)
```

Relevant simulations attributes (such as the computational grid, the geometry and the variables to load) are found automatically.
The data can be plotted through the Image class, which acts as a simplified maptlotlib wrapper.
An example of 1D plot of the density can be:

```python
D = pp.Load()
pp.Image().plot(D.x1,D.rho)
```

while 2D plots can be created with

```python
D = pp.Load()
pp.Image().display(D.rho, x1 = D.x1, x2 = D.x2)
```

## Documentation

For more detailed instructions and additional installation options, please refer to the PyPLUTO documentation where you can find comprehensive guides and examples.

## Contributing

If you have any questions, suggestions or find a bug, feel free to open an issue or fork the repository and create a pull request.
Any contribution aimed at helping the PLUTO code community to have better plots with less efforts will be greatly appreciated.

### Rules for Contributing

- **We do not enforce any strict style convention for PyPLUTO contributions, as long as code maintains high readability and overall quality.**

- If you are unsure on what style to use, please contact one of the administrators
