import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from progressbar import progressbar
import os
import glob

#  To do: export wavelngth from zemax
fnames = glob.glob('*/strehls.npz')
assert len(fnames) > 1

fname = fnames[0]
strehls_above = [0.7, 0.8, 0.9]
contour_levels = np.arange(0.5, 1.05, 0.1)


def open_strehl_data(fname):
    f = np.load(fname)
    x, y = f['x'], f['y']
    dx = np.diff(x)[0]
    xx, yy = np.meshgrid(x, y)
    zs = f['zs']
    array_radius = 65
    nconf = zs.shape[0]
    wavelength = f['wavelength']
    strehl_data = {'f': f,
                   'x': x,
                   'y': y,
                   'dx': dx,
                   'xx': xx,
                   'yy': yy,
                   'zs': zs,
                   'array_radius': array_radius,
                   'nconf': nconf,
                   'wavelength': float(wavelength)}
    return strehl_data


def make_circle(radius):
    '''Make a circle and return x,y coords with circle area'''
    t = np.linspace(0, 2*np.pi, 300)
    x_circ = radius * np.cos(t)
    y_circ = radius * np.sin(t)
    a_circ = np.pi * radius**2
    return x_circ, y_circ, a_circ


def make_summary(fraction_of_array_above_threshold, strehls_above):
    text_list = []
    for j in range(len(strehls_above)):
        s = '$A_{s>%1.1f}$=%3.0f%%' % (strehls_above[j],
                 100*fraction_of_array_above_threshold[j])  # noqa
        text_list.append(s)
    text = "\n".join(text_list)
    return text


def make_plots_and_pack_results(fname):
    folder = os.path.split(fname)[0]
    #  Open strehl ratio data for all the cams
    d = open_strehl_data(fname)
    x, y, dx, xx, yy = d['x'], d['y'], d['dx'], d['xx'], d['yy']
    zs, array_radius, nconf = d['zs'], d['array_radius'], d['nconf']
    wavelength = d['wavelength']

    #  prepare output arrays too many indices for array: array is
    #  0-dimensional, but 1 were indexed
    df_column_names = [('area_above_%1.1f' % (strehl_above)).replace('.', 'p')
                       for strehl_above in strehls_above]
    df_columns = np.zeros([nconf, len(strehls_above)])

    for conf in progressbar(range(nconf)):
        #  plot contours
        z = zs[conf, :, :]
        z_in = np.ma.masked_where(np.sqrt(xx**2+yy**2) > array_radius, z)
        z_out = np.ma.masked_where(np.sqrt(xx**2+yy**2) < array_radius, z)
        z_in.fill_value, z_out.fill_value = np.nan, np.nan

        pc = plt.pcolor(xx, yy, z_out, shading='nearest',
                        cmap='gray')
        pc = plt.pcolor(xx, yy, z_in, shading='nearest',
                        vmin=0.7, vmax=1.0)

        cs = plt.contour(x, y, z, extent=[-70, 70,
                                          -70, 70],
                         origin='upper',
                         levels=contour_levels,
                         vmin=0.7, vmax=1.0,
                         colors='gray')
        plt.clabel(cs, inline=1, fontsize=15)
        plt.colorbar(pc, label='Strehl ratio [-]')

        #  make array circle
        x_circ, y_circ, a_circ = make_circle(array_radius)
        plt.plot(x_circ, y_circ,
                 label='%i mm $\\phi$' % array_radius,
                 color='C1')
        plt.axis('equal')

        # compute areas
        areas = [np.sum(z_in > strehl) * dx**2 for strehl in strehls_above]
        areas = np.array(areas)
        fraction_of_array_above_threshold = areas/a_circ

        # save areas
        df_columns[conf] = fraction_of_array_above_threshold

        summary_text = make_summary(fraction_of_array_above_threshold,
                                    strehls_above)
        plt.text(-62, -62, summary_text,
                 horizontalalignment='left',
                 verticalalignment='bottom',
                 bbox=dict(boxstyle="round",
                           ec=(0.1, 0.1, 0.1, 0.5),
                           fc=(0.5, 0.5, 0.5, 0.5),),
                 zorder=10)

        plt.title('conf: %i wavelength: %1.1f' % (conf+1, wavelength))

        plt.xlabel('x [mm]')
        plt.ylabel('y [mm]')
        plt.legend(loc='upper right')
        plt.savefig('%s/%02i.png' % (folder, conf+1), dpi=150)
        plt.close()

    df_coords = pd.read_csv("./groups_info/85cam_groups.csv")
    df_coords.sort_values('config', inplace=True)
    x = df_coords.x.values
    y = df_coords.y.values
    df = pd.DataFrame(df_columns, columns=df_column_names)
    df['configuration'] = df_coords.config.values
    df['x_mm'] = x
    df['y_mm'] = y
    df.to_csv('%s/img_qual_coverage.csv' % folder)


for fname in fnames:
    make_plots_and_pack_results(fname)
