from .libraries import *
from typing import Optional, Union


def _is_number(value: Any
              ) -> bool:
    return isinstance(value, (int, float))

'''
def _islice_imin_imax(xvalue,xgrid):
    N = len(xgrid)
    i = np.argmin(abs(xgrid-xvalue))
    i_min = max(0, i - 2)
    i_max = min(N, i + 3)
    if N < 5:
        i_min, imax = 0, N
    else:
        if i_max == N:
            i_min = N-5
        if i_min == 0:
            i_max = 5
    return i-i_min, i_min, i_max

def _warning_cylindrical():
    warning_message = """
    CYLINDRICAL geometry has been deprecated since PLUTO v4.4.
    POLAR may be used instead by excluding the phi-direction
    (simply set INCLUDE_JDIR to NO in definitions.h).
    """
    warnings.warn(warning_message, DeprecationWarning, stacklevel=3)

def gradient(dat: Load,
             var: np.ndarray,
             x1slice: Optional[Union[float, int, None]] = None,
             x2slice: Optional[Union[float, int, None]] = None,
             x3slice: Optional[Union[float, int, None]] = None,
             edge_order: int = 2) -> np.ndarray:
    """
    Computes the gradient of a specified field 'var' in all available directions using
    second-order accurate central differences via the NumPy gradient() function.
    The first index of the resulting array represents the N gradient components.
    If 'x1slice', 'x2slice', or 'x3slice' are specified, the gradient is only computed
    at the corresponding x1, x2, or x3 values. N corresponds to the number of employed
    dimensions unless a slice is taken. 

    Parameters:
    dat : Load
        pyPLUTO.Load instance containing the grid information.
    var : numpy.ndarray
        The field whose gradient is calculated (e.g., 'rho', 'vx1'). Must have the
        same shape as dat.rho.
    x1slice : float or None, optional
        If not None, specifies the constant value for the x1 axis.
    x2slice : float or None, optional
        If not None, specifies the constant value for the x2 axis.
    x3slice : float or None, optional
        If not None, specifies the constant value for the x3 axis.
    edge_order : int, optional
        The order of accuracy of derivatives at the domain boundaries. Defaults to 2.

    Returns:
    numpy.ndarray
        Gradient of the input field 'var'. The shape of the array depends on the
        number of used spatial dimensions. E.g.:
        3D: (3, dat.nx1, dat.nx2, dat.nx3)
        3D, INCLUDE_JDIR == NO: (2, dat.nx1, dat.nx3)
        3D, x2slice = constant: (3, dat.nx1, dat.nx3)
    """

    if dat.geom == 'CYLINDRICAL':
        _warning_cylindrical()
    if _is_number(x1slice):
        i, imin, imax = _islice_imin_imax(x1slice,dat.x1)
        irange = slice(imin,imax)
    else:
        i = slice(0,dat.nx1)
        irange = i
        
    if _is_number(x2slice):
        j, jmin, jmax = _islice_imin_imax(x2slice,dat.x2)
        jrange = slice(jmin,jmax)
    else:
        j = slice(0,dat.nx2)
        jrange = j
        
    if _is_number(x3slice):
        k, kmin, kmax = _islice_imin_imax(x3slice,dat.x3)
        krange = slice(kmin,kmax)
    else:
        k = slice(0,dat.nx3)
        krange = k
    
    if dat.dim == 1:
        grad = np.gradient(var[irange],
                           dat.x1[irange],
                           edge_order=edge_order)
        return np.asarray(grad)[i]
    
    elif dat.dim == 2:
        grad = np.gradient(var[irange,jrange],
                           dat.x1[irange],
                           dat.x2[jrange],
                           edge_order=edge_order)

        if dat.geom in ['SPHERICAL', 'POLAR']:
            rr, _ = np.meshgrid(dat.x1[irange],
                                dat.x2[jrange],
                                indexing='ij')
            grad[1] /= rr
            
        return np.asarray(grad)[:,i,j]
    
    elif dat.dim == 3:
        if dat.nx2 == 1:
            grad = np.gradient(var[irange,0,krange],
                               dat.x1[irange],
                               dat.x3[krange],
                               edge_order=edge_order)

            if dat.geom == 'SPHERICAL':
                rr, _ = np.meshgrid(dat.x1[irange],
                                    dat.x3[krange],
                                    indexing='ij')
                grad[1] /= rr*np.sin(dat.x2[0])

            
            return np.asarray(grad)[:,i,k]
        
        else:
            grad = np.gradient(var[irange,jrange,krange],
                               dat.x1[irange],
                               dat.x2[jrange],
                               dat.x3[krange],
                               edge_order=edge_order)
        
            if dat.geom != 'CARTESIAN':
                xx1, xx2, _ = np.meshgrid(dat.x1[irange],
                                          dat.x2[jrange],
                                          dat.x3[krange],
                                          indexing='ij')
                grad[1] /= xx1
                if dat.geom == 'SPHERICAL':
                    grad[2] /= xx1*np.sin(xx2)

            return np.asarray(grad)[:,i,j,k]
        
def divergence(dat: Load,
               v1: Optional[Union[np.ndarray, None]] = None,
               v2: Optional[Union[np.ndarray, None]] = None,
               v3: Optional[Union[np.ndarray, None]] = None,
               x1slice: Optional[Union[float, int, None]] = None,
               x2slice: Optional[Union[float, int, None]] = None,
               x3slice: Optional[Union[float, int, None]] = None,
               edge_order: int = 2) -> np.ndarray:
    """
    Calculates the divergence of a vector field specified by its components v1, v2,
    and v3 using second-order accurate central differences via the NumPy gradient()
    function. If 'x1slice', 'x2slice', or 'x3slice' are specified, the divergence is
    only computed at the corresponding x1, x2, or x3 values.

    Parameters:
    dat : Load
        pyPLUTO.Load instance containing the grid information.
    v1, v2, v3 : numpy.ndarray or None, optional
        Fields corresponding to the vector components. Each must have the same shape
        as dat.rho. Can only be None if a given direction is not used. E.g., in 2D, v1
        and v2 must be specified. In 3D with INCLUDE_JDIR == NO, v1 and v3 must be
        specified.
    x1slice : float or None, optional
        If not None, specifies the constant value for the x1 axis.
    x2slice : float or None, optional
        If not None, specifies the constant value for the x2 axis.
    x3slice : float or None, optional
        If not None, specifies the constant value for the x3 axis.
    edge_order : int, optional
        The order of accuracy of derivatives at the domain boundaries. Defaults to 2.

    Returns:
    numpy.ndarray
        array corresponding to the divergence of the input vector field. In 3D, e.g.,
        its shape is (dat.nx1, dat.nx2, dat.nx3), while if INCLUDE_JDIR == NO (or if
        x2slice = constant), its shape is (dat.nx1, dat.nx3).
    """

    if dat.geom == 'CYLINDRICAL':
        _warning_cylindrical()
        
    if _is_number(x1slice):
        i, imin, imax = _islice_imin_imax(x1slice,dat.x1)
        irange = slice(imin,imax)
    else:
        i = slice(0,dat.nx1)
        irange = i
        
    if _is_number(x2slice):
        j, jmin, jmax = _islice_imin_imax(x2slice,dat.x2)
        jrange = slice(jmin,jmax)
    else:
        j = slice(0,dat.nx2)
        jrange = j
        
    if _is_number(x3slice):
        k, kmin, kmax = _islice_imin_imax(x3slice,dat.x3)
        krange = slice(kmin,kmax)
    else:
        k = slice(0,dat.nx3)
        krange = k

    if dat.dim == 1:
        var1 = v1[irange]

        rr = dat.x1[irange]

        if dat.geom in ['POLAR', 'CYLINDRICAL']:
            var1 *= rr
        elif dat.geom == 'SPHERICAL':
            var1 *= rr**2

        div1 = np.gradient(var1, rr, edge_order=edge_order)

        if dat.geom in ['POLAR', 'CYLINDRICAL']:
            div1 /= rr
        elif dat.geom == 'SPHERICAL':
            div1 /= rr**2
        
        return div1[i]
    
    elif dat.dim == 2:
        var1 = v1[irange,jrange]
        var2 = v2[irange,jrange]

        if dat.geom != 'CARTESIAN':
            rr, tt = np.meshgrid(dat.x1[irange],
                                 dat.x2[jrange],
                                 indexing='ij')
            
            if dat.geom in ['POLAR', 'CYLINDRICAL']:
                var1 *= rr
            elif dat.geom == 'SPHERICAL':
                var1 *= rr**2
                var2 *= np.sin(tt)

        div1 = np.gradient(var1,
                           dat.x1[irange],
                           axis=0,
                           edge_order=edge_order)
        div2 = np.gradient(var2,
                           dat.x2[jrange],
                           axis=1,
                           edge_order=edge_order)
        
        if dat.geom in ['POLAR', 'CYLINDRICAL']:
            div1 /= rr
            if dat.geom == 'POLAR':
                div2 /= rr
        elif dat.geom == 'SPHERICAL':
            div1 /= rr**2
            div2 /= rr*np.sin(tt)

        return div1[i,j] + div2[i,j]
    
    elif dat.dim == 3:

        if dat.nx2 == 1:
            var1 = v1[irange,0,krange]
            var3 = v3[irange,0,krange]
    
            if dat.geom != 'CARTESIAN':
                rr, _ = np.meshgrid(dat.x1[irange],
                                    dat.x3[krange],
                                    indexing='ij')
                
                if dat.geom == 'POLAR':
                    var1 *= rr
                elif dat.geom == 'SPHERICAL':
                    var1 *= rr**2

            div1 = np.gradient(var1,
                               dat.x1[irange],
                               axis=0,
                               edge_order=edge_order)
            div3 = np.gradient(var3,
                               dat.x3[krange],
                               axis=1,
                               edge_order=edge_order)
            
            if dat.geom == 'POLAR':
                div1 /= rr
            elif dat.geom == 'SPHERICAL':
                div1 /= rr**2
                div3 /= rr*np.sin(dat.x2[0])

            return div1[i,k] + div3[i,k]
        
        else:
            var1 = v1[irange,jrange,krange]
            var2 = v2[irange,jrange,krange]
            var3 = v3[irange,jrange,krange]

            if dat.geom != 'CARTESIAN':
                rr, tt, _ = np.meshgrid(dat.x1[irange],
                                        dat.x2[jrange],
                                        dat.x3[krange],
                                        indexing='ij')
                
                if dat.geom == 'POLAR':
                    var1 *= rr
                elif dat.geom == 'SPHERICAL':
                    var1 *= rr**2
                    var2 *= np.sin(tt)

            div1 = np.gradient(var1,
                               dat.x1[irange],
                               axis=0,
                               edge_order=edge_order)
            div2 = np.gradient(var2,
                               dat.x2[jrange],
                               axis=1,
                               edge_order=edge_order)
            div3 = np.gradient(var3,
                               dat.x3[krange],
                               axis=2,
                               edge_order=edge_order)
            
            if dat.geom == 'POLAR':
                div1 /= rr
                div2 /= rr
            elif dat.geom == 'SPHERICAL':
                div1 /= rr**2
                div2 /= rr*np.sin(tt)
                div3 /= rr*np.sin(tt)

            return div1[i,j,k] + div2[i,j,k] + div3[i,j,k]
        
def curl(dat: Load,
         v1: Optional[Union[np.ndarray, None]] = None,
         v2: Optional[Union[np.ndarray, None]] = None,
         v3: Optional[Union[np.ndarray, None]] = None,
         x1slice: Optional[Union[float, int, None]] = None,
         x2slice: Optional[Union[float, int, None]] = None,
         x3slice: Optional[Union[float, int, None]] = None,
         edge_order: int = 2) -> np.ndarray:
    """
    Calculates the curl of a specified vector field (v1, v2, v3) using second-order
    accurate central differences via the NumPy gradient() function. Unlike in divergence(),
    all three vector components must be specified. The resulting array has its first
    index representing the 3 curl components, while the remaining indices correspond to
    the grid location. If 'x1slice', 'x2slice', or 'x3slice' are specified, the curl is
    only computed at the corresponding x1, x2, or x3 values.

    Parameters:
    dat : Load
        pyPLUTO.Load instance containing the grid information.
    v1, v2, v3 : numpy.ndarray
        Fields corresponding to the vector components. Each must have the same shape
        as dat.rho.
    x1slice : float or None, optional
        If not None, specifies the constant value for the x1 axis.
    x2slice : float or None, optional
        If not None, specifies the constant value for the x2 axis.
    x3slice : float or None, optional
        If not None, specifies the constant value for the x3 axis.
    edge_order : int, optional
        The order of accuracy of derivatives at the domain boundaries. Defaults to 2.

    Returns:
    numpy.ndarray
        Curl of the specified vector field (v1, v2, v3). In 3D, e.g., its shape is
        (3, dat.nx1, dat.nx2, dat.nx3), while if INCLUDE_JDIR == NO (or if x2slice
        = constant), its shape is (3, dat.nx1, dat.nx3).
    """

    if dat.geom == 'CYLINDRICAL':
        _warning_cylindrical()

    if _is_number(x1slice):
        i, imin, imax = _islice_imin_imax(x1slice,dat.x1)
        irange = slice(imin,imax)
    else:
        i = slice(0,dat.nx1)
        irange = i
        
    if _is_number(x2slice):
        j, jmin, jmax = _islice_imin_imax(x2slice,dat.x2)
        jrange = slice(jmin,jmax)
    else:
        j = slice(0,dat.nx2)
        jrange = j
        
    if _is_number(x3slice):
        k, kmin, kmax = _islice_imin_imax(x3slice,dat.x3)
        krange = slice(kmin,kmax)
    else:
        k = slice(0,dat.nx3)
        krange = k

    if dat.dim == 1:
        raise ValueError('curl() requires DIMENSION >= 2')
    
    elif dat.dim == 2:
        var1 = v1[irange,jrange]
        var2 = v2[irange,jrange]
        var3 = v3[irange,jrange]

        if dat.geom != 'CARTESIAN':
            rr, tt = np.meshgrid(dat.x1[irange],
                                 dat.x2[jrange],
                                 indexing='ij')
            
            
            if dat.geom == 'POLAR':
                var2 *= rr
            elif dat.geom in 'CYLINDRICAL':
                var3 *= rr
            elif dat.geom == 'SPHERICAL':
                var2 *= rr
                var3 *= rr*np.sin(tt)

        dv1_dx2 = np.gradient(var1, dat.x2, axis=1,
                              edge_order=edge_order)
        dv2_dx1 = np.gradient(var2, dat.x1, axis=0,
                              edge_order=edge_order)
        dv3_dx1, dv3_dx2 = np.gradient(var3, dat.x1, dat.x2,
                                       edge_order=edge_order)

        curl1 = dv3_dx2
        curl2 = - dv3_dx1
        curl3 = dv2_dx1 - dv1_dx2
        if dat.geom == 'CYLINDRICAL':
            curl1 *= -1
            curl2 *= -1
            curl3 *= -1
        
        if dat.geom == 'POLAR':
            curl1 /= rr
            curl3 /= rr
        elif dat.geom == 'CYLINDRICAL':
            curl1 /= rr
            curl2 /= rr
        elif dat.geom == 'SPHERICAL':
            curl1 /= rr**2*np.sin(tt)
            curl2 /= rr*np.sin(tt)
            curl3 /= rr

        return np.asarray([curl1[i,j],curl2[i,j],curl3[i,j]])
    
    elif dat.dim == 3:

        if dat.nx2 == 1:
            var1 = v1[irange,0,krange]
            var2 = v2[irange,0,krange]
            var3 = v3[irange,0,krange]
    
            if dat.geom != 'CARTESIAN':
                rr, _ = np.meshgrid(dat.x1[irange],
                                    dat.x3[krange],
                                    indexing='ij')
                
                if dat.geom == 'POLAR':
                    var2 *= rr
                elif dat.geom == 'SPHERICAL':
                    var2 *= rr
                    var3 *= rr*np.sin(dat.x2[0])

            dv1_dx3 = np.gradient(var1, dat.x3, axis=1,
                                  edge_order=edge_order)
            dv2_dx1, dv2_dx3 = np.gradient(var2, dat.x1, dat.x3,
                                           edge_order=edge_order)
            dv3_dx1 = np.gradient(var3, dat.x1, axis=0,
                                  edge_order=edge_order)

            curl1 = - dv2_dx3
            curl2 = dv1_dx3 - dv3_dx1
            curl3 = dv2_dx1
            
            if dat.geom == 'POLAR':
                curl1 /= rr
                curl3 /= rr
            elif dat.geom == 'SPHERICAL':
                curl1 /= rr**2*np.sin(dat.x2[0])
                curl2 /= rr*np.sin(dat.x2[0])
                curl3 /= rr

            return np.asarray([curl1[i,k],curl2[i,k],curl3[i,k]])
        
        else:
            var1 = v1[irange,jrange,krange]
            var2 = v2[irange,jrange,krange]
            var3 = v3[irange,jrange,krange]

            if dat.geom != 'CARTESIAN':
                rr, tt, _ = np.meshgrid(dat.x1[irange],
                                        dat.x2[jrange],
                                        dat.x3[krange],
                                        indexing='ij')
                
                if dat.geom == 'POLAR':
                    var2 *= rr
                elif dat.geom == 'SPHERICAL':
                    var2 *= rr
                    var3 *= rr*np.sin(tt)

            dv1_dx2, dv1_dx3 = np.gradient(var1, dat.x2, dat.x3,
                                           axis=[1,2],
                                           edge_order=edge_order)
            dv2_dx1, dv2_dx3 = np.gradient(var2, dat.x1, dat.x3,
                                           axis=[0,2],
                                           edge_order=edge_order)
            dv3_dx1, dv3_dx2 = np.gradient(var3, dat.x1, dat.x2,
                                           axis=[0,1],
                                           edge_order=edge_order)

            curl1 = dv3_dx2 - dv2_dx3
            curl2 = dv1_dx3 - dv3_dx1
            curl3 = dv2_dx1 - dv1_dx2
            
            if dat.geom == 'POLAR':
                curl1 /= rr
                curl3 /= rr
            elif dat.geom == 'SPHERICAL':
                curl1 /= rr**2*np.sin(tt)
                curl2 /= rr*np.sin(tt)
                curl3 /= rr

            return np.asarray([curl1[i,j,k],curl2[i,j,k],curl3[i,j,k]])
'''