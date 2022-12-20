import zmx_api
import zmx
import numpy as np
import math as mt
import os
import matplotlib.pyplot as plt
import argparse
import pandas as pd


TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()
LDE = TheSystem.LDE
MCE = TheSystem.MCE
MFE = TheSystem.MFE

# set configuration in MFE
conf_op = MFE.GetOperandAt(1)
conf_cell = conf_op.GetCellAt(2)
conf = 8
#conf_cell.Value = '%i' % conf only one conf allowed

surfaces_to_mod_thickness = [3, 17, 28, 42]
thickness_sweep_amplitude = [15, 15, 15, 15]
th_names = ['FP-L3 d', 'L3-L2 d', 'L2-L1 d', 'L1-W d']

surfaces_to_mod_tilt_dec = [4, 18, 29, 43]
tilt_dec_name = ['L3', 'L2', 'L1', 'W']
tilt_sweep_amp = [4, 4, 4, 4]
dec_sweep_amp = [40, 40, 40, 40]

N_samples = 101

mf_val = MFE.CalculateMeritFunction()

def do_sweep_thickness(surf_num, amplitude, N_samples):
    val = np.zeros(N_samples)
    pars = np.linspace(-amplitude, amplitude, N_samples)
    for j, par in enumerate(pars):
        LDE.GetSurfaceAt(surf_num).Thickness = par
        val[j] = MFE.CalculateMeritFunction()
    LDE.GetSurfaceAt(surf_num).Thickness = 0.0
    return pars, val

def do_sweep_dec_x(surf_num, amplitude, N_samples):
    val = np.zeros(N_samples)
    pars = np.linspace(-amplitude, amplitude, N_samples)
    cellNum = 12
    for j, par in enumerate(pars):
        LDE.GetSurfaceAt(surf_num).GetSurfaceCell(cellNum).DoubleValue = par
        val[j] = MFE.CalculateMeritFunction()
    LDE.GetSurfaceAt(surf_num).GetSurfaceCell(cellNum).DoubleValue = 0.0
    return pars, val
   
def do_sweep_dec_y(surf_num, amplitude, N_samples):
    val = np.zeros(N_samples)
    pars = np.linspace(-amplitude, amplitude, N_samples)
    cellNum = 13
    for j, par in enumerate(pars):
        LDE.GetSurfaceAt(surf_num).GetSurfaceCell(cellNum).DoubleValue = par
        val[j] = MFE.CalculateMeritFunction()
    LDE.GetSurfaceAt(surf_num).GetSurfaceCell(cellNum).DoubleValue = 0.0
    return pars, val

def do_sweep_tilt_x(surf_num, amplitude, N_samples):
    val = np.zeros(N_samples)
    pars = np.linspace(-amplitude, amplitude, N_samples)
    cellNum = 14
    for j, par in enumerate(pars):
        LDE.GetSurfaceAt(surf_num).GetSurfaceCell(cellNum).DoubleValue = par
        val[j] = MFE.CalculateMeritFunction()
    LDE.GetSurfaceAt(surf_num).GetSurfaceCell(cellNum).DoubleValue = 0.0
    return pars, val

def do_sweep_tilt_y(surf_num, amplitude, N_samples):
    val = np.zeros(N_samples)
    pars = np.linspace(-amplitude, amplitude, N_samples)
    cellNum = 15
    for j, par in enumerate(pars):
        LDE.GetSurfaceAt(surf_num).GetSurfaceCell(cellNum).DoubleValue = par
        val[j] = MFE.CalculateMeritFunction()
    LDE.GetSurfaceAt(surf_num).GetSurfaceCell(cellNum).DoubleValue = 0.0
    return pars, val

# do thickness
ths, v_ths = [], []
for surf_num, amplitude in zip(surfaces_to_mod_thickness, thickness_sweep_amplitude):
    th, v = do_sweep_thickness(surf_num, amplitude, N_samples)
    ths.append(th)
    v_ths.append(v)

# do decx
decxs, v_decx = [], []
for surf_num, amplitude in zip(surfaces_to_mod_tilt_dec, dec_sweep_amp):
    dec, v = do_sweep_dec_x(surf_num, amplitude, N_samples)
    decxs.append(dec)
    v_decx.append(v)


