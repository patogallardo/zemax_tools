import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt
import scipy.interpolate as interp
from scipy import stats
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable

plt.rcParams.update({'font.size': 14})
s = pd.read_hdf('ray_db.hdf', 'system_variables')
center_field_deg = [s.center_field_x, s.center_field_y]

overlay_circle = True
rs = [2200/2]  # radii for circles overlay


def get_field_positions_and_strehl_map_fname():
    '''find 2 databases in current folder.
    field positions and strehls.
    if there are more than one file per flavor of database it will
    raise an error.'''
    field_position_fnames = glob.glob('ray_db.hdf')
    strehl_fnames = glob.glob('strehl_map.hdf')

    field_position_fnames.sort()
    strehl_fnames.sort()
    assert len(field_position_fnames) == len(strehl_fnames)
    assert len(field_position_fnames) == 1
    assert len(strehl_fnames) == 1

    pos_fname, strehl_fname = field_position_fnames[0], strehl_fnames[0]

    print('Analyzing the following files:')
    print("Focal plane positions: ", pos_fname)
    print("Strehl maps: ", strehl_fname)

    s = pd.read_hdf('ray_db.hdf', 'system_variables')

    projectName = s.project_name
    print('project name: %s' % projectName)

    return pos_fname, strehl_fname, projectName

pos_fname, strehl_fname, projectName = get_field_positions_and_strehl_map_fname()  # noqa


def interpolate_vignetting_for_strehls(xx, yy, vig):
    '''Receives the xx, yy grid in angle, and their vignetting flag.
    Figures out if rays are vignetted or not and returns an interpolator
    function'''
    dim = int(np.sqrt(len(xx)))
    x = np.reshape(xx, (dim, dim))[0, :]
    y = np.reshape(yy, (dim, dim))[:, 0]
    z = vig.reshape([dim, dim]) * 1.0  # float conversion
    u = interp.RegularGridInterpolator(points=(x, y),
                                       values=z.swapaxes(0, 1),
                                       method='linear',
                                       bounds_error=False)
    return u


class open_databases:
    '''object containing raytrace dataframe split by marginal rays
    '''
    def __init__(self):
        projectInfo = get_field_positions_and_strehl_map_fname()
        self.pos_fname, strehl_fnem, projectName = projectInfo
        df_rays = pd.read_hdf(self.pos_fname, key='df')

        df_rays['hx_deg'] = df_rays['hx_deg'] - center_field_deg[0]
        df_rays['hy_deg'] = df_rays['hy_deg'] - center_field_deg[1]

        df_pos = df_rays.query('px == 0 and py == 0', inplace=False)

        df_xp = df_rays.query('px==1 and py==0')
        df_yp = df_rays.query('px==0 and py==1')
        df_xm = df_rays.query('px==-1 and py==0')
        df_ym = df_rays.query('px==0 and py==-1')

        vig1 = df_xp.vignette_code.values != 0
        vig2 = df_yp.vignette_code.values != 0
        vig3 = df_xm.vignette_code.values != 0
        vig4 = df_ym.vignette_code.values != 0
        vig_p = np.logical_or(vig1, vig2)
        vig_m = np.logical_or(vig3, vig4)
        vig = np.logical_or(vig_p, vig_m)
        self.vig = vig

        df_pos.x_pos.values[vig] = np.nan
        df_pos.y_pos.values[vig] = np.nan

        u = interpolate_vignetting_for_strehls(df_pos.hx_deg.values,
                                               df_pos.hy_deg.values,
                                               vig)

        df_strh = pd.read_hdf(strehl_fname, key='df')
        df_strh['vignetted'] = u((df_strh.xx_deg.values,
                                 df_strh.yy_deg.values))

        self.df_pos = df_pos
        self.df_xp = df_xp
        self.df_yp = df_yp
        self.df_xm = df_xm
        self.df_ym = df_ym
        self.df_strh = df_strh


db = open_databases()


