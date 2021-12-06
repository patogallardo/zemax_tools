import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection
import numpy as np


def mk_hex(x, y, z,
           upper_lower=None,
           show=True, plot_range=None, colorbar_label='',
           fig_title='',
           plot_fname=None):
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    cmap = plt.get_cmap('inferno')
    rotation = 0
    patches = []
    for j in range(len(x)):
        x_coord, y_coord = x[j], y[j]
        p = RegularPolygon([x_coord, y_coord], 6, 100, rotation)
        patches.append(p)
    collection = PatchCollection(patches, cmap=cmap)
    collection.set_array(z)
    if plot_range is None:
        collection.set_clim([np.min(z), np.max(z)])
    else:
        collection.set_clim(plot_range)

    fig, ax = plt.subplots(figsize=[12, 9])
    ax.add_collection(collection)

    min_max_space = 1.15
    plt.xlim([x.min()*min_max_space, x.max()*min_max_space])
    plt.ylim([y.min()*min_max_space, y.max()*min_max_space])

    for j in range(len(x)):
        if upper_lower is None:
            st = "$%3.2f$" % z[j]
        else:
            upper, lower = upper_lower[0][j], upper_lower[1][j]
            st = "$%3.2f^{%3.2f}_{%3.2f}$" % (z[j], upper, lower)
        plt.text(x[j], y[j],
                 st,
                 ha='center', va='center', color='gray')
        plt.text(x[j]+50, y[j]+50,
                 "%i" % (j+1),
                 ha='center', va='center',
                 color='gray')

    ax.set_aspect('equal')
    plt.colorbar(collection,
                 label=colorbar_label)
    plt.title(fig_title)
    if show:
        plt.show()
    else:
        assert plot_fname is not None
        plt.savefig("%s.png" % plot_fname)
        plt.savefig("%s.pdf" % plot_fname)
        plt.close()
