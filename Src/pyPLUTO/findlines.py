from .libraries import *

def _check_var(self,
               var: str | NDArray,
               transpose: bool
             ):
    """
    Function that checks returns a variable. If the variable is a numpy array,
    it is simply returned (and the transpose is taken into account). If the 
    variable is a string, the variable is retrieved from the dataset. If the 
    variable is not found, an error is raised.

    Returns
    -------

    - var: NDArray
        The variable.

    Parameters
    ----------

    - var: str | NDArray
        The variable to be checked.
    - transpose: bool
        If True, the variable is transposed.

    Notes
    -----

    - None

    ----

    ========
    Examples
    ========

    - Example #1: var is a numpy array

        >>> var = np.array([1,2,3])
        >>> _check_var(var, False)
        array([1, 2, 3])

    - Example #2: var is a string

        >>> D = pp.Load()
        >>> _check_var("Bx1", False)
    
    """
    if isinstance(var, str):
        try:
            var = getattr(self,var)
        except:
            raise ValueError(f"Variable {var} not found in the dataset.")
    if transpose is True:
        var = var.T
    return var


def vector_field(t, y, var1, var2, xc, yc):
    """
    Compute the vector field at the given time and coordinates by interpolating
    the variables var1 and var2 at the given coordinates.

    Returns
    -------

    - qx, qy: NDArray
        The vector field components.

    Parameters
    ----------

    - t: float
        The time variable (not used here).
    - y: NDArray
        The coordinates. The first and second dimension are x and y.
    - var1: NDArray
        The first variable to be interpolated.
    - var2: NDArray
        The second variable to be interpolated.
    - xc: NDArray
        The x coordinates of the grid.
    - yc: NDArray
        The y coordinates of the grid.

    Notes
    -----

    - None

    ----

    ========
    Examples
    ========

    - Example #1: Compute the vector field at the given time and coordinates

        >>> vector_field(t, y, var1, var2, xc, yc)

    """

    # Get the coordinates
    x, y = y

    # Compute indices for closest grid points in xc and yc
    i0 = np.abs(x - xc).argmin()
    j0 = np.abs(y - yc).argmin()

    # Interpolate U and V at the given coordinates
    scrhUx = np.interp(x, xc, var1[:, j0])
    scrhUy = np.interp(y, yc, var1[i0])
    scrhVx = np.interp(x, xc, var2[:, j0])
    scrhVy = np.interp(y, yc, var2[i0])

    # Compute the resulting vector field components
    qx = scrhUx + scrhUy - var1[i0, j0]
    qy = scrhVx + scrhVy - var2[i0, j0]

    # Return the vector field
    return [qx, qy]

