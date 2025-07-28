import numpy as np
import matplotlib.pyplot as plt

def curved_mandelbrot(width=800, height=800, max_iter=100, k=0.5):
    x = np.linspace(-2, 1, width)
    y = np.linspace(-1.5, 1.5, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    
    # Warp coordinates
    U = X + k * np.cos(Y * np.pi)
    V = Y + k * np.sin(X * np.pi)
    C = U + 1j * V
    
    # Mandelbrot iteration
    M = np.zeros_like(C, dtype=int)
    Z_iter = np.zeros_like(C, dtype=complex)
    
    for i in range(max_iter):
        mask = np.abs(Z_iter) < 2
        Z_iter[mask] = Z_iter[mask] ** 2 + C[mask]
        M[mask] = i
    
    plt.imshow(M, cmap='magma', extent=(-2, 1, -1.5, 1.5))
    plt.title(f'Curved Mandelbrot (k={k})')
    plt.colorbar()
    plt.show()

curved_mandelbrot(k=0.3)
