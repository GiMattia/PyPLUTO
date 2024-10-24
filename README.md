# PyPLUTO

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

The package is provided with a `LICENSE` file which contains the license terms.

The package is provided with a `CODE_OF_CONDUCT.md` file which contains the code
of conduct.

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

### Documentation

For more detailed instructions and additional installation options, please refer to the PyPLUTO documentation where you can find comprehensive guides and examples.
