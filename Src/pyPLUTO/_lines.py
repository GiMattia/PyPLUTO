from ._libraries import *

def fieldlines(self,var1, var2, x0 = None, y0 = None, **kwargs):
    '''
    Fieldlines function (WIP)
    '''

    lines = []

    xc = kwargs.get('x1',self.Grid['x1'])
    yc = kwargs.get('x2',self.Grid['x2'])
    if x0 == None or y0 == None:
        print('Do not get here, please specify the footpoints for now. Work in progress...')
        return None, None
    if not isinstance(x0, list):
        x0 = [x0]
    if not isinstance(y0, list):
        y0 = [y0]

    # Get domain size (Take the initial and final coordinates
    # slightly larger to allow a seed to be specified on the boundary.

    xbeg = xc[0]  - 0.51*(xc[1]  - xc[0])
    xend = xc[-1] + 0.51*(xc[-1] - xc[-2])

    ybeg = yc[0]  - 0.51*(yc[1]  - yc[0])
    yend = yc[-1] + 0.51*(yc[-1] - yc[-2])

    # Normalize vectors to 1, only direction can change

    norm = 1/np.sqrt(var1*var1 + var2*var2 + 1.e-18)
    var1 = var1*norm
    var2 = var2*norm

    # Set keywords
    maxsteps = 16384
    maxfail  = 1024

    tol     = kwargs.get('tol', 1.e-6)
    cl_tol  = kwargs.get('cl_tol', 1.e-4)
    order   = kwargs.get('order','RK2')
    step    = kwargs.get('step',min((xend - xbeg)/len(xc),(yend - ybeg)/len(yc)))
    maxstep = 100*step
    minstep = 0.05*step

    for ind, xpos in enumerate(x0):
        lines.append(None)
        xline = []
        yline = []
        ypos = y0[ind]
        xclose = xpos
        yclose = ypos
        inside_domain = xpos > xbeg and xpos < xend and ypos > ybeg and ypos < yend
        isclosed = False
        if not inside_domain:
            print("Footpoint outside the domain!!")
            return None
        for s in [-1,1]:
            xl, yl = [xpos], [ypos]
            dh    = 0.02*s*step
            k     = 0
            kfail = 0
            while inside_domain and k < maxsteps - 1:
                #dh = s*min([np.abs(dh), maxstep])
                #dh = s*max([np.abs(dh), minstep])

                dh, xup, yup = self.adv_field_line(var1,var2,xc,yc,xl[-1],yl[-1],order,dh)
                xl.append(xup)
                yl.append(yup)
                k = k + 1
                isclosed = self.check_closed_line(xl[-1], yl[-1], xclose, yclose, cl_tol, k)
                if isclosed is True:
                    break
            if s == -1:
                xline = xline + xl[::-1]
                yline = yline + yl[::-1]
            else:
                xline = xline + xl[1:]
                yline = yline + yl[1:]
            xclose = xline[0]
            yclose = yline[0]
            if isclosed is True:
                break

        lines[ind] = [xline, yline]
    return lines

def field_interp(self,var1,var2,xc,yc,xp,yp):
    q = []
    U = var1
    V = var2
    i0 = np.abs(xp - xc).argmin()
    j0 = np.abs(yp - yc).argmin()
    scrhUx = np.interp(xp, xc, U[:, j0])
    scrhUy = np.interp(yp, yc, U[i0, :])
    q.append(scrhUx + scrhUy - U[i0, j0])
    scrhVx = np.interp(xp, xc, V[:, j0])
    scrhVy = np.interp(yp, yc, V[i0, :])
    q.append(scrhVx + scrhVy - V[i0, j0])
    return q

def adv_field_line(self,var1,var2,xc,yc,xl,yl,order,dh):
    if order == 'RK2':
        k1   = self.field_interp(var1, var2, xc, yc, xl, yl)
        xk1  = xl + 0.5*dh*k1[0]
        yk1  = yl + 0.5*dh*k1[1]

        k2   = self.field_interp(var1, var2, xc, yc, xk1, yk1)
        xres = xl + 0.5*dh*k2[0]
        yres = yl + 0.5*dh*k2[1]
    if order == 'RK4':
        k1   = self.field_interp(var1, var2, xc, yc, xl, yl)
        xk1  = xl + 0.5*dh*k1[0]
        yk1  = yl + 0.5*dh*k1[1]

        k2   = self.field_interp(var1, var2, xc, yc, xk1, yk1)
        xk1  = xl + 0.5*dh*k2[0]
        yk1  = yl + 0.5*dh*k2[1]

        k3 = self.field_interp(var1, var2, xc, yc, xk1, yk1)
        xk1  = xl + dh*k3[0]
        yk1  = yl + dh*k3[1]

        k4 = self.field_interp(var1, var2, xc, yc, xk1, yk1)
        xres = xl + dh*(k1[0] + 2.0*(k2[0] + k3[0]) + k4[0])/6.0
        yres = yl + dh*(k1[1] + 2.0*(k2[1] + k3[1]) + k4[1])/6.0
    if order == 'RK32' or order == 'RK23':
        print(order + ' not available yet!')
        quit()
    if order == 'RK54' or order == 'RK45':
        print(order + ' not available yet!')
        quit()
    return dh, xres,yres

def check_closed_line(self,xf,yf,xi,yi,tol, k):
    if np.sqrt((xf - xi)**2 + (yf - yi)**2) < tol and k > 1:
        return True
    else:
        return False

def contour_lines(self,**kwargs):
    fig_contour = plt.figure()
    ax_contour = fig_contour.add_subplot()

    xc = kwargs.get('x1',self.Grid['x1'])
    yc = kwargs.get('x2',self.Grid['x2'])


    return None