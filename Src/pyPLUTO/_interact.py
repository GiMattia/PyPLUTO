from ._libraries import *

def interactive(self, varx, vary = None, fig = None, **kwargs):

    # Store the variable
    if vary is None:
        vary = varx
        splt = np.ndim(varx[0])
        if splt == 1:
            varx = np.arange(len(vary))

    self.anim_var = vary
    nsld = len(vary) - 1
    splt = np.ndim(vary[0])

    # Set or create figure and axes (to test)
    ax, nax = self.assign_ax(kwargs.pop('ax', None), **kwargs, tight = False)
    self.anim_ax  = ax

    # Position the slider
    pos_slider = ax.get_position()
    pos_x0 = pos_slider.x0*1.5
    pos_x1 = pos_slider.x1*0.95 - pos_x0
    sliderax = self.fig.add_axes([pos_x0, 0.02, pos_x1, 0.04])

    # Create the slider
    self.slider = Slider(sliderax,label="out", valmin=0, valmax=nsld, valinit = 0, valstep = 1, valfmt = '%d')
    self.slider.on_changed(self.update_slider)

    # Display the data
    if splt == 2:
        self.display(self.anim_var[0], ax = ax,  **kwargs)
        self.anim_pcm = ax.collections[0]
    else:
        self.plot(varx,np.array(vary[0].tolist()), ax = ax, **kwargs)
        self.anim_pcm =  ax.get_lines()[0]

    return None

def update_slider(self, i):
    var = self.anim_var[int(i)]
    if np.ndim(var) == 2:
        self.anim_pcm.set_array(var.T.ravel())
    elif np.ndim(var) == 1:
        self.anim_pcm.set_ydata(var)
    self.fig.canvas.draw()