# do decy
decys, v_decy = [], []
for surf_num, amplitude in zip(surfaces_to_mod_tilt_dec, dec_sweep_amp):
    dec, v = do_sweep_dec_y(surf_num+1, amplitude, N_samples)
    decys.append(dec)
    v_decy.append(v)


# do tiltx

tiltxs, v_tiltx = [], []
for surf_num, amplitude in zip(surfaces_to_mod_tilt_dec, tilt_sweep_amp):
    tilt, v = do_sweep_tilt_x(surf_num+2, amplitude, N_samples)
    tiltxs.append(tilt)
    v_tiltx.append(v)

# do tilty

tiltys, v_tilty = [], []
for surf_num, amplitude in zip(surfaces_to_mod_tilt_dec, tilt_sweep_amp):
    tilt, v = do_sweep_tilt_y(surf_num+3, amplitude, N_samples)
    tiltys.append(tilt)
    v_tilty.append(v)


############# Make plots ########################
plt.rcParams.update({"font.size": 18})

plt.figure(figsize=[8, 4.5])

for j in range(len(ths)):
    plt.plot(ths[j], v_ths[j], 
                label=th_names[j],
                ls='--')
ths = ths[0]
v_ths = np.array(v_ths).T

decxs_names = []
for j in range(len(decxs)):
    plt.plot(decxs[j], v_decx[j],
                label='%s dec x' % tilt_dec_name[j])
    decxs_names.append("%s dec x" % tilt_dec_name[j])
decxs = decxs = decxs[0]
v_decx = np.array(v_decx).T

decys_names = []
for j in range(len(decys)):
    plt.plot(decys[j], v_decy[j],
                label='%s dec y' % tilt_dec_name[j])
    decys_names.append("%s dec y" % tilt_dec_name[j])
decys = decys[0]
v_decy = np.array(v_decy).T

plt.axhline(mf_val - 0.05, color='black')
plt.xlim([-15, 15])
plt.ylim([0.85, 0.99])
plt.xlabel('displacement [mm]')
plt.ylabel('Min Strehl [-]')
plt.legend(loc='lower center',
           fontsize=15,
              ncol=3)
plt.tight_layout()
plt.savefig('tel_tol_th_dec_cam_%i.pdf' % conf)
plt.close()

plt.figure(figsize=[8, 4.5])
# plot tilts
tiltxs_names = []
tiltys_names = []
for j in range(len(tiltxs)):
    plt.plot(tiltxs[j], v_tiltx[j],
                label="%s tilt x" % tilt_dec_name[j])
    tiltxs_names.append("%s tilt x" % tilt_dec_name[j])
for j in range(len(tiltys)):
    plt.plot(tiltys[j], v_tilty[j],
                label='%s tilt y' % tilt_dec_name[j])
    tiltys_names.append("%s tilt y" % tilt_dec_name[j])
tiltxs = tiltxs[0]
v_tiltx = np.array(v_tiltx).T
tiltys = tiltys[0]
v_tilty = np.array(v_tilty).T

plt.xlabel('tilt [degrees]')
plt.ylabel('Average Strehl [-]')
plt.axhline(mf_val - 0.05, color='black')
plt.xlim([-4, 4])
plt.ylim([0.85, 0.99])
plt.legend(loc='lower center',
           fontsize=15,
           ncol=3)
plt.tight_layout()
plt.savefig('tel_tol_tilt_conf_%i.pdf' % conf)
plt.savefig('tel_tol_tilt_conf_%i.png' % conf)
plt.close()

data = np.vstack([tiltxs, v_tiltx.T, tiltys, v_tilty.T, ths, v_ths.T, decxs,
                  v_decx.T, decys, v_decy.T])
names = ['tilt x'] + tiltxs_names + ['tilt y'] + tiltys_names + ['thickness'] + th_names + ['dec x'] + decxs_names + ['dec y'] + decys_names

df = pd.DataFrame(data.T, columns=names)
df.to_csv('tol_sweep.csv')