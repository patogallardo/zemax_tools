import pandas as pd
import matplotlib.pyplot as plt
import glob
import numpy as np
import os

plt.rcParams.update({'font.size': 15})


def get_fnumbers_given_vectors(ray1, ray2):
    '''Receives row objects ray1 and ray2, these must contain l,m,n
    coordinates.
    returns a f/#'''
    v1 = ray1[['l', 'm', 'n']].values[0]
    v2 = ray2[['l', 'm', 'n']].values[0]
    cos_theta = np.dot(v1, v2)
    return 0.5/np.tan(np.arccos(cos_theta))


def compare_fields(df1, df2):
    dif = df1[['hx_deg', 'hy_deg']].values - df2[['hx_deg', 'hy_deg']].values
    assert np.sum(dif**2) < 1e-16


def get_extreme_ray_dfs(df):
    df_cr = df.query('px==0 and py==0')
    df_xp = df.query('px==1 and py==0')
    df_xm = df.query('px==-1 and py==0')
    df_yp = df.query('px==0 and py==1')
    df_ym = df.query('px==0 and py==-1')

    compare_fields(df_cr, df_xp)
    compare_fields(df_cr, df_xm)
    compare_fields(df_cr, df_yp)
    compare_fields(df_cr, df_ym)

    return df_cr, df_xp, df_xm, df_yp, df_ym


def vignetted(df_cr, df_xp, df_xm, df_yp, df_ym):
    and_ = np.logical_and
    sel1 = df_cr.vignette_code.values == 0
    sel2 = df_xp.vignette_code.values == 0
    sel3 = df_xm.vignette_code.values == 0
    sel4 = df_yp.vignette_code.values == 0
    sel5 = df_ym.vignette_code.values == 0
    use = and_(and_(and_(and_(sel1, sel2), sel3), sel4), sel5)
    return use


def get_fnumber_for_a_given_direction(df1, df2):
    lmn = ['l', 'm', 'n']
    dot_p = np.sum(df1[lmn].values * df2[lmn].values, axis=1)
    fn = 0.5/np.tan(np.arccos(dot_p))
    return fn


def get_fnumbers_in_four_directions(df_cr, df_xp, df_xm, df_yp, df_ym):
    fn_xp = get_fnumber_for_a_given_direction(df_cr, df_xp)
    fn_xm = get_fnumber_for_a_given_direction(df_cr, df_xm)
    fn_yp = get_fnumber_for_a_given_direction(df_cr, df_yp)
    fn_ym = get_fnumber_for_a_given_direction(df_cr, df_ym)

    chief_ray_angle = np.rad2deg(np.arccos(df_cr.n.values))

    dont_use = np.logical_not(vignetted(df_cr, df_xp, df_xm, df_yp, df_ym))

    fn_xp[dont_use] = np.nan
    fn_xm[dont_use] = np.nan
    fn_yp[dont_use] = np.nan
    fn_ym[dont_use] = np.nan
    chief_ray_angle[dont_use] = np.nan

    fnumbers = {'fn_xp': fn_xp,
                'fn_xm': fn_xm,
                'fn_yp': fn_yp,
                'fn_ym': fn_ym,
                'fn_av': 0.25*(fn_xp + fn_xm + fn_yp + fn_ym),
                'hx_deg': df_cr.hx_deg.values,
                'hy_deg': df_cr.hy_deg.values,
                'x_pos': df_cr.x_pos.values,
                'y_pos': df_cr.y_pos.values,
                'chief_ray_angle_deg': chief_ray_angle}
    df_fnumbers = pd.DataFrame(fnumbers)
    return df_fnumbers


def get_stats(fn):
    av = np.percentile(fn, 50)
    av_m = av-np.percentile(fn, 50-34)
    av_p = np.percentile(fn, 50+34)-av
    return av, av_m, av_p


