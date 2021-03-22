import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from skimage.measure import EllipseModel
import os

fname = 'ray_db_pupil.hdf'

df = pd.read_hdf(fname, 'df')
grouped = df.groupby(['hx_deg', 'hy_deg'])

if not os.path.exists('ellipticity'):
    os.mkdir('ellipticity')

fits = []
for name, group in grouped:
    ellipse = EllipseModel()
    data = np.vstack((group.x_pos.values, group.y_pos.values))
    ellipse.estimate(data.T)
    fits.append(ellipse)

t = np.linspace(0, 2*np.pi, 1000)
for j, name_group in enumerate(grouped):
    name, group = name_group
    plt.scatter(group.x_pos, group.y_pos, marker='x',
                color='C%i' % j)
    p = fits[j].params
    label = 'fld: %1.1f %1.1f, a/b=%1.3f' % (name[0], name[1], p[2]/p[3])
    predicted = fits[j].predict_xy(t)
    plt.plot(predicted[:, 0], predicted[:, 1], label=label)
plt.grid()
plt.title('Ellipticity')
plt.xlabel('x[mm]')
plt.ylabel('y[mm]')
plt.legend(loc='upper left', fontsize=8)
plt.axis('equal')
plt.savefig('ellipticity/ellipticity.png', dpi=120)
