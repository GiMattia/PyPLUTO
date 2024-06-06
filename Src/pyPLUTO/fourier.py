import numpy as np
import pyPLUTO as pp
import matplotlib.pyplot as plt

def FourierTransform1D(f, dxi):
    """
    Calcola la trasformata di Fourier di un segnale f.
    
    Parameters
    ----------

    - f : numpy array, il segnale di input
    - dx: float, l'intervallo di campionamento (passo)
    
    Returns
    -------
    
    - k : numpy array, l'array delle frequenze
    - fk: numpy array, la trasformata di Fourier del segnale
    """
    # Calcola la lunghezza del segnale
    N = len(f)
    
    # Calcola la trasformata di Fourier del segnale
    fk = np.fft.fftn(f)
    
    # Calcola le frequenze corrispondenti ai coefficienti della trasformata
    k = np.fft.rfftfreq(N, dxi)
    
    return 2*np.pi*k, np.abs(fk[:N//2+1])

def FourierTransform2D(f, dx, dy):
    """
    Calcola la trasformata di Fourier di un segnale f.
    
    Args:
    - f: numpy array, il segnale di input
    - dx: float, l'intervallo di campionamento in x (passo)
    - dy: float, l'intervallo di campionamento in y (passo)
    
    Returns:
    - kx: numpy array, l'array delle frequenze in x
    - ky: numpy array, l'array delle frequenze in y
    - fk: numpy array, la trasformata di Fourier del segnale
    """
    # Calcola la lunghezza del segnale
    Nx, Ny = f.shape

    print("Nx: ", Nx)
    print("Ny: ", Ny)
    print("f = ", f.shape)
    
    # # Calcola la trasformata di Fourier del segnale
    fk = np.fft.fftn(f)
    
    # Calcola le frequenze corrispondenti ai coefficienti della trasformata
    kx = np.fft.rfftfreq(Nx, dx)
    ky = np.fft.rfftfreq(Ny, dy)
    print("kx, ky = ", kx.shape, ky.shape)
    
    return 2*np.pi*kx, 2*np.pi*ky, np.abs(fk[:Nx//2+1,:Ny//2+1])

def FourierTransform(f, *dx):
    """
    Calcola la trasformata di Fourier di un segnale f.

    Args:
    - f: numpy array, il segnale di input
    - *dx: float, l'intervallo di campionamento (passo) 
       per ciascuna dimensione (può essere uno o due valori)

    Returns:
    - k: numpy array, l'array delle frequenze in x 
      o in uno spazio a dimensioni superiori
    - fk: numpy array, la trasformata di Fourier del segnale
    """
    # Controlla le dimensioni del segnale di input
    dim = f.ndim

    # Calcola la trasformata di Fourier del segnale
    fk = np.fft.fftn(f)

    # In base alle dimensioni del segnale, calcola le frequenze corrispondenti
    if dim == 1:
        k = np.fft.rfftfreq(len(f), dx[0])
        return 2*np.pi*k, np.abs(fk[:len(f)//2 + 1])
    elif dim == 2:
        Ny, Nz = f.shape
        ky = np.fft.rfftfreq(Ny, dx[0])
        kz = np.fft.rfftfreq(Nz, dx[1])
        return 2*np.pi*ky, 2*np.pi*kz, np.abs(fk[:Ny//2 + 1, :Nz//2 + 1])
    else:  # Caso 3D con fissaggio della coordinata x
        nx, ny, nz = f.shape
        ky = np.fft.fftfreq(ny, dx[0])
        kz = np.fft.fftfreq(nz, dx[1])
        return 2 * np.pi * ky, 2 * np.pi * kz, np.abs(fk[:, :ny // 2 + 1, :nz // 2 + 1])


# Set the plot parameters
datapath='3D_Data/'
nalg = [datapath+'128/', datapath+'256/', datapath+'512/']  # List of directories
nsol = ['Bx1']
ncol = len(nalg) + 1        # Number of columns
nrow = len(nsol)            # Number of rows
alg  = ['128','256','512']  # Label
eps  = 1e-14

# Create image and axes
I = pp.Image(figsize = [11.2,8.2], fontsize = 20, LaTeX = True)
ax = I.create_axes(ncol = ncol, nrow = nrow, wratio = [1.0, 1.0, 1.0, 0.12], 
                    wspace = [0.005]*(ncol), hspace = [0.005]*(nrow), left = 0.1)

# # # Set the axes parameters
I.set_axis(ax[0], xtitle = '$ny$', ytitle = '$|fk|$')
I.set_axis(ax[1], xtitle = '$ny$', ytickslabels = None)
I.set_axis(ax[2], xtitle = '$ny$', ytickslabels = None)

def PlotData1D():    
    # Iterate on the numerical algorithms
    for i, algt in enumerate(nalg):

        # Compute the plot number
        nplot = i

        # Load the data
        D = pp.Load(0, path =algt, datatype = 'vtk', text = False)
        
        # Compute Fourier Transform
        dx = D.dx1[0]
        dy = D.dx2[0]
        Nx, Ny = D.Bx1.shape
        Ky = []
        Fk = []

        for i in range(Nx):
            ky, fk = FourierTransform(D.Bx1[i], dy)
            Ky.append(ky)
            Fk.append(fk)

        Ky = np.array(Ky)
        Fk = np.array(Fk)

        # Display the data
        I.plot(np.log10((Fk[0]+eps)**2), x1 = np.abs(Ky[0]), ax = ax[nplot], cmap = 'RdYlBu_r')

    pp.show()

def PlotData2D():

    # Create image and axes
    I = pp.Image(figsize = [11.2,8.2], fontsize = 20, LaTeX = True)
    ax = I.create_axes(ncol = ncol, nrow = nrow, wratio = [1.0, 1.0, 1.0, 0.12], 
                       wspace = [0.005]*(ncol), hspace = [0.005]*(nrow), left = 0.1)

    # # # Set the axes parameters
    I.set_axis(ax[0], xtitle = '$ny$', ytitle = '$nz$')
    I.set_axis(ax[1], xtitle = '$ny$', ytickslabels = None)
    I.set_axis(ax[2], xtitle = '$ny$', ytickslabels = None)

    # Iterate on the numerical algorithms
    for i, algt in enumerate(nalg):

        # Compute the plot number
        nplot = i

        # Load the data
        D = pp.Load(5, path =algt, datatype = 'vtk', text = False)
        
        # Compute Fourier Transform
        dx = D.dx1[0]
        dy = D.dx2[0]
        dz = D.dx3[0]
        Nx, Ny, Nz = D.Bx1.shape
        Ky = []
        Kz = []
        Fk = []

        for i in range(Nx):
            ky, kz, fk = FourierTransform(D.Bx1[i], dy, dz)
            Ky.append(ky)
            Kz.append(kz)
            Fk.append(fk)

        Ky = np.array(Ky)
        Kz = np.array(Kz)
        Fk = np.array(Fk)

        # Display the data
        I.display(np.log10((Fk[0]+eps)**2), x1 = np.abs(Ky[0]), x2 = np.abs(Kz[0]), ax = ax[nplot], cmap = 'RdYlBu_r') #, aspect = 'equal')


    # Place the colorbar
    I.text(r"$|fk|$", 0.96,0.48, xycoords = 'figure')
    I.colorbar(axs = ax[0], cax = ax[3])
    pp.show()

# Genera dati 1D di esempio 
def Example1D():
    Nx = 2048
    x = np.linspace(0.0, 1.0, Nx)
    dx = x[1] - x[0]
    twopi = 2.0 * np.pi * x
    f = 5.0 * np.sin(twopi) + 2.0 * np.sin(10.0 * twopi + 5.0) + np.cos(30.0 * twopi)

    # Calcola la trasformata di Fourier del segnale
    k, fk = FourierTransform1D(f, dx)

    # Plot del modulo della trasformata di Fourier
    plt.plot(k, np.abs(fk))
    plt.xlabel('k')
    plt.ylabel('|fk|')
    plt.title('Trasformata di Fourier del segnale 1D di test')
    plt.show()

# Genera dati 2D di esempio
def Example2D():
    Nx = 200
    Ny = 100
    x = np.linspace(0.0, 1.0, Nx)
    y = np.linspace(0.0, 1.0, Ny)
    dx = x[1]-x[0]
    dy = y[1]-y[0]
    X, Y = np.meshgrid(x, y, indexing='ij')
    f = np.abs(np.sin(25.0*np.pi*X)*np.sin(101.0*np.pi*Y)) + np.random.uniform(0, 1, X.shape)
    f0 = np.cos(42.0*Y)*np.sin(78.0*X) + np.cos(55.0*Y)*np.sin(101.0*X) + np.random.uniform(0, 1, X.shape)

    kx, ky, fk = FourierTransform2D(f, dx, dy)
    Kx, Ky = np.meshgrid(kx, ky, indexing='ij')

    print("fk = ", fk.shape)
    print("Max = ", np.max(np.abs(fk)))
    print("Min = ", np.min(np.abs(fk)))

    plt.figure(figsize=(8, 6))
    plt.pcolormesh(kx, ky, np.log10(np.abs(fk.T)**2), cmap='plasma')
    plt.colorbar(label='|fk|')
    plt.title('Trasformata di Fourier del segnale 2D di test')
    plt.xlabel('Kx')
    plt.ylabel('Ky')
    plt.show()


PlotData2D()


