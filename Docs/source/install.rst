Installation
============

The latest version of the *PyPLUTO* code is officially distributed with the
latest version (5.0) of the *PLUTO* code. This can be downloaded from 
PlutoDownload_.

.. _PlutoDownload: http://plutocode.ph.unito.it/download.html

The current version of *PyPLUTO* has been updated to support Python version 3.10
or newer.
Additional packages that are required are numpy, matplotlib,
scipy, pandas and h5py (although the latter is not mandatory).

All the relevant files are stored in the PyPLUTO directory, whichcan be accessed by typing:

.. code-block:: console

   $ cd $PLUTO_DIR/Tools/pyPLUTO

For the sake of simplicity, we will assume to be in the PyPLUTO directory from 
now until the end of the installation process.

|

----

Installation with pip
---------------------

The easiest and most efficient PyPLUTO installation is through pip, which can 
Tdone in two ways:

1. The first method is to install PyPLUTO from the main 
directory through the command:

.. code-block:: console

   (.venv) $ pip install ./

2. If this procedure does not work another installation is 
possible.
This time the installation is done from the Src directory through the setup.py 
file:

.. code-block:: console

   (.venv) $ cd Src
   Src$ pip install ./
   
Note that in this way, if you are working with conda, your installation will be always
confined within your conda environment.
   
Installation without pip
------------------------

If pip has not been installed a global installation through the ``setup.py`` 
can be done:

.. code-block:: console

   (.venv) $ cd Src
   Src$ python setup.py install


However, a good pratice is to create your own PYTHONPATH
and do a local install in the following way:

1. Create a directory where to store this module.
This directory does not need to be in the PyPLUTO folder, it can be in the HOME
directory or any of its subfolders. For the sake of simplicity we will assume 
that this directory will be created as a direct subfolder of the HOME directory:

.. code-block:: console

  (.venv) $ cd
  $ mkdir MyPython_Modules

2. Go back to the PyPLUTO directory:

.. code-block:: console

  $ cd $PLUTO_DIR/Tools/pyPLUTO/Src

3. Install the code in the directory created:

.. code-block:: console

  (.venv)/Src$ python setup.py install --prefix=~/MyPython_Modules

Remember that, in case you created the ``MyPython_Modules`` folder in a 
different location you should install the code following:

.. code-block:: console

  (.venv)/Src$ python setup.py install --prefix=<path to MyPython_Modules>

4. Append the following in your ``~/.bashrc`` file:

.. code-block:: console

  export PYTHONPATH =~/MyPython_Modules/lib/python<ver>/site-packages
  export PATH =~/MyPython_Modules/bin:$PATH

where ``<ver>`` indicates the python version used to install PyPLUTO.

5. Update the ``~/.bashrc`` file:

.. code-block:: console

  (.venv)/Src$ source ~/.bashrc

|

----

.. This is a comment to prevent the document from ending with a transition.