def interpolate_grid(df_pos):
    dim = int(np.sqrt(len(df_pos)))  # requires square grid
    xx = df_pos.hx_deg.values
    yy = df_pos.hy_deg.values
    x = np.reshape(xx, (dim, dim))[0, :]
    y = np.reshape(yy, (dim, dim))[:, 0]

    zx = df_pos.x_pos.values.reshape([dim, dim])
    zy = df_pos.y_pos.values.reshape([dim, dim])
    u = interp.RegularGridInterpolator((x, y), zx.swapaxes(0, 1),
                                       bounds_error=False)
    v = interp.RegularGridInterpolator((x, y), zy.swapaxes(0, 1),
                                       bounds_error=False)
    return u, v


def plotArea_focal_plane(x_mm, y_mm, z_strehl,
                         thresholds=[0.95],
                         overlay_circle=False,
                         rs=[2000, 3000]):
    sel = np.logical_not(np.isnan(x_mm))
    x, y, z = x_mm[sel], y_mm[sel], z_strehl[sel]
    res = stats.binned_statistic_2d(x, y, z, statistic='mean',
                                    range=[[-2000, 2000], [-2000, 2000]],
                                    bins=[100, 100])
    x_bin = 0.5*(res.x_edge[:-1] + res.x_edge[1:])
    y_bin = 0.5*(res.y_edge[:-1] + res.y_edge[1:])

    x_increment, y_increment = np.diff(res.x_edge)[0], np.diff(res.y_edge)[0]
    pixel_area = x_increment * y_increment

    above_thresholds = [res.statistic > threshold
                        for threshold in thresholds]
    areas = [np.sum(above_threshold) * pixel_area
             for above_threshold in above_thresholds]

    for j in range(len(thresholds)):
        print('Area above Strehl %1.2f: %3.1f [m^2]' % (thresholds[j],
                                                        areas[j]/1e6))

#   now make the plot
    fig, ax = plt.subplots(figsize=[6, 5])
    hb = ax.hexbin(x_mm, y_mm, z_strehl, vmin=0.95, vmax=1.0)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.05)

    cbar = plt.colorbar(hb, cax=cax,
                        ticks=np.array([0.95, 0.96, 0.97, 0.98, 0.99, 1.00]))
    cbar.set_label('Strehl ratio [-]')

    contours_ = [0.98, 0.99]
    cs = ax.contour(x_bin, y_bin, res.statistic.T, contours_,
                    cmap='inferno')
    ax.clabel(cs, inline=1, fontsize=15, fmt='%1.2f')

    if overlay_circle:
        theta = np.linspace(0, 2*np.pi, 1000)
        for j, r in enumerate(rs):
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            circle_area = np.pi * r**2/1e6  # in m^2
            ax.plot(x, y,
                 label='$r_{\\bigcirc}$= %1.2f m\nA=%1.2f$m^2$' % (r/1000, circle_area),  # noqa
                 color='C%i' %(j+1))  # noqa
        ax.legend(loc='lower left', fontsize=8)
    ax.set_aspect('equal')

    ax.set_xlabel('$x_{\\rm{focal~plane}}$ [mm]')
    ax.set_ylabel('$y_{\\rm{focal~plane}}$ [mm]')

    x_min, x_max = np.min(x_mm[sel])*1.05, np.max(x_mm[sel])*1.05
    y_min, y_max = np.min(y_mm[sel])*1.05, np.max(y_mm[sel])*1.05

    ax.set_xlim([x_min, x_max])
    ax.set_ylim([y_min, y_max])

    ax.set_title('Focal plane Strehl ratio at $\\lambda=1mm$')
#    plt.colorbar()
    ax.grid(alpha=0.3)

