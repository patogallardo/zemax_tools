import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt
import scipy.interpolate as interp
from scipy import stats


center_field_deg = [0, -10.5] # this should be the sky position in degrees
# the strehls were created around. See script focal_plane_strehl_ratios.py
# for more detail


def get_field_positions_and_strehl_map_fnames():
    '''find 2 databases in current folder.
    field positions and strehls.
    if there are more than one file per flavor of database
    it will make sure they are matched.'''
    field_position_fnames = glob.glob('*_field_positions.csv')
    strehl_fnames = glob.glob('*_strehl_map.csv')
    field_position_fnames.sort()
    strehl_fnames.sort()
    assert len(field_position_fnames) == len(strehl_fnames)
    
    for j in range(len(field_position_fnames)):
        fpos_design_name = field_position_fnames[j].split('_field')[0]
        strehl_design_name = strehl_fnames[j].split('_strehl')[0]
        assert fpos_design_name == strehl_design_name

    return field_position_fnames, strehl_fnames

pos_fnames, strehl_fnames = get_field_positions_and_strehl_map_fnames()

print('Analyzing the following files:')
print("Focal plane positions: ",pos_fnames)
print("Strehl maps: ", strehl_fnames)


j = 0

projectName = pos_fnames[0].split('_')[0]
print('project name: %s' %projectName)


#open databases

df_pos = pd.read_csv(pos_fnames[j], index_col=0)
df_strh = pd.read_csv(strehl_fnames[j], index_col=0)


# correct for center field position. This should be the field with respect to
# which the strehls were created.

df_pos['hx_deg'] = df_pos['hx_deg'] - center_field_deg[0]
df_pos['hy_deg'] = df_pos['hy_deg'] - center_field_deg[1]

# Now interpolate u(hx_deg, hy_deg) and v(hx_deg, hy_deg)

def interpolate_grid(df_pos):
    dim = int(np.sqrt(len(df_pos)))
    xx = df_pos.hx_deg.values
    yy = df_pos.hy_deg.values
    x = np.reshape(xx, (dim, dim))[0, :]
    y = np.reshape(yy, (dim, dim))[:, 0]
    
    zx = df_pos.x_pos.values.reshape([dim, dim])
    zy = df_pos.y_pos.values.reshape([dim, dim])
    u = interp.RegularGridInterpolator((x, y), zx.swapaxes(0,1),
                                       bounds_error=False)
    v = interp.RegularGridInterpolator((x, y), zy.swapaxes(0,1), 
                                       bounds_error=False)
    return u, v



def plotArea(x_mm, y_mm, z_strehl, thresholds=[0.7, 0.8, 0.9]):
    sel = np.logical_not(np.isnan(x_mm))
    x, y, z = x_mm[sel], y_mm[sel], z_strehl[sel]
    res = stats.binned_statistic_2d(x, y, z, statistic='mean',
                                    range=[[-2000, 2000],[-2000, 2000]],
                                    bins=[100, 100])
    x_bin = 0.5*(res.x_edge[:-1] + res.x_edge[1:])
    y_bin = 0.5*(res.y_edge[:-1] + res.x_edge[1:])

    x_increment, y_increment = np.diff(res.x_edge)[0], np.diff(res.y_edge)[0]
    pixel_area = x_increment * y_increment

    above_thresholds = [res.statistic > threshold 
                        for threshold in thresholds]
    areas = [np.sum(above_threshold) * pixel_area 
             for above_threshold in above_thresholds]

    for j in range(len(thresholds)): 
        print('Area above %1.1f: %3.1f' %(thresholds[j], areas[j]))

    #now make the plot
    fig, ax = plt.subplots(figsize=[8,4.5])
    ax.hexbin(x_mm, y_mm, z_strehl)
    cs = ax.contour(x_bin, y_bin, res.statistic.T, thresholds )
    ax.clabel(cs, inline=1, fontsize=15)

    plt.xlabel('$x_{focalPlane}$ [mm]')
    plt.ylabel('$y_{focalPlane}$ [mm]')

    x_min, x_max = np.min(x_mm[sel]), np.max(x_mm[sel])
    y_min, y_max = np.min(y_mm[sel]), np.max(y_mm[sel])

    plt.xlim([1.1*x_min, 1.1*x_max])
    plt.ylim([1.1*y_min, 1.1*y_max])

    plt.title('Focal plane Strehl ratio')
#    plt.colorbar()
    plt.grid(alpha=0.3)

    #bubble
    texts = ['Area Strehl > %1.1f: %1.3fm$^2$' %(thresholds[j], areas[j]/1e6)
             for j in range(len(thresholds))]
    textstr = '\n'.join(texts)
    props = dict(boxstyle='round', facecolor='white', alpha=1)
    plt.figtext(0.70, 0.8, textstr, bbox=props, fontsize=10)
    plt.savefig('%s_focal_plane_strehls.png' %projectName, dpi=150)
    
    return res


#plt.hexbin(x_mm, y_mm, df_strh.z_strehl.values)
#plt.colorbar()
#plt.show()
   

u, v = interpolate_grid(df_pos)

x_str_deg, y_str_deg = df_strh.xx_deg.values, df_strh.yy_deg.values
positions_to_eval = np.hstack([x_str_deg[:, np.newaxis],
                               y_str_deg[:, np.newaxis]])

x_mm = u(positions_to_eval)
y_mm = v(positions_to_eval)


res = plotArea(x_mm, y_mm, df_strh.z_strehl.values)

