import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection
import numpy as np


def mk_hex(x, y, z,
           upper_lower=None,
           show=True, plot_range=None, colorbar_label='',
           fig_title='',
           plot_fname=None,
           float_fmt_number_of_decimals=2):
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    cmap = plt.get_cmap('inferno')
    rotation = 0
    patches = []
    for j in range(len(x)):
        x_coord, y_coord = x[j], y[j]
        p = RegularPolygon([x_coord, y_coord], 6, 107, rotation)
        patches.append(p)
    collection = PatchCollection(patches, cmap=cmap)
    collection.set_array(z)

    if plot_range is None:
        vmin = np.min(z)
        vmax = np.max(z)
        if np.isclose(vmin, vmax):
            vmin = 0
        collection.set_clim(vmin=vmin, vmax=vmax)
        print("min: %1.2f, max: %1.2f" % (np.min(z), np.max(z)))
    else:
        collection.set_clim(plot_range)

    fig, ax = plt.subplots(figsize=[4, 4.5])
    ax.add_collection(collection)

    min_max_space = 1.12
    plt.xlim([x.min()*min_max_space, x.max()*min_max_space])
    plt.ylim([y.min()*min_max_space, y.max()*min_max_space])

    for j in range(len(x)):
        if upper_lower is None:
            if float_fmt_number_of_decimals == 0:
                st = "$%3.0f$" % z[j]
            elif float_fmt_number_of_decimals == 1:
                st = "$%3.1f$" % z[j]
            else:
                st = "$%3.2f$" % z[j]
        else:
            upper, lower = upper_lower[0][j], upper_lower[1][j]
            st = "$%3.2f^{%3.2f}_{%3.2f}$" % (z[j], upper, lower)
        plt.text(x[j], y[j],
                 st,
                 ha='center', va='center', color='gray',
                 size=5.8)
        plt.text(x[j], y[j]+60,
                 "%i" % (j+1),
                 ha='center', va='center',
                 color='gray', size=6)
    ax.set_aspect('equal')
    plt.axis('off')
    plt.colorbar(collection,
                 label=colorbar_label,
                 location='bottom',
                 pad=0.03,
                 fraction=0.05,
                 shrink=0.85,
                 aspect=40)
    plt.xlabel("x [mm]")
    plt.ylabel("y [mm]")
    plt.tight_layout()
    if show:
        plt.show()
        plt.close()
    else:
        assert plot_fname is not None
        plt.savefig("%s.png" % plot_fname)
        plt.savefig("%s.pdf" % plot_fname)
        plt.close()
