import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from skimage.measure import EllipseModel
import os
import progressbar


if not os.path.exists('f_numbers/ellipticity'):
    os.mkdir('f_numbers/ellipticity')
if not os.path.exists('f_numbers/ellipses_fits'):
    os.mkdir('f_numbers/ellipses_fits')
if not os.path.exists('f_numbers/a'):
    os.mkdir('f_numbers/a')
if not os.path.exists('f_numbers/b'):
    os.mkdir('f_numbers/b')
if not os.path.exists('f_numbers/solidangle'):
    os.mkdir('f_numbers/solidangle')


fname = 'f_numbers/ray_db_pupil.hdf'

configuration = 1
distance = 1e5

for configuration in progressbar.progressbar(range(1, 86, 1)):
    ellipse_info = []
    df = pd.read_hdf(fname, 'df%02i' % configuration)
    grouped = df.groupby(['hx_deg', 'hy_deg'])

    fits = []
    for name, group in grouped:
        ellipse = EllipseModel()
        data = np.vstack((group.x_pos.values, group.y_pos.values))
        ellipse.estimate(data.T)
        fits.append(ellipse)

    t = np.linspace(0, 2*np.pi, 1000)
    for j, name_group in enumerate(grouped):
        name, group = name_group
        plt.scatter(group.x_pos, group.y_pos, marker='x',
                    color='C%i' % j)
        p = fits[j].params
        a, b = max(p[2], p[3]), min(p[2], p[3])

        angle_a = np.rad2deg(np.arctan(a/distance))
        angle_b = np.rad2deg(np.arctan(b/distance))

        ellipse_info.append([name[0], name[1], a, b, angle_a, angle_b])
        label = 'fld: %1.2f %1.2f, a/b=%1.3f' % (name[0], name[1], a/b)
        predicted = fits[j].predict_xy(t)
        plt.plot(predicted[:, 0], predicted[:, 1], label=label)
    df_ellipses = pd.DataFrame(ellipse_info,
                               columns=['Hx', 'Hy', 'a', 'b',
                                        'angle_a', 'angle_b'])
    df_ellipses['r'] = np.sqrt(df_ellipses.Hx**2 + df_ellipses.Hy**2)

#  Plot ellipticity
    plt.title('Ellipticity')
    plt.xlabel('x[mm]')
    plt.ylabel('y[mm]')
    plt.legend(loc='upper left', fontsize=5, ncol=2)
    plt.axis('equal')
    plt.savefig('f_numbers/ellipses_fits/ellipticity_conf_%02i.png' % configuration,  # noqa
                dpi=120)
    plt.close()


#  Plot semiaxis a
    plt.scatter(df_ellipses.Hx, df_ellipses.Hy,
                c=df_ellipses.angle_a)
    plt.colorbar(label='a [deg]')
    plt.savefig('f_numbers/a/a_conf_%02i.png' % configuration,
                dpi=120)
    plt.close()


# plot semiaxis b
    plt.scatter(df_ellipses.Hx, df_ellipses.Hy,
                c=df_ellipses.angle_b)
    plt.colorbar(label='b [deg]')
    plt.savefig('f_numbers/b/b_conf_%02i.png' % configuration,
                dpi=120)
    plt.close()


# plot ellipticity a/b
    fig, [ax1, ax2] = plt.subplots(nrows=2, ncols=1, figsize=[6, 9])
    mappable = ax1.scatter(df_ellipses.Hx, df_ellipses.Hy,
                           c=df_ellipses.angle_a/df_ellipses.angle_b)
    plt.colorbar(mappable, ax=ax1, label='a/b [-]')

    ax2.scatter(df_ellipses.r,
                df_ellipses.angle_a/df_ellipses.angle_b)
    ax2.set_xlabel('r')
    ax2.set_ylabel('a/b')
    plt.savefig('f_numbers/ellipticity/ellipticity_map_conf_%02i' % configuration,  # noqa
                dpi=120)  # noqa
    plt.close()


# plot solid angle
    fig, [ax1, ax2, ax3] = plt.subplots(nrows=3, ncols=1, figsize=[6, 9])
    mappable = ax1.scatter(df_ellipses.Hx, df_ellipses.Hy,
                c=np.pi * df_ellipses.angle_a * df_ellipses.angle_b)  # noqa
    ax1.axis('equal')
    plt.colorbar(mappable, ax=ax1, label='$\\Omega$ [deg$^2$]')
    ax2.scatter(df_ellipses.r,
                np.pi * df_ellipses.angle_a * df_ellipses.angle_b)
    ax2.set_xlabel('r [deg]')
    ax2.set_ylabel('$\\Omega$ [$deg^2$]')
    ax3.hist(np.pi * df_ellipses.angle_a * df_ellipses.angle_b)  # noqa
    ax3.set_xlabel("$\\Omega$ [deg$^2$]")
    ax3.set_ylabel('Count')
    plt.savefig('f_numbers/solidangle/solidangle_conf_%02i' % configuration,
                dpi=120)
    plt.close()
