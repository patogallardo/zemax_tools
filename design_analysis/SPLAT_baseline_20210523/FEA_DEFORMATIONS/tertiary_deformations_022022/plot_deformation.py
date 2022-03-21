import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize


def plane(x, y, A):
    z = A[0] * x + A[1] * y + A[2]
    return z


def error_plane(A, x, y, z):
    z_theo = plane(x, y, A)
    err = (z_theo - z)**2
    return np.sqrt(np.sum(err))

df = pd.read_csv("FEA_Mirror3Ra_WithCone-M3Ra_El00Pa00ct_Bonded-Results-DispZ-M.txt", skiprows=14,  # noqa
encoding = "cp1252", thousands='\xa0', delimiter='\t', # noqa
engine='python')  # noqa

x, y, dz = df.X_mm, df.Y_mm, df.Valeur

A0 = [0, 5e-5, 0.07]
opt = minimize(error_plane, A0, (x, y, dz), method='Nelder-Mead')
A_opt = opt.x

z_theo = plane(x, y, A_opt)
dz_subs = dz - z_theo

plt.hexbin(df.X_mm, df.Y_mm, dz_subs * 1000)
plt.colorbar(label='dz [um]')
plt.savefig('tertiary_dz.pdf')
