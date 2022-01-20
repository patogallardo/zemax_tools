import zmx_api
import zmx  # noqa
from progressbar import progressbar

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

MFE = TheSystem.MFE
MCE = TheSystem.MCE

Nconf = MCE.NumberOfConfigurations
rows_to_set = [1, 2, 3]
values = [38, 38, 0]
row_pickup = 2
row_to_mirror = 1

# Nconf = 1 # comment out for debug
for conf in progressbar(range(1, Nconf + 1)):
    for j, row in enumerate(rows_to_set):
        operand_row = MCE.GetOperandAt(row)
        cell = operand_row.GetOperandCell(conf)
        cell.DoubleValue = values[j]

for conf in progressbar(range(1, Nconf + 1)):
    operand_row = MCE.GetOperandAt(row_pickup)
    cell = operand_row.GetOperandCell(conf)
    ConfigPickupSolve = cell.CreateSolveType(ZOSAPI.Editors.SolveType.ConfigPickup)  # noqa
    ConfigPickupSolve._S_ConfigPickup.Configuration = conf
    ConfigPickupSolve._S_ConfigPickup.Operand = row_to_mirror
    cell.SetSolveData(ConfigPickupSolve)
