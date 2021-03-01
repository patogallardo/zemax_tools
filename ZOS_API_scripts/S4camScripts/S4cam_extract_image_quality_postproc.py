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
    radii_array = f['radii_array']
    nconf = zs.shape[0]
    field_size = f['field_size']
    wavelength = f['wavelength']
    strehl_data = {'f': f,
                   'x': x,
                   'y': y,
                   'dx': dx,
                   'xx': xx,
                   'yy': yy,
                   'zs': zs,
                   'radii_array': radii_array,
                   'nconf': nconf,
                   'field_size': field_size,
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
    zs, radii_array, nconf = d['zs'], d['radii_array'], d['nconf']
    field_size = d['field_size']
    wavelength = d['wavelength']

    #  prepare output arrays too many indices for array: array is
    #  0-dimensional, but 1 were indexed
    df_column_names = [('area_above_%1.1f' % (strehl_above)).replace('.', 'p')
                       for strehl_above in strehls_above]
    df_columns = np.zeros([nconf, len(strehls_above)])

    for conf in progressbar(range(nconf)):
        #  plot contours
        z = zs[conf, :, :]
        pc = plt.pcolor(xx, yy, z, shading='nearest')
        cs = plt.contour(x, y, z, extent=[-field_size, field_size,
                                          -field_size, field_size],
                         origin='upper',
                         levels=contour_levels)
        plt.clabel(cs, inline=1, fontsize=15)
        plt.colorbar(pc, label='Strehl ratio [-]')

        #  make array circle
        x_circ, y_circ, a_circ = make_circle(radii_array[conf])
        plt.plot(x_circ, y_circ, label='130 mm $\\phi$', color='black')
        plt.axis('equal')

        # compute areas
        areas = [np.sum(z > strehl) * dx**2 for strehl in strehls_above]
        areas = np.array(areas)
        fraction_of_array_above_threshold = np.minimum(areas/a_circ, 1.0)

        # save areas
        df_columns[conf] = fraction_of_array_above_threshold

        summary_text = make_summary(fraction_of_array_above_threshold,
                                    strehls_above)
        plt.text(-field_size, -field_size, summary_text,
                 horizontalalignment='left', verticalalignment='bottom')

        plt.title('conf: %i wavelength: %1.1f' % (conf+1, wavelength))

        plt.xlabel('x [deg]')
        plt.ylabel('y [deg]')
        plt.legend(loc='upper right')
        plt.savefig('%s/%02i.png' % (folder, conf+1), dpi=150)
        plt.close()

    df_coords = pd.read_csv("C:\\Users\\pgall\\Documents\\wilson\\"
                            "code\\zemax_tools\\S4cam\\groupCameras\\"
                            "85cam_groups.csv")
    x = df_coords.x.values
    y = df_coords.y.values
    df = pd.DataFrame(df_columns, columns=df_column_names)
    df['configuration'] = df.index + 1
    df['x_mm'] = x
    df['y_mm'] = y
    df.to_csv('%s/img_qual_coverage.csv' % folder)


for fname in fnames:
    make_plots_and_pack_results(fname)
