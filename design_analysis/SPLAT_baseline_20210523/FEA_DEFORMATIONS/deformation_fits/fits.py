import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from numpy.polynomial.polynomial import polyval2d
import sys
import seaborn as sns

show = False

columns = ["Node", "Value_mm", "x_mm", "y_mm", 'z_mm', "Components"]

fname = 'data/FEA_Mirror1S_WithCone2-M1S_El00Pa00c-DisplZ-1.txt'
df = pd.read_csv(fname,
                 delim_whitespace=True,
                 skiprows=8,
                 names=columns,
                 encoding='latin-1')

x, y, z = df.x_mm.values, df.y_mm.values, df.Value_mm.values


def plane(x, y, A):
    z = A[0] * x + A[1] * y + A[2]
    return z


def nterms(degree):
    '''returns the number of terms for a given order polynomial.'''
    if degree % 2 == 0:
        return int((degree + 1) * (degree/2 + 1))
    elif degree % 2 == 1:
        return int((degree + 1) * ((degree-1)/2 + 1))


def polynomial_matrix(A, degree):
    assert len(A) == nterms(degree)
    c = np.zeros([degree + 1, degree + 1])
    nit = int(len(A) / (degree + 1))
    for j in range(nit):
        c[j*2, :] = A[(degree + 1) * j: (degree + 1) * (j + 1)]
    return c


def error_polynomial_of_degree(A, x, y, z, degree):
    c = polynomial_matrix(A, degree)
    z_theo = polynomial(x, y, c)
    err = (z_theo - z)**2
    return np.sqrt(np.sum(err))


def polynomial(x, y, c):
    Rx = 2500.0
    Ry = 2500.0
    x_norm = x/Rx
    y_norm = y/Ry
    z = polyval2d(x_norm, y_norm, c)
    return z


def error_polynomial_reduced_8(A, x, y, z):
    c = np.zeros([4, 4])
    c[0, :] = A[0:4]
    c[2, :] = A[4:8]
    z_theo = polynomial(x, y, c)
    err = (z_theo - z)**2
    return np.sqrt(np.sum(err))


def error_polynomial_reduced_18(A, x, y, z):
    c = np.zeros([6, 6])
    c[0] = A[0:6]
    c[2] = A[6:12]
    c[4] = A[12:18]
    z_theo = polynomial(x, y, c)
    err = (z_theo - z)**2
    return np.sqrt(np.sum(err))


def error_polynomial(A, x, y, z):
    c = A.reshape([4, 4])
    z_theo = polynomial(x, y, c)
    err = (z_theo - z)**2
    return np.sqrt(np.sum(err))


def error_plane(A, x, y, z):
    z_theo = plane(x, y, A)
    err = (z_theo - z)**2
    return np.sqrt(np.sum(err))


A0 = [0, 5e-5, 0.07]
opt = minimize(error_plane, A0, (x, y, z), method='Nelder-Mead')
A_opt = opt.x

z_theo = plane(x, y, A_opt)
dz = z - z_theo

# Fits
degree = int(sys.argv[1])
print("degree %i" % degree)
A_poly = np.zeros(nterms(degree))
sol = minimize(error_polynomial_of_degree, A_poly, (x, y, dz, degree),
               method='CG')
A_sol = sol.x
c = polynomial_matrix(A_sol, degree)

z_model = polynomial(x, y, c)
residual = dz - z_model

# plot fit and data
fig, axs = plt.subplots(2, 2, figsize=[7, 7])
ax = axs[0, 0]
pcm = ax.hexbin(x, y, dz * 1000)
ax.set_title('Deformation rms: %1.2f $\\mu m$' % (np.std(dz) * 1000))
fig.colorbar(pcm, ax=ax)

ax = axs[0, 1]
pcm = ax.hexbin(x, y, z_model * 1000)
fig.colorbar(pcm, ax=ax)
ax.set_yticklabels([])
ax.set_xticklabels([])
ax.set_title('model deg=%i, rms:%1.2f $\\mu m$' % (degree,
                                                   np.std(z_model)*1000))

ax = axs[1, 0]
sns.heatmap(c, annot=True, ax=ax, fmt="1.1e",
            cbar=False, annot_kws={"size": 6})


ax = axs[1, 1]
pcm = ax.hexbin(x, y, residual*1000)
fig.colorbar(pcm, ax=ax)
ax.set_title('residual, rms:%1.2f $\\mu m$' % (np.std(residual) * 1000))

ax = axs[1, 0]
ax.axis('off')

if show:
    plt.show()
else:
    plt.savefig('fit_model_residuals_degree_%i.pdf' % degree)
    plt.savefig('fit_model_residuals_degree_%i.png' % degree)
    plt.close()

np.savez('./model_parameters_deg_%i.npz' % degree,
         A=A_sol, degree=degree)
