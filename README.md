# PyPLUTO: a data analysis Python package for the PLUTO code

| Category | Badges |
| --- | --- |
| Package | [![Project Status: Active](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active) ![Python Versions](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat&logo=python&logoColor=white) ![GitHub release](https://img.shields.io/github/v/release/GiMattia/PyPLUTO?include_prereleases&label=Github%20Release) [![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) |
| Tests | [![Windows Tests](https://github.com/GiMattia/PyPLUTO/actions/workflows/test_windows.yml/badge.svg)](https://github.com/GiMattia/PyPLUTO/actions/workflows/test_windows.yml) [![MacOS Tests](https://github.com/GiMattia/PyPLUTO/actions/workflows/test_macos.yml/badge.svg)](https://github.com/GiMattia/PyPLUTO/actions/workflows/test_macos.yml) [![Linux Tests](https://github.com/GiMattia/PyPLUTO/actions/workflows/test_linux.yml/badge.svg)](https://github.com/GiMattia/PyPLUTO/actions/workflows/test_linux.yml) ![Coverage Report](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/GiMattia/384b1f3a3a3b74cdbd65c4e3dce0632f/raw/pytest-coverage-comment__main.json) |
| Style | [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com//GiMattia/PyPLUTO/actions/workflows/pre-commit.yml) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) ![Pylint](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/GiMattia/8fc3a521f1c5e59e41eb16d1197bf8c8/raw/pylint-score.json) |
| Distribution | [![Arxiv](https://img.shields.io/badge/arXiv-2501.09748-8F1515?style=flat&logo=arxiv&logoColor=red)](https://doi.org/10.48550/arXiv.2501.09748) [![Documentation](https://readthedocs.org/projects/pypluto/badge/?version=latest)](https://pypluto.readthedocs.io/en/latest/?badge=latest) |
![Mypy](https://img.shields.io/badge/type_checking-mypy-brightgreen) |
<!-- ![Doc Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/GiMattia/cc212934fc58b93ddebda8c669dbb171/raw/interrogate-badge.svg) -->

<!-- ![PyPI](https://img.shields.io/pypi/v/PyPLUTO) -->
<!-- ![Conda](https://img.shields.io/badge/conda-available-brightgreen) -->
<!-- ![Zenodo](https://img.shields.io/badge/zenodo-DATA-brightgreen) -->
<!-- [![DOI](https://joss.theoj.org/papers/.../status.svg)](https://doi.org/...) -->



PyPLUTO is a Python library which loads and plots the data obtain from the
PLUTO code simulations.
The aim of this package is to simplify some non-trivial python routines in order
to quickly recover effective plots that are suited for scientific publications.

The package is designed to be used in both an interactive environment like
ipython shell or Jupyter notebook and standard Python scripts.

The package is structured as follow:

- the Load class is used to load the data from the PLUTO simulation fluid files.
- the LoadPart class is used to load the data from the PLUTO simulation particle files.
- the Image class is used to visualize the loaded data.
- additional functions (e.g., to save the images) are included in the package.

The package includes a set of examples in the `Examples` directory.

The package is tested on Python 3.10 (and newer versions) and with the following dependencies:

- `numpy`
- `matplotlib`
- `scipy`
- `pandas`
- `h5py`
- `PyQt6`

The package is provided with a `LICENSE` file which contains the license terms.

The package is provided with an extensive documentation in the `Docs` directory.

## Installation Instructions

To install the PyPLUTO package, you can use the following methods:

### Installation with pip

The easiest way to install PyPLUTO is through pip. Open your terminal and run the following command:

```bash
pip install ./
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
pp.Image().plot(D.x1, D.rho)
pp.show()
```

while 2D plots can be created with

```python
D = pp.Load()
pp.Image().display(D.rho, x1=D.x1, x2=D.x2, cpos="right")
pp.show()
```

## Examples

In order to test PyPLUTO capabilities, even without the PLUTO code, we provide
an extensive tests suite with all the necessary data.
In this way, PyPLUTO can be explored without any knowledge of the PLUTO code.
All the tests are located in the `Examples` directory and are aimed at showing
how to exploit the package capabilities.

## Documentation

For more detailed instructions and additional installation options, please refer to the PyPLUTO documentation where you can find comprehensive guides and examples.

## Cite This Repository

If you use this repository in your research or projects, please consider citing the arxiv paper.

```
@ARTICLE{PyPLUTO2025,
       author = {{Mattia}, Giancarlo and {Crocco}, Daniele and {Melon Fuksman}, David and {Bugli}, Matteo and {Berta}, Vittoria and {Puzzoni}, Eleonora and {Mignone}, Andrea and {Vaidya}, Bhargav},
        title = "{PyPLUTO: a data analysis Python package for the PLUTO code}",
      journal = {arXiv e-prints},
     keywords = {Astrophysics - Instrumentation and Methods for Astrophysics},
         year = 2025,
        month = jan,
          eid = {arXiv:2501.09748},
        pages = {arXiv:2501.09748},
          doi = {10.48550/arXiv.2501.09748},
}
```

We recommend to put one the following expressions in your manuscript:

"The figures presented in this paper were generated using the PyPLUTO package (citation to the paper)"

"This research has benefited from the PyPLUTO package for data visualization (citation to the paper)"

## Contributing

If you have any questions, suggestions or find a bug, feel free to open an issue or fork the repository and create a pull request.
Any contribution aimed at helping the PLUTO code community to have better plots with less efforts will be greatly appreciated.
If you want to contribute to PyPLUTO please be sure to install it in the developer mode, through the command:

```bash
pip install -r requirements_dev.txt
```

### Rules for Contributing

We use pre-commit to ensure that the code is consistent with the code guidelines, including the "black" format and several "ruff" checks.
You can either link the pre-commit to the repository through the command

```bash
pre-commit install
```

or by enforcing the guide styles manually through the command

```bash
pre-commit run --all-files
```

Before opening a pull request,there is the possibility to run a deeper series of checks, including tests with coverage, pylint check, docstring coverage and so through the command

```bash
pre-commit run --all-files --hook-stage manual
```

If one or more tests do not pass the automatic code checks anforced through github actions will not allow the pull request to pass, so is higly recommended to run the full pre-commit before every pull request.
For any question or enquiry, please contact one of the administrators.
