Installation
============

The latest version of the *pyPLUTO* code is officially distributed with the
latest version (4.4) of the *PLUTO* code. This can be downloaded from PlutoDownload_.

.. _PlutoDownload: http://plutocode.ph.unito.it/download.html

The current version of *pyPLUTO* has been updated to support Python version 3.

For all the methods the installing directory is the pyPLUTO directory (or a subfolder):

.. code-block:: console

   $ cd $PLUTO_DIR/Tools/pyPLUTO

For the sake of simplicity, we will assume to be in the pyPLUTO directory  from now until the
end of the installation process.

Global installation
-------------------

A global installation of pyPLUTO by default creates a PYTHONPATH.
Three ways of global installation can be followed, depending on which libraries and
software are installed on the computer.

1. The first method is (if pip is installed) to install pyPLUTO from the main directory
through the command:

.. code-block:: console

   (.venv) $ pip install ./

2. If this procedure does not work another installation (again through pip) is possible.
This time the installation is done from the Src directory through the setup.py file:

.. code-block:: console

   (.venv) $ cd Src
   Src$ pip install ./

3. If pip has not been installed a global installation through the ``setup.py`` can be done:

.. code-block:: console

   (.venv) $ cd Src
   Src$ python setup.py install

Local installation
-------------------

If pip is not installed, a good pratice is to create your own PYTHONPATH
and do a local install in the following way:

1. Create a directory where to store this module.
This directory does not need to be in the pyPLUTO folder, it can be in the HOME
directory or any of its subfolders. For the sake of simplicity we will assume that this
directory will be created as a direct subfolder of the HOME directory:

.. code-block:: console

  (.venv) $ cd
  $ mkdir MyPython_Modules

2. Go back to the pyPLUTO directory:

.. code-block:: console

  $ cd $PLUTO_DIR/Tools/pyPLUTO/Src

3. Install the code in the directory created:

.. code-block:: console

  (.venv)/Src$ python setup.py install --prefix=~/MyPython_Modules

Remember that, in case you created the ``MyPython_Modules`` folder in a different
location you should install the code following:

.. code-block:: console

  (.venv)/Src$ python setup.py install --prefix=<path to MyPython_Modules>

4. Append the following in your ``~/.bashrc`` file:

.. code-block:: console

  export PYTHONPATH =~/MyPython_Modules/lib/python<ver>/site-packages
  export PATH =~/MyPython_Modules/bin:$PATH

where ``<ver>`` indicates the python version used to install pyPLUTO.

5. Update the ``~/.bashrc`` file:

.. code-block:: console

  (.venv)/Src$ source ~/.bashrc
