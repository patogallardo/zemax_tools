import pandas as pd
import matplotlib.pyplot as plt
import sys
print("Usage mk_hist.py fname.xls")

SHOW = False

MF_val = 0.05442
fname = sys.argv[1]
df = pd.read_excel(fname)

plt.rcParams.update({"font.size":18})
fig, ax = plt.subplots(figsize=[8, 4.5])
ax.hist(df["strehl"], bins=20, cumulative=False, density=False,
        histtype='step', color='black')
ax.axvline(1 - MF_val - 0.05, label='5% Strehl degradation')

ax.set_xlabel('Strehl[-]')
ax.set_ylabel('counts [-]')
ax.legend(loc='lower right',
          fontsize=15)

percentiles = [0.5-.95/2, 0.5-.68/2, 0.5, 0.5+0.68/2, 0.5+.95/2]
s = df.strehl.describe(percentiles=percentiles).to_string(float_format="%1.2f")
print(s)
ax.text(0.05, 0.95, s,
        transform=ax.transAxes,
        va='top',
        bbox=dict(alpha=0.95, facecolor='white'),
        fontsize=10)
plt.grid()
plt.tight_layout()


if SHOW:
    plt.show()
else:
    label = fname.split('.')[0]
    plt.savefig('hist_mc_%s.png' % label, dpi=120)
    plt.savefig('hist_mc_%s.pdf' % label)
    plt.savefig('C:\\Users\\pgall\\OneDrive - The University of Chicago\\Github\\SPLAT_paper\\figures\\hist_mc.pdf')  # noqa
    plt.close()
