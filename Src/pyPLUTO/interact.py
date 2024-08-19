from .libraries import *

def interactive(self, varx, vary = None, fig = None, **kwargs):
    """
    Creates an interactive plot with a slider to change the data.
    Warning: it works only with the fluid variables.

    Returns
    -------

    - None.

    Parameters
    ----------

    - varx: array_like
        The x-axis variable.
    - vary: array_like, default None
        The y-axis variable.
    - fig: Figure, default None
        The figure instance.
    - ax: Axes, default None
        The axes instance.
    - vmin: float, default None
        The minimum value of the data.
    - vmax: float, default None
        The maximum value of the data.
    
    Notes
    -----

    - Check vmin and vmax to set the colorbar limits.
    - Interact is a very primordial version and it should not be used tu perform
      very complex plots. Instead, it gives a very nice overview of the data
      as functions of time (like in other softwares such as visit or paraview).

    ----

    ========
    Examples
    ========

    - Example #1: Create an interactive 2D plot

        >>> import pyPLUTO as pp
        >>> D = pp.Load('all')
        >>> I = pp.Image()
        >>> I.interactive(D.rho, x1 = D.x1, x2 = D.x2, 
        ... cpos = 'right', vmin = 0, vmax = 1.0)
        ... 
        >>> pp.show()

    - Example #2: Create an interactive 1D plot with a composite variable

        >>> import pyPLUTO as pp
        >>> import numpy as np
        >>> D = pp.Load('all')
        >>> pp.Image().interactive(D.x1, np.sqrt(D.vx1**2 + D.vx2**2))
        >>> pp.show()

    """

    # Store the variable x
    if vary is None:
        vary = varx
        splt = np.ndim(varx[0])
        # Use range if the variable is 1D
        if splt == 1:
            varx = np.arange(len(vary))

    # Store the variable to animate
    self.anim_var = vary
    nsld = len(vary) - 1

    # Check the number of dimensions
    splt = np.ndim(vary[0])

    # Set or create figure and axes (to test)
    ax, nax = self._assign_ax(kwargs.pop('ax', None), **kwargs, tight = False)
    self.anim_ax  = ax

    # Position the slider
    pos_slider = ax.get_position()
    pos_x0     = pos_slider.x0*1.5
    pos_x1     = pos_slider.x1*0.95 - pos_x0
    sliderax   = self.fig.add_axes((pos_x0, 0.02, pos_x1, 0.04))

    # Create the slider
    self.slider = Slider(sliderax, label = "out", valmin = 0, valmax = nsld, 
                                   valinit = 0, valstep = 1, valfmt = '%d')
    self.slider.on_changed(self._update_slider)

    # Display the data
    if splt == 2:
        # Display the data if it is 2D
        self.display(self.anim_var[0], ax = ax,  
                     vmin = kwargs.pop('vmin',self.anim_var.min()), 
                     vmax = kwargs.pop('vmax',self.anim_var.max()), **kwargs)
        self.anim_pcm = ax.collections[0]
    else:
        # Plot the data if it is 1D
        self.plot(varx,np.array(vary[0].tolist()), ax = ax, **kwargs)
        self.anim_pcm = ax.get_lines()[0]

    return None

def _update_slider(self, i: int) -> None:
    """
    Updates the data in the interactive plot.

    Returns
    -------

    - None.

    Parameters
    ----------

    - i: int
        The slider index.

    Notes
    -----

    - None.

    ----

    ========
    Examples
    ========

    - Example #1: Update the data in the interactive plot

        >>> _update_slider(1)

    """

    # Update the data
    var = self.anim_var[int(i)]
    if np.ndim(var) == 2:
        # Update the data array if it is 2D
        self.anim_pcm.set_array(var.T.ravel())
    elif np.ndim(var) == 1:
        # Update the data array if it is 1D
        self.anim_pcm.set_ydata(var)
    
    # Update the plot
    self.fig.canvas.draw()

    # End of the function
    return None
