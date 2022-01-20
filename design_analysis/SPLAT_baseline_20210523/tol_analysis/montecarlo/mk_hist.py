import pandas as pd
import matplotlib.pyplot as plt

SHOW = False

fname = 'sim_res.xls'
df = pd.read_excel(fname)

fig, ax = plt.subplots()
ax.hist(df["strehl"], bins=20, cumulative=False, density=False,
        histtype='step', color='black')
ax.axvline(1 - 0.030411 - 0.05, label='5% Strehl degradation')

ax.set_xlabel('Strehl[-]')
ax.set_ylabel('counts [-]')
ax.legend()

percentiles = [0.5-.95/2, 0.5-.68/2, 0.5, 0.5+0.68/2, 0.5+.95/2]
s = df.strehl.describe(percentiles=percentiles).to_string(float_format="%1.2f")
print(s)
ax.text(0.05, 0.95, s,
        transform=ax.transAxes,
        va='top',
        bbox=dict(alpha=0.95, facecolor='white'))
plt.grid()


if SHOW:
    plt.show()
else:
    plt.savefig('hist_mc.png', dpi=120)
    plt.savefig('hist_mc.pdf')
    plt.savefig('C:\\Users\\pgall\\OneDrive - The University of Chicago\\Github\\SPLAT_paper\\figures\\hist_mc.pdf')  # noqa
    plt.close()
