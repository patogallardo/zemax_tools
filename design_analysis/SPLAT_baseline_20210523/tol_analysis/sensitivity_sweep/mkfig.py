import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.size': 18})
df = pd.read_csv('tol_sweep.csv')
LABELFS = 11

StrehlNominal =df['FP tilt x'][np.where(df['tilt x'].values == 0)[0][0]] 

fig_size = np.array([6, 7])
fig = plt.figure(constrained_layout=True, figsize=fig_size)
axs = fig.subplots(3)

ax = axs[0]
ax.plot(df['thickness'],
         df['M1-M2 dist'],
         label='M1-M2 dist')
ax.plot(df['thickness'],
         df['M2-M3 dist'],
         label='M2-M3 dist')
ax.plot(df['thickness'],
         df['M3-FP dist'],
         label='M3-FP dist')
ax.plot(df['dec x'],
        df['M2 dec x'],
        label='M2 dec x')
ax.plot(df['dec x'],
        df['M3 dec x'],
        label='M3 dec x')
ax.plot(df['dec y'],
        df['M2 dec y'],
        label='M2 dec y')
ax.plot(df['dec y'],
        df['M3 dec y'],
        label='M3 dec y')
ax.axhline(StrehlNominal - 0.05,
           color='black',
           label='5% degradation')
ax.legend(ncol=3, fontsize=LABELFS, loc='lower center')
ax.set_xlabel('Displacement [mm]')
ax.set_ylabel('Min Strehl [-]')
ax.set_ylim([0.80, 0.96])


ax = axs[1]
ax.plot(df['tilt x'],
        df['M2 tilt x'],
        label='M2 tilt x')
ax.plot(df['tilt x'],
        df['M3 tilt x'],
        label='M3 tilt x')
ax.plot(df['tilt y'],
        df['M2 tilt y'],
        label='M2 tilt y')
ax.plot(df['tilt y'],
        df['M3 tilt y'],
        label='M3 tilt y')
ax.plot(df['tilt x'],
        df['FP tilt x'],
        label='FP tilt x')
ax.plot(df['tilt y'],
        df['FP tilt y'],
        label='FP tilt y')

ax.axhline(StrehlNominal - 0.05,
           color='black',
           label='5% degradation')

ax.set_xlabel('Tilt [degrees]')
ax.set_ylabel('Min Strehl [-]')
ax.legend(loc='lower center',
          ncol=3, fontsize=LABELFS)
ax.set_ylim([0.80, 0.96])

ax = axs[2]
df_mc = pd.read_excel('../montecarlo/sim_res_suggested_spread.xls')
BINS = np.arange(0.87, 0.97, 0.005)
ax.hist(df_mc.strehl,
        cumulative=False, density=False, histtype='step',
        color='black',
        ls='--',
        label='Without refocus',
        bins=BINS)
ax.set_xlabel('Min Strehl ratio [-]')
ax.set_ylabel('Count [-]')
ax.ticklabel_format(scilimits=(-2, 2))

df_comp = pd.read_excel('../montecarlo_withcompensation/MC_withcomp.xlsx')
ax.hist(df_comp.Strehl,
        cumulative=False, density=False, histtype='step',
        color='black', ls='-',
        label='With refocus',
        bins=BINS)

ax.axvline(StrehlNominal - 0.05,
         label='5% Strehl degradation')

ax.legend(loc='upper left', fontsize=LABELFS)

plt.savefig('tel_tolerancing_3panels.pdf')
plt.close()
