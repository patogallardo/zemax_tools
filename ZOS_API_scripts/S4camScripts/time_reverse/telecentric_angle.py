# exports fov data
import numpy as np
import zmx_api
import os
import matplotlib.pyplot as plt
import pandas as pd
from progressbar import progressbar
# import pandas as pd

c = zmx_api.connect_zmx_interactive()
TheSystem, ZOSAPI, ZOSAPI_NetHelper = c
MCE = TheSystem.MCE
MFE = TheSystem.MFE
LDE = TheSystem.LDE

nsurf = LDE.NumberOfSurfaces
NRINGS = 5
NARMS = 12
NCAMS = MCE.NumberOfConfigurations
Rs = np.linspace(0, 1, NRINGS)
angle = np.linspace(0, 2 * np.pi, NARMS + 1)

output_dir = "./telecentric_angle"
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

for j in range(MFE.NumberOfOperands):
    MFE.RemoveOperandAt(1)

for j in range(NRINGS * NARMS + 30):
    MFE.AddOperand()

row = MFE.GetOperandAt(1)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.CONF)
cell = row.GetOperandCell(2)
cell.IntegerValue = 1

row = MFE.GetOperandAt(2)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.CVIG)

row = MFE.GetOperandAt(3)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.SVIG)


row_number = 4
for nring in range(1, NRINGS):
    for narm in range(NARMS):
        row = MFE.GetOperandAt(row_number)
        row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.RAED)
        row.GetOperandCell(2).IntegerValue = 1  # surf
        row.GetOperandCell(3).IntegerValue = 1  # wave

        row.GetOperandCell(4).DoubleValue = np.cos(angle[narm]) * Rs[nring]
        row.GetOperandCell(5).DoubleValue = np.sin(angle[narm]) * Rs[nring]
        row.GetOperandCell(6).DoubleValue = 0  # Px
        row.GetOperandCell(7).DoubleValue = 0  # Py
        row_number += 1

row = MFE.GetOperandAt(row_number)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.RAED)
row.GetOperandCell(2).IntegerValue = 1  # surf
row.GetOperandCell(3).IntegerValue = 1  # wave

row.GetOperandCell(4).DoubleValue = 0
row.GetOperandCell(5).DoubleValue = 0
row.GetOperandCell(6).DoubleValue = 0  # Px
row.GetOperandCell(7).DoubleValue = 0  # Py

AllCamValues = []
for nconf in progressbar(range(1, NCAMS + 1)):
    this_iteration_values = np.zeros(NARMS * (NRINGS-1) + 1)
    row = MFE.GetOperandAt(1)
    row.GetOperandCell(2).IntegerValue = nconf
    MFE.CalculateMeritFunction()

    for j in range(NARMS * (NRINGS - 1) + 1):
        this_iteration_values[j] = MFE.GetOperandAt(j + 4).Value
    AllCamValues.append(this_iteration_values)

AllCamValues = np.array(AllCamValues)
print("Max angle: %1.3f" % AllCamValues.max())
print("Min angle: %1.3f" % AllCamValues.min())
