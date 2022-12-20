import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from skimage.measure import EllipseModel
import os
import progressbar

plt.rcParams.update({
    "text.usetex": True})
plt.rcParams.update({"font.size": 18})


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
if not os.path.exists('f_numbers/equivalent_f_number'):
    os.mkdir('f_numbers/equivalent_f_number')


fname = 'f_numbers/ray_db_pupil.hdf'

configuration = 1
distance = 1e5

f_num, f_num_min, f_num_max = [], [], []

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

# plot semiaxis f/#
    plt.scatter(df_ellipses.Hx, df_ellipses.Hy,
                c=1.0/2.0/(np.tan(np.deg2rad(df_ellipses.angle_a)))
                )
    plt.colorbar(label='$f/\\#_{a}$')
    plt.savefig('f_numbers/a/f_a_conf%02i.png' % configuration,
                dpi=120)
    plt.close()

# plot semiaxis b
    plt.scatter(df_ellipses.Hx, df_ellipses.Hy,
                c=df_ellipses.angle_b)
    plt.colorbar(label='b [deg]')
    plt.savefig('f_numbers/b/b_conf_%02i.png' % configuration,
                dpi=120)
    plt.close()


# plot semiaxis f/# b

    plt.scatter(df_ellipses.Hx, df_ellipses.Hy,
                c=1.0/2.0/(np.tan(np.deg2rad(df_ellipses.angle_b)))
                )
    plt.colorbar(label='$f/\\#_{b}$')
    plt.savefig('f_numbers/b/f_b_conf%02i.png' % configuration,
                dpi=120)
    plt.close()

# plot equivalent f/#
    plt.scatter(df_ellipses.Hx, df_ellipses.Hy,
                c=1.0/2.0/np.tan(np.deg2rad(np.sqrt(df_ellipses.angle_a *
                                                    df_ellipses.angle_b))))
    plt.colorbar(label='$f/\\#_{eq}$')
    cs = plt.tricontour(df_ellipses.Hx, df_ellipses.Hy,
                     1.0/2.0/np.tan(np.deg2rad(np.sqrt(df_ellipses.angle_a *  # noqa
                                                       df_ellipses.angle_b))),  # noqa
                        levels=np.arange(1.7, 2.55, 0.05),
                        vmin=2.0, vmax=2.5,
                        colors='gray')
    plt.clabel(cs, inline=1, fontsize=15)
    plt.xlabel('x [mm]')
    plt.ylabel('y [mm]')
    xy_lim = [df_ellipses.Hy.min()*1.1, df_ellipses.Hy.max()*1.1]
    plt.xlim(xy_lim)
    plt.ylim(xy_lim)
    plt.title("Camera %i"% configuration)
    plt.tight_layout()
    plt.savefig('f_numbers/equivalent_f_number/'
                'eq_f_n_%02i.png' % configuration,
                dpi=120)
    plt.savefig('f_numbers/equivalent_f_number/'
                'eq_f_n_%02i.pdf' % configuration)

    plt.close()


# plot eq f/# histogram
    plt.hist(1.0/2.0/np.tan(np.deg2rad(np.sqrt(df_ellipses.angle_a *
                                               df_ellipses.angle_b))),
             bins=5,
             histtype='step',
             label='conf:%02i' % configuration)
    plt.xlabel('$f/\\#$')
    plt.ylabel('count')
    plt.legend()
    plt.savefig('f_numbers/equivalent_f_number/'
                'eq_fn_%02i_hist.png' % configuration,
                dpi=120)
    plt.close()

    f_nums = 1.0/2.0/np.tan(np.deg2rad(np.sqrt(df_ellipses.angle_a *
                                               df_ellipses.angle_b)))
    f_num.append(np.mean(f_nums))
    f_num_min.append(np.min(f_nums))
    f_num_max.append(np.max(f_nums))

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

df_out = pd.DataFrame(np.array([range(1, 86, 1), f_num,
                                f_num_min, f_num_max]).T,
                      columns=['cam', 'f_num', 'f_num_min', 'f_num_max'])
df_out.to_csv('./f_numbers/f_numbers.csv')
