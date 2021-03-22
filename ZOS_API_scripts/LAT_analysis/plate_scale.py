'''Generates plate scale calculations from a zemax sequential raytrace.
'''

import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import numpy as np

assert os.path.exists('ray_db.hdf')


DEBUG = False # makes intermediate step plots
delta_sky = 12./50 # width of a line in degrees

s = pd.read_hdf('ray_db.hdf', 'system_variables')
df = pd.read_hdf('ray_db.hdf', 'df').query('px==0 and py==0 and vignette_code==0', inplace=False)
df['hx_deg'] = df['hx_deg'] - s.center_field_x
df['hy_deg'] = df['hy_deg'] - s.center_field_y

center_x, center_y = s.center_field_x, s.center_field_y

def extract_sky_focal_plane_coords_for_direction(df, direction='x', 
                                                 delta_sky=0.05):
    if direction == 'x':
        df_subset = df.query('hy_deg > %1.3e and hy_deg<%1.3e' 
                             %(-delta_sky, delta_sky))
    if direction == 'y':
        df_subset = df.query('hx_deg > %1.3e and hx_deg<%1.3e' 
                             %(-delta_sky, delta_sky))

    return df_subset

df_x = extract_sky_focal_plane_coords_for_direction(df, delta_sky=0.05,
                                                    direction='x')
df_y = extract_sky_focal_plane_coords_for_direction(df, delta_sky=0.05,
                                                    direction='y')

if DEBUG:
    plt.scatter(df_x.hx_deg, df_x.hy_deg)
    plt.show()
    plt.scatter(df_y.hx_deg, df_y.hy_deg)
    plt.show()

    plt.scatter(df_x.hx_deg, df_x.hy_deg)
    plt.scatter(df_y.hx_deg, df_y.hy_deg)
    plt.show()

# now make plot

#top pane
fig = plt.figure(figsize=[8, 4.5])
plot_grid = plt.GridSpec(3, 1, hspace=0.1)


plot_err = fig.add_subplot(plot_grid[2, :])
plot_main = fig.add_subplot(plot_grid[0:2, :], sharex=plot_err)

#x direction
plot_main.scatter(df_x.hx_deg, df_x.x_pos, marker='.')
polyx = np.polyfit(df_x.hx_deg, df_x.x_pos, 1)
fitx = np.poly1d(polyx)
label = "x direction fit: x$_{fp}$[mm] = %3.1f[mm/deg] x$_{sky}$ + %2.1f[mm]" %(fitx[1], fitx[0])
plot_main.plot(df_x.hx_deg, fitx(df_x.hx_deg), lw=2, label=label, 
               alpha=0.7)
print('x direction fit:\n', fitx)

#y direction
plot_main.scatter(df_y.hy_deg, df_y.y_pos, marker='.')
polyy = np.polyfit(df_y.hy_deg, df_y.y_pos, 1)
fity= np.poly1d(polyy)
label = "y direction fit: y$_{fp}$[mm] = %3.1f[mm/deg] y$_{sky}$ + %2.1f[mm]" % (fity[1], fity[0])
plot_main.plot(df_y.hy_deg, fity(df_y.hy_deg), lw=2, label=label,
               alpha=0.7)
print('y direction fit:\n', fity)

plot_main.legend(loc='upper left', fontsize=8)

plot_main.set_ylabel('focal plane coordinate [mm]')

#Bottom pane
plot_err.axhline(0, color='black')
plot_err.set_xlabel('sky coordinate [deg]')
plot_err.set_ylabel('fit - position [mm]')

arg = np.argsort(df_x.hx_deg)
plot_err.plot(df_x.hx_deg.values[arg], 
              df_x.x_pos.values[arg] - fitx(df_x.hx_deg.values[arg]),
              color='C0')
arg = np.argsort(df_y.hy_deg)
plot_err.plot(df_y.hy_deg.values[arg],
              df_y.y_pos.values[arg] - fity(df_y.hy_deg.values[arg]),
              color='C1')
plt.setp(plot_main.get_xticklabels(), visible=False)

if not os.path.exists('./plate_scale'):
    os.mkdir('./plate_scale')

plot_main.set_title('Plate scale')
plt.savefig('./plate_scale/plate_scale.png', dpi=150)
