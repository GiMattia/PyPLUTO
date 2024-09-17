from .libraries import *

def interactive(self, 
                varx: np.ndarray, 
                vary: np.ndarray | None = None, 
                check: bool = True,
                limfix = True,
                labslider = None,
                **kwargs
               ) -> None:
    """
    Creates an interactive plot with a slider to change the data.
    Warning: it works only with the fluid variables.

    Returns
    -------

    - None

    Parameters
    ----------

    - varx (not optional): array_like
        The x-axis variable.
    - vary: array_like, default None
        The y-axis variable.
    - ax: Axes, default None
        The axes instance.
    - labslider: str, default None
        The label of the slider.
    - limfix: bool, default True
        If True, the colorbar limits are fixed through the entire animation.
    - **kwargs: Any
        Other parameters to pass used in the plot or display functions.
    - vmin: float, default None
        The minimum value of the data.
    - vmax: float, default None
        The maximum value of the data.
    
    Notes
    -----

    - Check vmin and vmax to set the colorbar limits.
    - Interact is a very primordial version and it should not be used tu perform
        very complex plots. Instead, it gives a very nice overview of the data
        as functions of time (like in other softwares such as visit or 
        paraview).
    - The checking of the parameters has not been enabled yet!

    ----

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

    # Check parameters
    #param = {'ax','vmin','vmax'}
    #if check is True:
    #    check_par(param, 'interactive', **kwargs)

    # Store the variable x. If vary is None, it is set to varx
    if vary is None:
        vary = varx
        splt = np.ndim(varx[0])
        # Use range if the variable is 1D
        if splt == 1:
            varx = np.arange(len(vary))

    # Store the variable to animate
    self.anim_var = vary
    self.nsld     = len(vary)
    nsld          = self.nsld - 1
    self.lenlab   = len(str(nsld))    

    # Check the number of dimensions
    splt = np.ndim(vary[0])

    # Set or create figure and axes (to test)
    ax, nax = self._assign_ax(kwargs.pop('ax', None), **kwargs, tight = False)
    self.anim_ax  = ax

    # Position the slider
    pos_slider = ax.get_position()
    pos_x0     = pos_slider.x0*(1.5 + 0.2*(self.lenlab - 2))
    pos_x1     = pos_slider.x1*0.95 - pos_x0

    # Adjust the lower part of the position by increasing the 'y0' value
    if 'xtitle' in kwargs:
        new_pos = [pos_slider.x0, pos_slider.y0 + 0.07, 
                   pos_slider.width, pos_slider.height - 0.07]

        # Apply the new position
        ax.set_position(new_pos)

    sliderax   = self.fig.add_axes((pos_x0, 0.02, pos_x1, 0.04))

    # Create the slider
    if labslider is not None:
        self.labslider = labslider
        label = labslider[0]
    else:
        self.labslider = None
        label = f"nout = {int(0):0{self.lenlab}d}"
    self.slider = Slider(sliderax, label = label, valmin = 0, valmax = nsld, 
                                   valinit = 0, valstep = 1, valfmt = '%d')
    self.slider.on_changed(self._update_slider)

    # Display the data
    if splt == 2:

        self.limfix = limfix
        vmin = self.anim_var.min() if limfix is True else self.anim_var[0].min()
        vmax = self.anim_var.max() if limfix is True else self.anim_var[0].max()

        vmin = kwargs.pop('vmin',vmin)
        vmax = kwargs.pop('vmax',vmax)

        # Display the data if it is 2D
        self.display(self.anim_var[0], ax = ax,  
                     vmin = vmin, vmax = vmax, **kwargs) 
        self.anim_pcm = ax.collections[0]
    else:
        # Plot the data if it is 1D
        self.plot(varx,np.array(vary[0].tolist()), ax = ax, **kwargs)
        self.anim_pcm = ax.get_lines()[0]

    return None


def _update_slider(self, 
                   i: int
                  ) -> None:
    """
    Updates the data in the interactive plot.

    Returns
    -------

    - None

    Parameters
    ----------

    - i  (not optional): int
        The slider index.

    Notes
    -----

    - None

    ----

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

        # Update vmin and vmax dynamically
        if self.limfix is False:
            self.anim_pcm.set_clim(self.anim_var[int(i)].min(),
                                   self.anim_var[int(i)].max())

    elif np.ndim(var) == 1:
        # Update the data array if it is 1D
        self.anim_pcm.set_ydata(var)

    if self.labslider is not None:
        self.slider.label.set_text(self.labslider[i])
    else:
        self.slider.label.set_text(f"nout = {int(i):0{self.lenlab}d}")

    # Update the plot
    self.fig.canvas.draw()

    # End of the function
    return None

def _update_both(self, i):
    """
    Updates both the plot and the slider value during animation.

    Returns
    -------

    - None

        
    Parameters
    ----------
    - i (not optional): int
        The current frame index.

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: Update the data in the interactive plot

        >>> _update_slider(1)

    """

    # Update the plot with the current frame
    self._update_slider(i)
    
    # Update the slider's position visually
    self.slider.set_val(i)

    # End of the function
    return None


def animate(self, 
            gifname = None, 
            frames = None, 
            interval=500, 
            updateslider = True):
    """
    Displays the animation interactively.
    
    Returns
    -------

    - None

    Parameters
    ----------

    - frames: int, default None
        The number of frames in the animation.
    - gifname: str, default None
        The name of the GIF file.
    - interval: int, default 500 
        The interval between frames in milliseconds.
    - updateslider: bool, default True
        If True, the slider is shown and updated with each frame.

    Notes
    -----

    - This method creates and shows an interactive animation based on the stored data.

    Examples
    ========

    - Example #1: Display the animation

            >>> show_animation()

    - Example #2: Display the animation with a specific number of frames

            >>> show_animation(frames=[0, 1, 2], interval=300)

    """

    # Choose the frames
    frames = self.nsld if frames is None else frames

    update = self._update_both if updateslider else self._update_slider

    # Create the animation
    ani = animation.FuncAnimation(self.fig, update, 
                                  frames=frames, interval=interval)

    if gifname is not None:
        # Save as GIF
        ani.save(gifname)

        plt.close(self.fig)

    else:

        # Display the animation
        plt.show()