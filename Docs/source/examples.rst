Examples
========

The following benchmark problems showcase PyPLUTO's capabilities using data
from standard PLUTO test problems. All necessary data is bundled with the
package, so no PLUTO installation is required.

After installing PyPLUTO (``pip install py-pluto``), examples are accessible
via the command-line interface:

.. code-block:: console

   $ pypluto-examples list          # list all available examples
   $ pypluto-examples copy          # copy example scripts to ./pypluto_examples/
   $ pypluto-examples run test01_sod  # run one example directly

or through the Python API:

.. code-block:: python

   import pyPLUTO as pp

   print(pp.examples_path())        # path to the installed examples directory
   pp.copy_examples()               # copies scripts to ./pypluto_examples/
   pp.run_example("test01_sod")     # runs one example script

The example scripts themselves load data via ``pyPLUTO.find_example()``, which
resolves the bundled data path regardless of the installation method.

|

----

.. toctree::

  test01_sod
  test02_ot
  test03_rti
  test04_rotor
  test05_fieldloop
  test06_diskplanet
  test07_khi
  test08_torus
  test09_blast
  test10_riemann2d
  test11_crxpoint
  test12_riemannlp
  test13_flowpastcyl

|

----

.. This is a comment to prevent the document from ending with a transition.