def make_fnumber_hists(df_fn, show=True):
    sel = np.logical_not(np.isnan(df_fn.fn_av.values))
    plt.figure(figsize=[5, 2.5], constrained_layout=True)

    fn_yp_av, fn_yp_m, fn_yp_p = get_stats(df_fn.fn_yp.values[sel])
    plt.hist(df_fn.fn_yp.values[sel],
             histtype='step',
             label='$f/\\#_{y+}: %1.2f_{-%1.2f}^{+%1.1f}$' % (fn_yp_av,
                                                fn_yp_m, fn_yp_p),  # noqa
             bins=40, density=True)

    fn_ym_av, fn_ym_m, fn_ym_p = get_stats(df_fn.fn_ym.values[sel])
    plt.hist(df_fn.fn_ym.values[sel],
             histtype='step',
             label='$f/\\#_{y-}: %1.2f_{-%1.2f}^{+%1.1f}$' % (fn_ym_av,
                                                fn_ym_m, fn_ym_p),  # noqa
             bins=40, density=True)

    fn_xp_av, fn_xp_m, fn_xp_p = get_stats(df_fn.fn_xp.values[sel])
    plt.hist(df_fn.fn_xp.values[sel],
             histtype='step',
             label='$f/\\#_{x+}: %1.2f_{-%1.2f}^{+%1.1f}$' % (fn_xp_av,
                                                fn_xp_m, fn_xp_p),  # noqa

             bins=40, density=True)

    fn_xm_av, fn_xm_m, fn_xm_p = get_stats(df_fn.fn_xm.values[sel])
    plt.hist(df_fn.fn_xm.values[sel],
             histtype='step',
             label='$f/\\#_{x-}: %1.2f_{-%1.2f}^{+%1.1f}$' % (fn_xm_av,
                                                fn_xm_m, fn_xm_p),  # noqa
             bins=40, density=True)

    av = np.percentile(df_fn.fn_av.values[sel], 50)
    av_m = av-np.percentile(df_fn.fn_av.values[sel], 50-34)
    av_p = np.percentile(df_fn.fn_av.values[sel], 50+34)-av

    plt.hist(df_fn.fn_av.values[sel],
             histtype='step', lw=2,
             label='$f/\\#_{av}: %1.2f_{-%1.1f}^{+%1.1f}$' % (av, av_m, av_p),
             bins=40, density=True)
    plt.axvspan(av-av_m, av+av_p, color='C4', alpha=0.2)

    plt.legend(loc='upper right', fontsize=12)
#    plt.title('Chief ray relative $f/\\#$')
    plt.xlabel('$f/\\#$ [-]')
    plt.ylabel('pdf [-]')
#    plt.tight_layout()
    if show:
        plt.show()
    else:
        plt.savefig(os.path.join(out_folder, 'fnumber_hists.png'), dpi=150)
        plt.savefig(os.path.join(out_folder, 'fnumber_hists.pdf'))
        plt.savefig(r"C:\Users\pgall\OneDrive - The University of Chicago\Github\SPLAT_paper\figures\fnumber_hists.pdf")  # noqa
        plt.close()


