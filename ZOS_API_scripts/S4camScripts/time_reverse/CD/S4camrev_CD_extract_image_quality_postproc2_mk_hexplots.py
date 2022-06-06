import glob
import numpy as np  # noqa
import pandas as pd
import os
import zmx_plot

fnames = glob.glob('*/img_qual_coverage.csv')
print(fnames)
color_cols = ['area_above_0p7',
              'area_above_0p8',
              'area_above_0p9']
fname = fnames[0]


def mk_hexagons(fname, color_col,
                show=True):
    pct_strehl = float(color_col.split('_')[-1].replace('p', '.'))
    directory = os.path.split(fname)[0]  # noqa
    df = pd.read_csv(fname)
    x, y = df.x_mm.values, df.y_mm.values
    color_vals = df[color_col].values * 100

    wavelength = directory.split('_')[-1]
    title  = 'Fraction of area above Strehl %1.1f, $\\lambda$=%s' % (pct_strehl, wavelength)  # noqa
    fnameout = os.path.join(directory, color_col)
    zmx_plot.mk_hex(x, y, color_vals, show=False,
       colorbar_label='Fraction of area above Strehl %1.1f at $\\lambda=$%s [%%]'  % (pct_strehl, wavelength),  # noqa
                    fig_title=title,
                    plot_fname=fnameout,
                    float_fmt_number_of_decimals=0)


for fname in fnames:
    mk_hexagons(fname, color_cols[0])
    mk_hexagons(fname, color_cols[1])
    mk_hexagons(fname, color_cols[2])
