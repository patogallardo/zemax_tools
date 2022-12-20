import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.size': 18})
df = pd.read_csv('./sweep/tol_sweep.csv')
LABELFS = 11

StrehlNominal =df['L1 tilt x'][np.where(df['tilt x'].values == 0)[0][0]] 

fig_size = np.array([6, 7])
fig = plt.figure(constrained_layout=True, figsize=fig_size)
axs = fig.subplots(3)

ax = axs[0]
ax.plot(df['thickness'],
         df['FP-L3 d'],
         label='FP-L3 dist')
ax.plot(df['thickness'],
         df['L3-L2 d'],
         label='L3-L2 dist')
ax.plot(df['thickness'],
         df['L2-L1 d'],
         label='L2-L1 dist')
ax.plot(df['thickness'],
        df['L1-W d'],
        label='L1- Wed d')

ax.plot(df['dec x'],
        df['L1 dec x'],
        label='L1 dec x')
ax.plot(df['dec x'],
        df['L2 dec x'],
        label='L2 dec x')
ax.plot(df['dec x'],
        df['L3 dec x'],
        label='L3 dec x')

ax.plot(df['dec y'],
        df['L1 dec y'],
        label='L1 dec y')
ax.plot(df['dec y'],
        df['L2 dec y'],
        label='L2 dec y')
ax.plot(df['dec y'],
        df['L3 dec y'],
        label='L3 dec y')
ax.axhline(StrehlNominal - 0.05,
           color='black',
           label='5% degradation')
ax.legend(ncol=3, fontsize=LABELFS, loc='lower center')
ax.set_xlabel('Displacement [mm]')
ax.set_ylabel('Avg Strehl [-]')
ax.set_ylim([0.80, 0.98])
ax.set_xlim([-10, 10])


ax = axs[1]
ax.plot(df['tilt x'],
        df['L1 tilt x'],
        label='L1 tilt x')
ax.plot(df['tilt x'],
        df['L2 tilt x'],
        label='L2 tilt x')
ax.plot(df['tilt x'],
        df['L3 tilt x'],
        label='L3 tilt x')
ax.plot(df['tilt x'],
        df['W tilt x'],
        label='W tilt x')

ax.plot(df['tilt y'],
        df['L1 tilt y'],
        label='L1 tilt y')
ax.plot(df['tilt y'],
        df['L2 tilt y'],
        label='L2 tilt y')
ax.plot(df['tilt y'],
        df['L3 tilt y'],
        label='L3 tilt y')
ax.plot(df['tilt y'],
        df['W tilt y'],
        label='W tilt y')

ax.axhline(StrehlNominal - 0.05,
           color='black',
           label='5% degradation')

ax.set_xlabel('Tilt [degrees]')
ax.set_ylabel('Avg Strehl [-]')
ax.legend(loc='lower center',
          ncol=3, fontsize=LABELFS)
ax.set_ylim([0.80, 0.98])
ax.set_xlim([-4, 4])

ax = axs[2]
df_mc = pd.read_excel('./MC_suggestedvalues.xls')
BINS = np.arange(0.86, 1.0, 0.005)
ax.hist(df_mc.strehl,
        cumulative=False, density=False, histtype='step',
        color='black',
        ls='-',
        label='Without refocus',
        bins=BINS)
ax.set_xlabel('Avg Strehl ratio [-]')
ax.set_ylabel('Count [-]')
ax.ticklabel_format(scilimits=(-2, 2))

#df_comp = pd.read_excel('../MC_withcomp.xlsx')
#ax.hist(df_comp.Strehl,
#        cumulative=False, density=False, histtype='step',
#        color='black', ls='-',
#        label='With refocus',
#        bins=BINS)

ax.axvline(StrehlNominal - 0.05,
           label='5% Strehl degradation')

ax.legend(loc='upper left', fontsize=LABELFS)

plt.savefig('cam8_tolerancing_3panels.pdf')
plt.close()