def make_fnumber_maps(df_fn, show=True):
    fig, ax = plt.subplots(2, 2, sharex='col', sharey='row',
                           figsize=[10, 8])
    data_id = [['fn_xp', 'fn_xm'], ['fn_yp', 'fn_ym']]
    titles = {'fn_xp': '$f/\\#_{x+}$',
              'fn_xm': '$f/\\#_{x-}$',
              'fn_yp': '$f/\\#_{y+}$',
              'fn_ym': '$f/\\#_{y-}$'}

    for i in range(2):
        for j in range(2):
            id = data_id[i][j]
            ax[i, j].set_title(titles[id])
            hb = ax[i, j].hexbin(df_fn.x_pos, df_fn.y_pos, df_fn[id])
            fig.colorbar(hb, ax=ax[i, j])
            if i == 1:
                ax[i, j].set_xlabel('x$_{focal plane}$ [mm]')
            if j == 0:
                ax[i, j].set_ylabel('y$_{focal plane}$ [mm]')
            ax[i, j].set_aspect('equal')
    fig.tight_layout()
    if show:
        plt.show()
    else:
        plt.savefig(os.path.join(out_folder, 'fnumber_xy_direction_maps.png'),
                    dpi=150)
    plt.close()

    plt.figure(figsize=[5.5, 4])
    plt.hexbin(df_fn.x_pos, df_fn.y_pos, df_fn['fn_av'])
    plt.title('Average f/$\\#$ (in x/y)')
    plt.xlabel('x$_{focal plane}$ [mm]')
    plt.ylabel('y$_{focal plane}$ [mm]')
    plt.axis('equal')
    plt.colorbar()
    plt.tight_layout()
    if show:
        plt.show()
    else:
        plt.savefig(os.path.join(out_folder, 'fnumber_av.png'),
                    dpi=150)
    plt.close()


def make_chief_angle_map(df_fn, show=False):
    plt.figure(figsize=[5.5, 4])
    plt.hexbin(df_fn.x_pos, df_fn.y_pos, df_fn['chief_ray_angle_deg'])
    plt.title('Focal plane chief ray angle (90-$\\theta$)')
    plt.xlabel('x$_{focal plane}$ [mm]')
    plt.ylabel('y$_{focal plane}$ [mm]')
    plt.axis('equal')
    plt.colorbar()
    plt.tight_layout()

    if not os.path.exists('./chief_ray'):
        os.mkdir('./chief_ray')
    if show:
        plt.show()
    else:
        plt.savefig(os.path.join('./chief_ray', 'chief_ray_angles_map.png'),
                    dpi=150)
    plt.close()


def make_chief_angle_hist(df_fn, show=False):
    plt.figure(figsize=[8, 7])
    chief_ray_angles = df_fn['chief_ray_angle_deg'].values
    sel = np.logical_not(np.isnan(chief_ray_angles))
    pct_50, pct_50m, pct_50p = np.percentile(chief_ray_angles[sel],
                                             [50, 50-34, 50+34])
    sigma_p, sigma_m = pct_50p-pct_50, pct_50 - pct_50m
    plt.hist(chief_ray_angles[sel], bins=50, histtype='step',
             color='black', label='angle=$%1.2f^{+%1.2f}_{-%1.2f}$' % (
                                  pct_50, sigma_p, sigma_m))
    plt.axvline(pct_50, color='black', alpha=1)
    plt.axvline(pct_50p, color='black', alpha=0.3)
    plt.axvline(pct_50m, color='black', alpha=0.3)
    plt.legend()
    plt.title('Chief ray angles (90-$\\theta$)')
    plt.xlabel('chief ray angle [deg]')
    plt.ylabel('N')

    plt.tight_layout()
    if not os.path.exists('./chief_ray'):
        os.mkdir('./chief_ray')
    if show:
        plt.show()
    else:
        plt.savefig(os.path.join('./chief_ray', 'chief_ray_angles_hist.pdf'))
        plt.savefig(os.path.join('./chief_ray', 'chief_ray_angles_hist.png'),
                    dpi=150)
    plt.close()


fnames = glob.glob('ray_db.hdf')
assert len(fnames) == 1
fname = fnames[0]

out_folder = './fNumbers'
if not os.path.exists(out_folder):
    os.mkdir(out_folder)

df = pd.read_hdf(fname, 'df')
df_cr, df_xp, df_xm, df_yp, df_ym = get_extreme_ray_dfs(df)
df_fnumbers = get_fnumbers_in_four_directions(df_cr, df_xp, df_xm,
                                              df_yp, df_ym)
make_fnumber_hists(df_fnumbers, show=False)

make_fnumber_maps(df_fnumbers, show=False)

make_chief_angle_map(df_fnumbers)
make_chief_angle_hist(df_fnumbers)
