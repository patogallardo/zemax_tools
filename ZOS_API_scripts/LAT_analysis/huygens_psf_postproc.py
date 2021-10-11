import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
import os
import glob
from progressbar import progressbar
fnames = glob.glob('psfcut/data/*.npz')
show = False
SCALE_X = 2.559e-4
UNIT = "arcmin"


if not os.path.exists('psfcut/plots'):
    os.mkdir('psfcut/plots')


def get_fwhm(x, y):
    max_strehl = np.max(y)
    if max_strehl < 0.3:
        fwhm = np.nan
    else:
        f = interpolate.interp1d(x, y, kind='cubic')
        x_new = np.linspace(x.min(), x.max(), 400)
        y_new = f(x_new)
        max_strehl = y_new.max()
        y_norm_to_one = y_new/max_strehl
        sel = y_norm_to_one > 0.5
        x_min_fw = x_new[sel].min()
        x_max_fw = x_new[sel].max()
        fwhm = x_max_fw - x_min_fw
    return fwhm * SCALE_X


for jfilename in progressbar(range(len(fnames))):
    data = np.load(fnames[jfilename])
    if jfilename == 0:
        print("data containers have the following: ", data.files)

    nx, nfields = data['psf'].shape

    for j in range(nfields):
        x = data['x']
        y = data['psf'][:, j]
        fwhm = get_fwhm(x, y)
        plt.plot(x*SCALE_X, y,
                 label='field: %i, fwhm:%1.3f %s' % ((j+1),
                                                     fwhm,
                                                     UNIT))
    plt.legend()
    if show:
        plt.show()
    else:
        fnametosave = os.path.split(fnames[jfilename])[-1] + '.png'
        plt.savefig('psfcut/plots/' + fnametosave)
        plt.close()
