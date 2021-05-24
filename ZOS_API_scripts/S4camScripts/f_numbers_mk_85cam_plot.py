import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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


s = pd.Series(z)
table = s.describe(percentiles=[.10, .50, .90]).to_latex(float_format="%1.2f")
table = table.replace('\\toprule', '')
table = table.replace('\\bottomrule', '')
table = table.replace('\\midrule', '')
table = table.replace('\n', " ")
table = table.replace(' 0 ', '')


plt.rcParams.update({
    "text.usetex": True})
plt.figure(figsize=[8, 4.5])
plt.hist(z, histtype='step', color='black', bins=15)
plt.xlabel('$f/\\#$')
plt.ylabel('camera count')
plt.title('Camera f-numbers')
plt.figtext(0.7, 0.7, table)

plt.savefig('f_numbers/cam_fnumbers_hist.png', dpi=150)
plt.savefig('f_numbers/cam_fnumbers_hist.pdf', dpi=150)
plt.close()
