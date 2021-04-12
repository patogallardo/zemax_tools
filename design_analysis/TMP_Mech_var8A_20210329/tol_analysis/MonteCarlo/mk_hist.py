import pandas as pd
import matplotlib.pyplot as plt

SHOW = False

fname = 'sim_res.xls'
df = pd.read_excel(fname)

plt.hist(df["strehl"], bins=20, cumulative=False, density=False,
         histtype='step', color='black')
plt.axvline(1 - 0.02632998 - 0.05, label='5% Strehl degradation')
plt.xlabel('strehl[-]')
plt.ylabel('counts [-]')
plt.legend()

plt.grid()


if SHOW:
    plt.show()
else:
    plt.savefig('hist_mc.png', dpi=120)
    plt.close()
