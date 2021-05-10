import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection

df_groups = pd.read_csv('./groups_info/85cam_groups.csv')
df_fn = pd.read_csv('./f_numbers/f_numbers.csv')


def mk_hex(x, y, z, show=True, plot_range=None, colorbar_label='',
           fig_title='',
           plot_fname=None):
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
        plt.text(x[j], y[j],
                 "%3.2f" % z[j],
                 ha='center', va='center', color='gray')

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


x_mm, y_mm = [], []
for cam in df_fn.cam.values:
    sel = df_groups.config.values == cam
    assert(np.sum(sel) == 1)
    x_mm.append(df_groups.x.values[sel][0])
    y_mm.append(df_groups.y.values[sel][0])
x_mm = np.array(x_mm)
y_mm = np.array(y_mm)
z = df_fn.f_num.values

mk_hex(x_mm, y_mm, z, show=False, fig_title="f/#",
       colorbar_label="f/#", plot_fname='./f_numbers/summary_fn')
