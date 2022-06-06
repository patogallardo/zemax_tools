import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

show = False
fname = "./psf2d/arrays.npz"
npz = np.load(fname)

semi_a = np.maximum(npz['semi_a'], npz['semi_b'])
semi_b = np.minimum(npz['semi_a'], npz['semi_b'])

bins = np.arange(1, 1.14, 0.005)
ratios_mean = np.mean(semi_a/semi_b, axis=1)
ratios_max = np.max(semi_a/semi_b, axis=1)
ratios_min = np.min(semi_a/semi_b, axis=1)
ratios_mean = pd.Series(ratios_mean)
txt = ratios_mean.describe().to_string(float_format='%1.2f')


plt.hist(ratios_mean.values, bins=bins,
         histtype='step',
         color='black',
         label='mean')
plt.hist(ratios_max, bins=bins, histtype='step', color='gray',
         ls='--',
         label='max')
plt.hist(ratios_min, bins=bins, histtype='step', color='gray',
         ls='dotted',
         label='min')
plt.xlim([1, 1.14])
plt.figtext(0.73, 0.18, txt)
plt.xlabel('a/b [-]')
plt.ylabel('Camera Count [-]')
plt.title('Beam ellipticity')
plt.legend(loc='upper right')
if show:
    plt.show()
else:
    plt.savefig('psf2d/ellipticity_hist.pdf')
    plt.close()

argmax = np.unravel_index(np.argmax(semi_a/semi_b),
                          shape=semi_a.shape)
argmin = np.unravel_index(np.argmin(semi_a/semi_b),
                          shape=semi_a.shape)
print("max ellipticity, cam:%i, field:%i" % (
      argmax[0]+1, argmax[1]))
print("min ellipticity: cam:%i, field:%i" % (
      argmin[0]+1, argmin[1]))
