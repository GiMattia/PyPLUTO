.. _faq:

FAQs
====

This section contains all the Frequently Asked Questions regarding the
installation of the PyPLUTO package and its use.

|

----

How do I install PyPLUTO?
-------------------------

To install PyPLUTO, you can use the procedure explained in the
:ref:`installation` section.

|

----

Can I use PyPLUTO with Python 3.9 or 3.10?
-------------------------------------------

No, PyPLUTO is compatible only from Python 3.11 onwards.
Although we do not expect to always update PyPLUTO to only the latest version
possible, we will try to keep it up to date with the latest versions of Python
to take advance to the most up-to-date features.

|

----

What file formats does PyPLUTO support?
---------------------------------------

PyPLUTO supports all output formats produced by the PLUTO code:

- **Fluid data**: ``dbl``, ``flt``, ``vtk``, ``dbl.h5``, ``flt.h5``,
  ``hdf5`` (AMR via CHOMBO), and ``tab`` (serial, 1D/2D only).
- **Particle data**: ``dbl``, ``flt``, ``vtk``.

Both single-file and multiple-file (one file per variable) layouts are
supported for binary and VTK formats. Descriptor files (``.out``) are
required for binary formats and recommended for all others.

|

----

What is the difference between ``Load`` and ``LoadPart``?
---------------------------------------------------------

:ref:`Load <load>` is used to load **fluid** output files (density, pressure,
velocity, magnetic fields, etc.). :ref:`LoadPart <loadpart>` is used to load
**particle** output files. Both classes share the same architecture and support
the same unit attachment methods (``to_astropy_units``, ``to_code_units``).

|

----

Can I use PyPLUTO without having the PLUTO code installed?
----------------------------------------------------------

Yes. PyPLUTO ships with a set of bundled example datasets that can be used
independently of the PLUTO code. After installing the package, run:

.. code-block:: console

   $ pypluto-examples list
   $ pypluto-examples run test01_sod

See the :ref:`examples <examples>` section for the full list.

|

----

How do I attach physical units to loaded variables?
----------------------------------------------------

Pass ``units=True`` when loading to attach CGS units to all known variables:

.. code-block:: python

   D = pp.Load(units=True)

To attach units to specific variables only:

.. code-block:: python

   D = pp.Load(units=["rho", "prs"])

Units can also be attached or removed after loading:

.. code-block:: python

   D.to_astropy_units("rho")   # attach
   D.to_code_units("rho")      # remove

Unit scales are resolved automatically from the PLUTO log file or
``definitions.h``. Custom scales can be supplied via the ``user_units``
keyword. See the :ref:`to_astropy_units <to_astropy_units>` page for details.

|

----

How do I define custom variables in the GUI?
--------------------------------------------

In the variables panel, select **"Custom var..."** from the variable dropdown.
A dialog opens where you can define one or more variables using the syntax::

   NAME = EXPR

For example::

   beta = 2 * prs / (Bx1**2 + Bx2**2 + Bx3**2)

Prefixing a name with ``!`` computes it silently without adding it to the
dropdown (useful for intermediate quantities). Custom variables persist across
output reloads within the same session.
See the :ref:`guivars` section for the full syntax reference.

|

----

Can I use PyPLUTO with simulation codes other than PLUTO?
---------------------------------------------------------

The :ref:`Image <imageclass>` class is entirely code-independent and can be
used to visualize any data loaded into NumPy arrays.
Additionally, native loading support is provided for:

- **ECHO** (parameters: ``nout``, ``path``, ``vars``)
- **IDEFIX**

|

----

How do I create 1D and 2D plots with the Image class?
------------------------------------------------------

Create an :ref:`Image <image>` instance and call :ref:`plot <plot>` for 1D or
:ref:`display <display>` for 2D:

.. code-block:: python

   D = pp.Load()
   I = pp.Image()
   I.create_axes()

   # 1D
   I.plot(D.x1, D.rho, label="density")
   I.legend()

   # 2D
   I.display(D.rho, x1=D.x1, x2=D.x2, cpos="right")

   pp.show()

Both methods accept a wide range of keywords for labels, scales, colormaps, and
axis ranges, and internally call :ref:`set_axis <set_axis>` for per-subplot
customization.

|

----

How do I create a figure with multiple subplots?
-------------------------------------------------

Use :ref:`create_axes <create_axes>` to define the subplot grid before plotting:

.. code-block:: python

   I = pp.Image()
   I.create_axes(ncols=2, nrows=1)   # two side-by-side panels
   I.plot(D.x1, D.rho, nwin=0)
   I.plot(D.x1, D.prs, nwin=1)
   pp.show()

For non-uniform layouts (different size ratios or overlapping axes),
``create_axes`` can be called multiple times on the same ``Image``.

|

----

How do I create interactive or animated plots?
----------------------------------------------

Load multiple outputs with ``nout="all"`` and use
:ref:`interactive <interactive>` to navigate through them with a slider:

.. code-block:: python

   D = pp.Load(nout="all")
   I = pp.Image()
   I.interactive(D, "rho")
   pp.show()

To save the evolution as a video, use :ref:`animate <animate>`:

.. code-block:: python

   I.animate(D, "rho", filename="rho_evolution.mp4")

|

----

How do I plot field lines and contour lines?
--------------------------------------------

PyPLUTO offers two approaches with different accuracy/speed trade-offs.

**Quick visualization** — use the :ref:`streamplot <streamplot>` and
:ref:`contour <contour>` methods directly on the ``Image`` class. These wrap
the corresponding Matplotlib routines and are fast but limited to Cartesian
grids:

.. code-block:: python

   I.streamplot(D.vx1, D.vx2, x1=D.x1, x2=D.x2)
   I.contour(D.rho, x1=D.x1, x2=D.x2, levels=10)

**High-accuracy computation** — use :ref:`find_fieldlines <find_fieldlines>`
and :ref:`find_contour <find_contour>` on the ``Load`` object. These compute
lines via high-order ODE integration (field lines) or the ``contourpy``
library (contour lines) and work in any geometry. For non-Cartesian grids,
first convert to a Cartesian mesh with ``reshape_cartesian``:

.. code-block:: python

   D.reshape_cartesian()
   lines = D.find_fieldlines(D.Bx1c, D.Bx2c, footpoints=[(0.5, 0.0)])
   for line in lines:
       I.plot(line[0], line[1])

|

----

How do I report a bug or request a feature?
--------------------------------------------

Please open an issue on the
`GitHub repository <https://github.com/GiMattia/PyPLUTO>`_.
For contributing guidelines see the :ref:`contributing` section.

|

----

.. This is a comment to prevent the document from ending with a transition.
