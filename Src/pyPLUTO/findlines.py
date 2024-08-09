from .libraries import *

def _check_var(self,var, transpose):
    if isinstance(var, str):
        try:
            var = getattr(self,var)
        except:
            print(f"Variable {var} not found in the dataset.")
            return None
    else:
        var = var
    if transpose is True:
        var = var.T
    return var

def vector_field(t, y, var1, var2, xc, yc):

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

    return [qx, qy]

def find_fieldlines(self,
               var1,
               var2, 
               x0 = None, 
               y0 = None, 
               **kwargs: Any
              ) -> list:
    
    # Get the variable, if it is a string, get the variable from the dataset.
    # The .T is used to transpose the variable to the correct shape.
    var1 = self._check_var(var1, kwargs.get('transpose', False))
    var2 = self._check_var(var2, kwargs.get('transpose', False))

    # Get the grid information
    xc = kwargs.get('x1',self.x1)
    yc = kwargs.get('x2',self.x2)

    # Get the footpoints
    if x0 is None or y0 is None:
        warnings.warn("Footpoints not provided, please provide the footpoints.")
        return None, None

    x0 = makelist(x0)
    y0 = makelist(y0)

    # Get the domain size (Take the initial and final coordinates
    # slightly larger to allow a seed to be specified on the boundary.
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

    step    = kwargs.get('step',min((xend - xbeg)/self.nx1,\
                                    (yend - ybeg)/self.nx2))
    
    maxstep = kwargs.get('maxstep',100*step)
    numstep = kwargs.get('maxsteps', 16384)
    tfin    = maxstep*numstep

    def system(t, y):
        return vector_field(t, y, var1, var2, xc, yc)
    
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
            print("EXIT")
            return 0
        self.oldpos = y
        return 1
    
    # Event to detect if the maximum number of steps is reached
    def max_num_steps(t, y):
        self.stepnum += 1
        if self.stepnum > numstep:
            return 0
        return 1
    
    close_to_start.terminal  = True if kwargs.get('close',True) is True else False
    close_to_start.direction = 0

    outside_domain.terminal = True
    outside_domain.direction = 0

    max_num_steps.terminal = True
    max_num_steps.direction = 0

    lines_list = []
    linekwargs = {}

    if order == 'LSODA':
        linekwargs['minstep'] = kwargs.get('minstep',0.05*step)


    for ind, xp in enumerate(x0):

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
        
        numstep = 0 if self.loop_dom is True else numstep
        self.init_pos = [sol_forward.y.T[:,0][-1], sol_forward.y.T[:,1][-1]]
        self.stepnum = 0
        t_span       = (0, -tfin)
        sol_backward = solve_ivp(system, t_span, [xp, yp], method = order,
                                         events=[outside_domain, max_num_steps,
                                                 close_to_start], rtol = rtol, 
                                         atol = atol, max_step = 0.1, 
                                         first_step = 0.1,
                                         dense_output = dense, **linekwargs)

        x_line = np.vstack((sol_backward.y.T[::-1],sol_forward.y.T))[:, 0]
        y_line = np.vstack((sol_backward.y.T[::-1],sol_forward.y.T))[:, 1]

        if self.loop_dom is True:
            x_line = np.append(x_line, x_line[0])
            y_line = np.append(y_line, y_line[0])

        print("Final integration time: ", sol_forward.t[-1])
        print("Final step number: ", self.stepnum)

        lines_list.append([x_line, y_line]) if len(x_line) > 1 else None

    for method_name in ['init_pos', 'stepnum', 'out_dom', 'oldpos']:
        if method_name in self.__class__.__dict__:
            delattr(self.__class__, method_name)

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
        List of lines. Each line is a list of two arrays containing the x and y
        coordinates of the line.

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

    Examples
    --------

    ...

    """

    # Get the variable, if it is a string, get the variable from the dataset.
    # The .T is used to transpose the variable to the correct shape.
    var = self._check_var(var, kwargs.get('transpose', False))
    
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