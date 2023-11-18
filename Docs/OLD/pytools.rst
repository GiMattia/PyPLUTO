pyPLUTO quick tools
===================

While the Tools class includes all the functions required to process and
manipulate the data (e.g. slices, nabla operators, etc.), other quick python
functions (which are already built in the numpy/matplotlib/scipy libraries)
are needed in order to see/save the figures.

In order to avoid the loading of such libraries only to write a single additional
line of code, we built some simple key functions within the pyPLUTO module.

Be aware that these functions are a very simplified version of the original python
function, and therefore, in case additional levels of complexity are needed, we
strongly encourage the users to make use of the standard python functions instead
of these ones.