def find_fieldlines(self,
               var1,
               var2, 
               x0 = None, 
               y0 = None, 
               text = False,
               **kwargs: Any
              ) -> list:
    """
    Find field lines using the vector field. The field lines are computed by
    interpolating the variables var1 and var2 at the footpoints x0 and y0.
    Different integration algorithms are available, based on the method
    solve_ivp of the scipy package.

    Returns
    -------

    - linelist: list
        A list of lists containing the coordinates of the field lines.
        The strcuture of the list is [[x1, y1], [x2, y2], ...] where
        x1, y1, x2, y2 are numpy arrays representing the coordinates of
        the field lines.

    Parameters
    ----------

    - atol: float, default 1e-6
        The absolute tolerance for the integration.
    - close: bool, default True
        If True, it checks if the line is closed on itself.
    - ctol: float, default 1e-6
        The absolute tolerance for line closing on itself.
    - dense: bool, default False
        If True, the grid is dense (dense=True) or sparse (dense=False).
    - maxstep: float, default 100*step
        The maximum step size for the integration.
    - minstep: float, default 0.05*step
        The minimum step size for the integration (only used if order is LSODA).
    - numsteps: int, default 16384
        The maximum number of steps for the integration.
    - order: str, default 'RK45'
        The integration method. Available options are: 'RK45', 'RK23', 'DOP853',
        'Radau', 'BDF', 'LSODA'.
    - rtol: float, default 1e-6
        The relative tolerance for the integration.
    - step: float, default min((xend - xbeg)/self.nx1, (yend - ybeg)/self.nx2)
        The initial step size for the integration.
    - text: bool, default False
        If True some additional information is printed.
    - transpose: bool, default False
        If True, the variables are transposed.
    - var1: str | NDArray
        The first variable to be interpolated.
    - var2: str | NDArray
        The second variable to be interpolated.
    - x0: list
        The x coordinates of the footpoints.
    - x1: NDArray | list | None, default self.x1
        The x coordinates of the grid.
    - x2: NDArray | list | None, default self.x2
        The y coordinates of the grid.
    - y0: list
        The y coordinates of the footpoints.

    ... (to be continued)

    Notes
    -----

    - None

    ----

    ========
    Examples
    ========

    - Example #1: Find field lines using the vector field

        >>> find_fieldlines(var1, var2, x0, y0)

    - Example #2: Find field lines using two strings 'Bx1' and 'Bx2'

        >>> find_fieldlines('Bx1', 'Bx2', x0, y0)

    - Example #3: Find field lines using two variables and two footpoints

        >>> find_fieldlines(var1, var2, [x1, x2], [y1, y2])

    """
    
    # Get the variable, if it is a string, get the variable from the dataset.
    # The .T is used to transpose the variable to the correct shape.
    varx = self._check_var(var1, kwargs.get('transpose', False))
    vary = self._check_var(var2, kwargs.get('transpose', False))

    # Get the grid information
    xc = kwargs.get('x1',self.x1)
    yc = kwargs.get('x2',self.x2)

    # Check if the grid is uniform
    if not np.all(np.diff(xc) == np.diff(xc)[0]):
        err = "The grid is not uniform. Only uniform grids are supported."
        raise ValueError(err)

    # Get the footpoints
    if x0 is None or y0 is None:
        raise ValueError("Footpoints not provided.")

    # Make sure x0 and y0 are lists
    x0 = makelist(x0)
    y0 = makelist(y0)

    # Get the domain size (Take the initial and final coordinates
    # slightly larger to allow a seed to be specified on the boundary).
    xbeg = xc[0]  - 0.51*(xc[1]  - xc[0])
    xend = xc[-1] + 0.51*(xc[-1] - xc[-2])

    ybeg = yc[0]  - 0.51*(yc[1]  - yc[0])
    yend = yc[-1] + 0.51*(yc[-1] - yc[-2])

    # Set the keywords
    rtol  = kwargs.get('rtol', 1.e-3)
    atol  = kwargs.get('atol', 1.e-6)
    ctol  = kwargs.get('ctol', 1.e-6)
    order = kwargs.get('order','RK45')
    dense = kwargs.get('dense',False)

    # Set the initial step size and maximum number of steps
    step    = kwargs.get('step',min((xend - xbeg)/self.nx1,\
                                    (yend - ybeg)/self.nx2))
    
    maxstep = kwargs.get('maxstep',100*step)
    numstep = kwargs.get('maxsteps', 16384)
    tfin    = maxstep*numstep

    # Define the system of differential equations
    def system(t, y):
        return vector_field(t, y, varx, vary, xc, yc)
    
    # Event to detect if the field line exits the domain
    def outside_domain(t, y):
        
        if y[0] < xbeg or y[0] > xend or \
           y[1] < ybeg or y[1] > yend:
            return 0  # Trigger event (exiting the domain)
        return 1  # Do not trigger event (still within the domain)

    # Event to detect if the field line closes on itself
    def close_to_start(t, y):
        dist_0 = np.linalg.norm(y - np.asarray(self.init_pos))
        if dist_0 < ctol and t > maxstep:
            self.loop_dom = True
            return 0 # Trigger event (closing on itself)
        self.oldpos = y
        return 1 # Do not trigger event (open line)
    
    # Event to detect if the maximum number of steps is reached
    def max_num_steps(t, y):
        self.stepnum += 1
        if self.stepnum > numstep:
            return 0 # Trigger event (maximum number of steps reached)
        return 1 # Do not trigger event (still below maximum step number)
    

    # Set the events to be triggered
    close_to_start.terminal  = True if kwargs.get('close',True) is True \
                                    else False
    close_to_start.direction = 0

    outside_domain.terminal = True
    outside_domain.direction = 0

    max_num_steps.terminal = True
    max_num_steps.direction = 0

    # Initilaize the list of lines and set the keywords
    lines_list = []
    linekwargs = {}

    if order == 'LSODA':
        linekwargs['minstep'] = kwargs.get('minstep',0.05*step)

    # Iterate on the footpoints
    for ind, xp in enumerate(x0):

        # Set the initial conditions
        self.loop_dom  = False
        yp            = y0[ind]
        self.init_pos = [xp, yp]
        self.oldpos   = [xp, yp]
        self.stepnum  = 0
        t_span        = (0, tfin)

        # Integrate forward   
        sol_forward  = solve_ivp(system, t_span, [xp, yp], method = order,
                                         events=[outside_domain, max_num_steps,
                                                 close_to_start], rtol = rtol, 
                                         atol = atol, max_step = maxstep, 
                                         first_step = step,
                                         dense_output = dense, **linekwargs)
        
        # If the line did not close on itself, integrate backward
        numstep = 0 if self.loop_dom is True else numstep

        # Set the new conditions
        forw_steps    = self.stepnum
        self.init_pos = [sol_forward.y.T[:,0][-1], sol_forward.y.T[:,1][-1]]
        self.stepnum  = 0
        t_span        = (0, -tfin)

        # Integrate backward
        sol_backward = solve_ivp(system, t_span, [xp, yp], method = order,
                                         events=[outside_domain, max_num_steps,
                                                 close_to_start], rtol = rtol, 
                                         atol = atol, max_step = maxstep, 
                                         first_step = step,
                                         dense_output = dense, **linekwargs)

        # Concatenate the solutions (backward and forward)
        x_line = np.vstack((sol_backward.y.T[::-1],sol_forward.y.T))[:, 0]
        y_line = np.vstack((sol_backward.y.T[::-1],sol_forward.y.T))[:, 1]

        # If the line is closed on itself, close the line
        if self.loop_dom is True:
            x_line = np.append(x_line, x_line[0])
            y_line = np.append(y_line, y_line[0])

        # Print the time of the integration
        if text is True:
            print("Final integration time forward:  ", sol_forward.t[-1])
            print("Final integration time backward: ", sol_backward.t[-1])
            print("Final step number forward:       ", forw_steps)
            print("Final step number backward:      ", self.stepnum)

        # Add the line to the list (if it has more than one point)
        lines_list.append([x_line, y_line]) if len(x_line) > 1 else None

    # Delete the methods that are not needed
    for method_name in ['init_pos', 'stepnum', 'out_dom', 'oldpos']:
        if method_name in self.__class__.__dict__:
            delattr(self.__class__, method_name)

    # Return the list of lines
    return lines_list


