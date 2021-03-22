'''
Receives a ray database and plot the vignetting in the design.
'''

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


def plot_vignetting(df_rays):
    cmap = plt.cm.viridis  # define the colormap
    # extract all colors from the .jet map
    cmaplist = [cmap(i) for i in range(cmap.N)]
    # force the first color entry to be grey
    cmaplist[0] = (.5, .5, .5, 1.0)

    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        'Custom cmap', cmaplist, cmap.N)

    # define the bins and normalize
    bounds = np.linspace(0, 20, 21)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    # make the scatter
    plt.hexbin(df_rays.x_pos, df_rays.y_pos, df_rays.vignette_code,
               cmap=cmap, norm=norm)
    plt.colorbar()
    plt.show()


df_rays = pd.read_hdf('ray_db.hdf', 'df')

plot_vignetting(df_rays)
