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

if not os.path.exists('./fov'):
    os.mkdir('./fov')

for j in range(MFE.NumberOfOperands):
    MFE.RemoveOperandAt(1)

for j in range(30):
    MFE.AddOperand()

row = MFE.GetOperandAt(1)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.CONF)
cell = row.GetOperandCell(2)
cell.IntegerValue = 1

row = MFE.GetOperandAt(2)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.CVIG)

row = MFE.GetOperandAt(3)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.SVIG)

# cosine coordinates
row = MFE.GetOperandAt(4)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAA)
row.GetOperandCell(2).IntegerValue = nsurf
row.GetOperandCell(5).DoubleValue = 1.0

row = MFE.GetOperandAt(5)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAB)
row.GetOperandCell(2).IntegerValue = nsurf
row.GetOperandCell(5).DoubleValue = 1.0


row = MFE.GetOperandAt(6)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAC)
row.GetOperandCell(2).IntegerValue = nsurf
row.GetOperandCell(5).DoubleValue = 1.0


row = MFE.GetOperandAt(8)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAA)
row.GetOperandCell(2).IntegerValue = nsurf
row.GetOperandCell(5).DoubleValue = -1.0


row = MFE.GetOperandAt(9)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAB)
row.GetOperandCell(2).IntegerValue = nsurf
row.GetOperandCell(5).DoubleValue = -1.0


row = MFE.GetOperandAt(10)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAC)
row.GetOperandCell(2).IntegerValue = nsurf
row.GetOperandCell(5).DoubleValue = -1.0



row = MFE.GetOperandAt(12)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.PROD)
row.GetOperandCell(2).IntegerValue = 4
row.GetOperandCell(3).IntegerValue = 8

row = MFE.GetOperandAt(13)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.PROD)
row.GetOperandCell(2).IntegerValue = 5
row.GetOperandCell(3).IntegerValue = 9


row = MFE.GetOperandAt(14)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.PROD)
row.GetOperandCell(2).IntegerValue = 6
row.GetOperandCell(3).IntegerValue = 10


row = MFE.GetOperandAt(16)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.OSUM)
row.GetOperandCell(2).IntegerValue = 12
row.GetOperandCell(3).IntegerValue = 14


row = MFE.GetOperandAt(17)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.ACOS)
row.GetOperandCell(2).IntegerValue = 16
row.GetOperandCell(3).IntegerValue = 1


values = []
for j in progressbar(range(1, MCE.NumberOfConfigurations + 2)):
    row = MFE.GetOperandAt(1)
    row.GetOperandCell(2).IntegerValue = j

    MFE.CalculateMeritFunction()
    row = MFE.GetOperandAt(17)
    values.append(row.Value)

values = np.array(values)
np.savez('fov/fov.npz', full_fov=values)

df = pd.DataFrame({"fov": values})


plt.hist(values, color='black', histtype='step')
plt.xlabel('Full FoV [deg]')
plt.ylabel('Camera count [-]')
plt.savefig('./fov/fov_hist.pdf')
df.fov.describe().to_csv("fov/fov_summary.csv")
