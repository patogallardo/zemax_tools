'''
Visualizes distortions in the focal plane by using a regular grid in 
sky coordinates
'''

import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec

assert os.path.exists('ray_db.hdf')

def get_grid(df, step):
    '''extracts a grid in hx, hy with the step in degrees'''
    x_grid = np.arange(np.round(df.hx_deg.min()), 
                       np.round(df.hx_deg.max()), 
                       step)
    y_grid = np.arange(np.round(df.hy_deg.min()), 
                       np.round(df.hy_deg.max()),
                       step)
    
    x_unique = df.hx_deg.unique()
    y_unique = df.hy_deg.unique()
    
    x_sampled = [x_unique[np.argsort((x_unique - x)**2)[0]] for x in x_grid]
    y_sampled = [y_unique[np.argsort((y_unique - y)**2)[0]] for y in y_grid]

    usex = [df.hx_deg.values == x for x in x_sampled]
    usey = [df.hy_deg.values == y for y in y_sampled]
    use = usex + usey
    
    sel = usex[0]
    for usej in use:
        sel = np.logical_or(sel, usej)
    return sel



s = pd.read_hdf('ray_db.hdf', 'system_variables')
df = pd.read_hdf('ray_db.hdf', 'df').query('px==0 and py==0 and vignette_code==0', inplace=False)
df['hx_deg'] = df['hx_deg'] - s.center_field_x
df['hy_deg'] = df['hy_deg'] - s.center_field_y

sel = get_grid(df, step=1)
df = df[sel]

fig = plt.figure(figsize = [15, 6])
gs = gridspec.GridSpec(1,2)
ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])

ax1.scatter(df.hx_deg, df.hy_deg, marker='.')
ax1.set_aspect('equal')
ax1.set_title('Sky')
ax1.set_xlabel('x [deg]')
ax1.set_ylabel('y [deg]')
ax1.grid()

ax2.scatter(df.x_pos, df.y_pos, marker='.')
ax2.set_aspect('equal')
ax2.set_title('Focal plane')
ax2.set_xlabel('x [mm]')
ax2.set_ylabel('y [mm]')
ax2.grid()

plt.tight_layout()

dirname = 'distortion'
if not os.path.exists(dirname):
    os.mkdir(dirname)
plt.savefig(os.path.join(dirname, 'distortion.png'), dpi=150)

