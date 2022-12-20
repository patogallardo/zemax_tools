import zmx_api
import zmx
import numpy as np
import math as mt
import matplotlib.pyplot as plt


TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()
MFE = TheSystem.MFE

MFE_rows = [16, 17, 20]
diameter = 188

def set_diameter(MFE_rows, diameter):
    cons = np.array([0, 0, -0.1])
    targets = np.ones(3) * diameter + cons

    for j, MFE_row in enumerate(MFE_rows):
        row = MFE.GetOperandAt(MFE_row)
        row.Target = targets[j]

diameters = np.arange(165, 205, 5)
fnums_center = np.zeros(len(diameters))
fnums_side_p = np.zeros(len(diameters))
fnums_side_m = np.zeros(len(diameters))

for j in range(len(diameters)):
    set_diameter(MFE_rows, diameters[j])
    zmx.zemax_optimize(TheSystem, ZOSAPI)

    value_row = 39
    value_fnum = MFE.GetOperandAt(value_row).Value
    fnums_center[j] = value_fnum

    print("f_num_center: %1.2f" % value_fnum)
    value_row = 45
    value_fnum = MFE.GetOperandAt(value_row).Value
    fnums_side_p[j] = value_fnum

    value_row = 51
    value_fnum = MFE.GetOperandAt(value_row).Value
    fnums_side_m[j] = value_fnum


plt.title('L1 diameter, L3:180 mm dia')
plt.plot(diameters, fnums_center,
            label='fnum_center_field',
            ls='-', marker= 'o')
plt.plot(diameters, fnums_side_p,
            label='fnum_marginal1',
            ls='-', marker='o')
plt.plot(diameters, fnums_side_m,
            label='fnum_marginal2',
            ls= '-', marker='o')
plt.axvline(193, color='black',
            label='mech dia')
plt.axvline(173, color='gray',
            label='10mm clr')
plt.axvline(183, color='darkgray',
            label='5mm clr')
plt.xlabel('diameter [mm]')
plt.ylabel('f number [-]')
plt.grid()
plt.legend()
plt.savefig("f_numbs.png", dpi=120)
plt.savefig("f_numbs.pdf")