#   bubble
    texts = ['Area$_{Strehl > %1.2f}$: %1.1fm$^2$' % (thresholds[j], areas[j]/1e6)  # noqa
             for j in range(len(thresholds))]
    textstr = '\n'.join(texts)
    props = dict(boxstyle='round', facecolor='white', alpha=1)
    plt.figtext(0.63, 0.84, textstr, bbox=props, fontsize=8, alpha=1.0)
    plt.figtext(0.9, 0.05, projectName, fontsize=5, ha='right')
    if not os.path.exists('./strehls'):
        os.mkdir('./strehls')
    fig.tight_layout()
    plt.savefig('./strehls/focal_plane_strehls.png', dpi=150)
    plt.savefig('./strehls/focal_plane_strehls.pdf')
    plt.close()


def plot_img_qual_sky(db, thresholds=[0.95, 0.8]):
    df_strh = db.df_strh
    sel = df_strh.vignetted == 0

    x, y = df_strh.xx_deg.values[sel], df_strh.yy_deg.values[sel]
    z = df_strh.z_strehl.values[sel]
    res = stats.binned_statistic_2d(x, y, z, statistic='mean',
                                    range=[[-7, 7], [-7, 7]],
                                    bins=[100, 100])
    # compute area over thresholds
    x_bin = 0.5*(res.x_edge[:-1] + res.x_edge[1:])
    y_bin = 0.5*(res.y_edge[:-1] + res.y_edge[1:])

    x_increment, y_increment = np.diff(res.x_edge)[0], np.diff(res.y_edge)[0]
    pixel_area = x_increment * y_increment  #

    above_thresholds = [res.statistic > threshold
                        for threshold in thresholds]
    areas = [np.sum(above_threshold) * pixel_area
             for above_threshold in above_thresholds]

    for j in range(len(thresholds)):
        print('Area above Strehl %1.2f: %3.1f [deg^2]' % (thresholds[j],
                                                          areas[j]))

#   now make the plot
    fig, ax = plt.subplots(figsize=[6, 5])

    hb = ax.hexbin(x, y, z, vmin=0.80, vmax=1.0)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.05)

    cbar = plt.colorbar(hb, cax=cax,
                        ticks=np.arange(0.7, 1.05, 0.05))
    cbar.set_label('Strehl ratio [-]')

    cs = ax.contour(x_bin, y_bin, res.statistic.T,
                    np.arange(0.75, 1.0, 0.05),
                    cmap='inferno')
    ax.clabel(cs, inline=1, fontsize=15)

    ax.set_xlabel('$x_{sky}$ [deg]')
    ax.set_ylabel('$y_{sky}$ [deg]')

    xmax = 5.0
    ax.set_xlim([-xmax, xmax])
    ax.set_ylim([-xmax, xmax])

    ax.set_title('Sky Strehl ratio at $\\lambda=1mm$')
    ax.grid(alpha=0.3)

#    bubble
    texts = ['$\\Omega_{Strehl > %1.2f}$: %1.2f deg$^2$' % (thresholds[j],
                                                            areas[j])
             for j in range(len(thresholds))]
    textstr = '\n'.join(texts)
    props = dict(boxstyle='round', facecolor='white', alpha=0.7)
    plt.figtext(0.60, 0.165, textstr, bbox=props, fontsize=8)
    plt.figtext(0.9, 0.05, projectName, fontsize=5, ha='right')
    if not os.path.exists('./strehls'):
        os.mkdir('./strehls')
    fig.tight_layout()
    plt.savefig('./strehls/sky_strehls.png', dpi=150)
    plt.savefig('./strehls/sky_strehls.pdf')
    plt.close()


u, v = interpolate_grid(db.df_pos)

x_str_deg, y_str_deg = db.df_strh.xx_deg.values, db.df_strh.yy_deg.values
positions_to_eval = np.hstack([x_str_deg[:, np.newaxis],
                               y_str_deg[:, np.newaxis]])

x_mm = u(positions_to_eval)
y_mm = v(positions_to_eval)


plotArea_focal_plane(x_mm, y_mm, db.df_strh.z_strehl.values,
                     overlay_circle=overlay_circle,
                     rs=rs)

plot_img_qual_sky(db)
