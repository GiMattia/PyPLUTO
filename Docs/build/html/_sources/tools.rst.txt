Manipulating the data
=====================

Once loaded, both fluid and particle data can be customized in order to retrieve
fundamental quantities.

Variables and grid conversion
-----------------------------

.. toctree::
   :hidden:

   cartesian_vector
   reshape_cartesian
   reshape_uniform
   slices

PyPLUTO works with all the geometries accessible with the PLUTO code.
In order to obtain field lines in non-cartesian geometries, some additional
procedures should be followed. First, the vector components whould bconverted
into the cartesian ones through the :ref:`cartesian_vector <cartesian_vector>`
method, which works for both polar and spherical coordinates.
Next, the variables and the grid can be converted into a cartesian mesh by using
the :ref:`reshape_cartesian <reshape_cartesian>` method.
Note that the inner radial zones will also be interpolated for the sake of
simplicity. One this transformation is complete, field lines become possible
as with cartesian grids.
In order to reshape the domain, the :ref:`reshape_uniform <reshape_uniform>`
method is used. Such method converts a stretched grid into a uniform one, and
can be used also for cartesian grids since it does not alter the geometry of
the grid but only its spacing.

Variables can also be slices through one or more axes and through the major and
minor diagonal by using the :ref:`slices <slices>` method.

|

----

Field and contour lines tool
----------------------------

.. toctree::
   :hidden:

   find_fieldlines
   find_contour

The :ref:`find_fieldlines <find_fieldlines>` methods represents an upgrade in
terms of accuracy when compared to the streamplot method. Here the field lines
are computed through high-order integration algorithms starting from a selected
footpoint in both directions. Additional checks, e.g. exiting from the domain
or closing the field line, are performed.
Once the lines are computed, they can be plotted through standard plotting
methods.
The same principle works for the :ref:`find_contour <find_contour>` method,
which aims at finding all the contour lines of sleected levels (or a range
of levels linearly or logarithmically spaced) in any geometry.
As for the field lines, here the contour lines are only computed (and associated
to a color depending on the level) and can be plotted through standard plotting
methods. Such method, however, has an enhanced accuracy when compared with the
plotting contour method.

|

----

Fourier Transform
-----------------

.. toctree::
   :hidden:

   fourier

Fourier transform can be performed in all dimensions considering or exclunding
selected directions through the :ref:`fourier <fourier>` method. Note that this
method works only in cartesiangeometry and for uniform grids (but the
:ref:`reshape_uniform <reshape_uniform>` method can convert a stretched grid
into a cartesian one).

|

----


Derivatives
-----------

.. toctree::
   :hidden:

   gradient
   divergence
   curl

Derivatives (such as :ref:`gradient <gradient>`, :ref:`divergence <divergence>`
and :ref:`curl <curl>` can be perfoemrd in any geometry and dimension. A 3-cells
stencil is computed in order to achieve at least second-order accuracy.

|

----

Spectrum and select particles
-----------------------------

Particle spectra are a key tool in order to investigate their acceleration in
magnetized plasma. The :ref:`spectrum <spectrum>` method has a variable number
of bins and can be done in both linear and logarithmic scale.
In case particles need a filter, the :ref:`select <select>` method can be
adopted to sort or find a particles subset with specific requirements.
Both a string and a lambda function can be adopted.

.. toctree::
   :hidden:

   spectrum
   select

|

----

.. This is a comment to prevent the document from ending with a transition.
