import pandas as pd
import matplotlib.pyplot as plt
import numpy as np  # noqa
from scipy.optimize import minimize


def chisq_linear(y0_scale, xy_dxdy):
    y0, scale = y0_scale
    x, y, dx, dy = xy_dxdy
    deltax = dx - x * scale
    deltay = dy - y*scale - y0
    chisq = deltax**2 + deltay**2
    chisq = np.sum(chisq)
    return chisq


show = True

fname = 'window_offsets.csv'
df = pd.read_csv(fname)
x_mm = df.x_mm.values
y_mm = df.y_mm.values

V10C_dx = df['10C_dx'].values
V10C_dy = df['10C_dy'].values

sol = minimize(chisq_linear,
               x0=[0, 3],
               args=[x_mm, y_mm, V10C_dx, V10C_dy])
scale, y0 = sol.x[1], sol.x[0]

plt.figure(figsize=[8, 8])
plt.plot(x_mm, scale*x_mm, label='model x, scale:%1.3e' % scale)
plt.plot(y_mm, scale*y_mm + y0, label='model y: offset: %1.3f' % y0)

# plot 8A differences
plt.scatter(x_mm, V10C_dx,
            label='X')
plt.scatter(y_mm, V10C_dy,
            label='Y')
plt.legend()

plt.title('Window displacements')
plt.xlabel('x/y [mm]')
plt.ylabel('deviation x/y [mm]')

if show:
    plt.show()
else:
    plt.savefig('xy_dxdy.png')
    plt.savefig('xy_dxdy.pdf')