def find_contour(self,
                 var: str | np.ndarray, 
                 **kwargs: Any
                ) -> list:
    """
    Generate contour lines for a given variable.
    ...

    Returns
    -------

    - lines_list : list
        List of contour lines. The strcuture of the list is 
        [[x1, y1], [x2, y2], ...] where x1, y1, x2, y2 are numpy arrays 
        representing the coordinates of the field lines.

    Parameters
    ----------

    - cmap : str, default None
        The colormap to use to associate each level with a color.
        The colormap can also be a color, which is used for all the levels.
        If not provided, all the lines are associated with the color black.
    - levels : int | array_like, default 10
        The levels of number of levels or the list of levels for the contours. 
        If an integer is provided, the levels are generated using a linear or
        logarithmic scale. If an array is provided, the levels are taken from
        the array.
    - levelscale : str, default 'linear'
        The scale of the levels. Available options are 'linear' and 
        'logarithmic'.
    - var : str | array_like
        The variable to plot. If a string is provided, the variable is taken 
        from the dataset.
    - vmax : float, default np.max(var)
        The maximum value of the variable.
    - vmin : float, default np.min(var)
        The minimum value of the variable.
    - x1 : array_like, default self.x1
        The x1 coordinates. If the geometry is non-Cartesian, the x1 cartesian 
        coordinates are taken from the dataset.
    - x2 : array_like, default self.x2
        The x2 coordinates. If the geometry is non-Cartesian, the x2 cartesian
        coordinates are taken from the dataset.
    
    Notes
    -----

    - None

    ----

    ========
    Examples
    ========

    - Example #1: Generate contour lines for a given variable.

    >>> lines_list = find_contour(var)

    - Example #2: Generate contour lines for a given variable and coordinates.

    >>> lines_list = find_contour(var, x1=x1, x2=x2)

    - Example #3: Generate contour lines for a given variable and coordinates
      with a logarithmic scale.

    >>> lines_list = find_contour(var, x1=x1, x2=x2, levelscale='logarithmic')

    - Example #4: Generate contour lines for a given variable and coordinates
      with a logarithmic scale and a colormap.

    >>> lines_list = find_contour(var, x1=x1, x2=x2, levelscale='logarithmic', 
    >>> ... cmap='jet')

    """

    # Get the variable, if it is a string, get the variable from the dataset.
    # The .T is used to transpose the variable to the correct shape.
    var = self._check_var(var, kwargs.get('transpose', False)).T
    
    # Get the grid information and provide a default value for the coordinates
    # if they are not provided depending on the geometry.
    if self.geom == "SPHERICAL":
        x1 = self.x1p
        x2 = self.x2p
    elif self.geom == "POLAR" and self.nx2 == 1:
        x1 = self.x1
        x2 = self.x3
    elif self.geom == "POLAR":
        x1 = self.x1c
        x2 = self.x2c
    else:
        x1 = self.x1
        x2 = self.x2
    
    # Get the coordinates from the keyword arguments (if provided)
    x1 = kwargs.get('x1',x1)
    x2 = kwargs.get('x2',x2)

    # Get the variable information (minimum and maximum values)
    vmin = kwargs.get('vmin',np.nanmin(var))
    vmax = kwargs.get('vmax',np.nanmax(var))


    # Compute the levels of the contours, in linear or logarithmic scale
    levels     = kwargs.get('levels',10)
    levelscale = kwargs.get('levelscale','linear')

    # If levels is an integer, the levels are computed in lin or log scale
    if isinstance(levels, int):
        levels = np.linspace(vmin,vmax,levels) if levelscale == 'linear' else \
                 np.logspace(np.log10(vmin),np.log10(vmax),levels)
        
    # If levels is a float, convert it to a list
    if isinstance(levels, float):
        levels = [levels]

    # Set colormap (try to get it from the colormap list, if not then use
    # the color provided), if not provided use black.
    if 'cmap' in kwargs:
        try:
            cmap = plt.get_cmap(kwargs.get('cmap'))
        except:
            cmap = mcol.ListedColormap(kwargs.get('cmap'))
    else:
        cmap = mcol.ListedColormap(['k'])


    # Initialize the list of lines
    lines_list = []

    # Get the contour generator and the lines for every level
    cont_gen = cp.contour_generator(x1, x2, var, name = 'serial')
    for indx, level in enumerate(levels):
        contour = cont_gen.lines(level)
        for line in contour:
            x_c = line[:, 0]
            y_c = line[:, 1]
            col = cmap(indx/(len(levels) - 1)) if 'cmap' in kwargs else 'k'

            lines_list.append([x_c, y_c, col]) if len(line) > 1 else None

    # Return the list of lines
    return lines_list