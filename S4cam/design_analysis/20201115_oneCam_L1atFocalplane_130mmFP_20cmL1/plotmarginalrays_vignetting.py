import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_hdf('ray_db.hdf', key='df_00')

extreme_norm = np.unique(np.abs(df.px.unique())).max()


px = df.px.values
py = df.py.values

sels = [np.logical_and(px == 0, py==0),
        np.logical_and(px==-extreme_norm, py==0),
        np.logical_and(px==extreme_norm, py==0),
        np.logical_and(px==0, py==extreme_norm),
        np.logical_and(px==0, py==-extreme_norm)]

j = 1
df1 = df.iloc[sels[j]]

fp_max_radius = 75
selx = np.logical_and(df1.x_pos>-fp_max_radius, 
                      df1.x_pos<fp_max_radius)
sely = np.logical_and(df1.y_pos>-fp_max_radius, 
                      df1.y_pos<fp_max_radius)
sel = np.logical_and(selx, sely)
selvig = df1.vignette_code.values == 0
sel = np.logical_and(sel, selvig)

plt.hexbin(df1.x_pos.values[sel],
           df1.y_pos.values[sel],
           df1.vignette_code.values[sel])
plt.colorbar()
plt.show()
