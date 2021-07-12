import glob
import matplotlib.pyplot as plt
import numpy as np  # noqa
import pandas as pd
import os
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection

fnames = glob.glob('*/img_qual_coverage.csv')
print(fnames)
color_cols = ['area_above_0p7', 'area_above_0p8', 'area_above_0p9']

fname = fnames[0]


def mk_hexagons(fname, color_col, rotation=0, show=False):
    pct_strehl = float(color_col.split('_')[-1].replace('p', '.'))
    directory = os.path.split(fname)[0]  # noqa
    df = pd.read_csv(fname)
    x, y = df.x_mm.values, df.y_mm.values
    color_vals = df[color_col].values * 100
    cmap = plt.get_cmap('inferno')

    patches = []
    for j in range(len(df)):
        x_coord, y_coord = df.x_mm.values[j], df.y_mm.values[j]
        p = RegularPolygon([x_coord, y_coord], 6, 100, rotation)
        patches.append(p)
    collection = PatchCollection(patches, cmap=cmap)
    collection.set_array(color_vals)
    collection.set_clim([0, 100])
    fig, ax = plt.subplots(figsize=[12, 9])
    ax.add_collection(collection)

    min_max_space = 1.15
    plt.xlim([x.min()*min_max_space, x.max()*min_max_space])
    plt.ylim([y.min()*min_max_space, y.max()*min_max_space])

    for j in range(len(df)):
        plt.text(df.x_mm.values[j], df.y_mm.values[j],
                 '%3i %%' % color_vals[j],
                 ha='center', va='center',
                 color='gray')
    ax.set_aspect('equal')
    plt.colorbar(collection,
                 label='%% of array above Strehl %1.1f' % (pct_strehl))
    wavelength = directory.split('_')[-1]
    plt.title('Area above Strehl %1.1f, $\\lambda$=%s' % (pct_strehl,
                                                          wavelength))
    if show:
        plt.show()
    else:
        plt.savefig(os.path.join(directory, color_col + ".pdf"))
        plt.savefig(os.path.join(directory, color_col + ".png"))
        plt.close()


for fname in fnames:
    mk_hexagons(fname, color_cols[0])
    mk_hexagons(fname, color_cols[1])
    mk_hexagons(fname, color_cols[2])
