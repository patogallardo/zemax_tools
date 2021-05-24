import pandas as pd
import numpy as np
from zmx_plot import mk_hex

df_groups = pd.read_csv('./groups_info/85cam_groups.csv')
df_fn = pd.read_csv('./f_numbers/f_numbers.csv')


x_mm, y_mm = [], []
for cam in df_fn.cam.values:
    sel = df_groups.config.values == cam
    assert(np.sum(sel) == 1)
    x_mm.append(df_groups.x.values[sel][0])
    y_mm.append(df_groups.y.values[sel][0])
x_mm = np.array(x_mm)
y_mm = np.array(y_mm)
z = df_fn.f_num.values
lower_fn = df_fn.f_num_min.values
upper_fn = df_fn.f_num_max.values

mk_hex(x_mm, y_mm, z, upper_lower=[upper_fn, lower_fn],
       show=False, fig_title="f/#",
       colorbar_label="f/#", plot_fname='./f_numbers/summary_fn')
