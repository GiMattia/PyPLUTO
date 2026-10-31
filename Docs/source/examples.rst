Examples
========

The examples come in two groups:

- The :doc:`gallery <gallery/index>` shows one feature at a time: short
  scripts on synthetic data, grouped by topic, each with its figure and
  its code. They run as they are, with nothing but pyPLUTO installed, and
  every page can be downloaded as a Python script or a Jupyter notebook.

- The :doc:`PLUTO test problems <pluto_tests/index>` are complete
  scripts: each loads the output of a standard PLUTO test problem and
  builds a publication-ready figure, combining loading, the analysis
  tools and plotting. The data are bundled with pyPLUTO, so no PLUTO
  installation is needed.

|

----

Running the PLUTO test problems
-------------------------------

The scripts of the test problems are installed with pyPLUTO
(``pip install py-pluto``), and can be listed, copied and run from the
command line:

.. code-block:: console

   $ pypluto-examples list            # list the examples
   $ pypluto-examples copy            # copy them to ./pypluto_examples/
   $ pypluto-examples run test01_sod  # run one

or from Python:

.. code-block:: python

   import pyPLUTO as pp

   print(pp.examples_path())     # where they are installed
   pp.copy_examples()            # copy them to ./pypluto_examples/
   pp.run_example("test01_sod")  # run one

Each script finds its data through ``pyPLUTO.find_example()``, which gives
the path of the bundled data however pyPLUTO was installed.

.. toctree::
  :hidden:
  :maxdepth: 1

  gallery/index
  pluto_tests/index

|

----

.. This is a comment to prevent the document from ending with a transition.
