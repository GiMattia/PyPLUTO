import pyPLUTO    as pp
import matplotlib as mpl
import numpy      as np

print(f"Testing the Image class initialization... ".ljust(50), end='')

# Check the default values of the figure created in the __init__
I = pp.Image()
assert type(I.fig) == mpl.figure.Figure
assert I.fig.get_figwidth()     == 8.0
assert I.fig.get_figheight()    == 5.0
assert I.fig._suptitle          == None
assert I.fontsize               == 17
assert I.fig.get_tight_layout() == False
assert I.fig.number             == 1

# Check the window number
I = pp.Image(nwin = 2)
assert I.fig.number == 2

# Check the figure size
I = pp.Image(figsize = (6,7))
assert I.fig.get_figwidth()  == 6.0
assert I.fig.get_figheight() == 7.0

# Check the suptitle
I = pp.Image(suptitle = 'This is a title')
assert I.fig._suptitle.get_text() == 'This is a title'

# Check the fontsize
I = pp.Image(fontsize = 20)
assert I.fontsize == 20

# Check the tight layout
I = pp.Image(tight = False)
assert I.fig.get_tight_layout() == False

# Test the LaTeX
pass

# Test the colorlines
pass

print("\033[34mPASSED!\033[0m")
