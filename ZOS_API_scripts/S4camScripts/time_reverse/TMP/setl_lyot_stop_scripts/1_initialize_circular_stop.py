import zmx_api
import zmx  # noqa
from progressbar import progressbar

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

MFE = TheSystem.MFE
MCE = TheSystem.MCE

Nconf = MCE.NumberOfConfigurations
rows_to_set = [1]
values = [35]

# Nconf = 1 # comment out for debug
for conf in progressbar(range(1, Nconf + 1)):
    for j, row in enumerate(rows_to_set):
        operand_row = MCE.GetOperandAt(row)
        cell = operand_row.GetOperandCell(conf)
        cell.DoubleValue = values[j]

# These were deleted, file needs to have a circular aperture, and 
# SDIA 6 operand needs to be in row 1 if you want to make 
# a circular aperture design.


#for conf in progressbar(range(1, Nconf + 1)):
#    operand_row = MCE.GetOperandAt(row_pickup)
#    cell = operand_row.GetOperandCell(conf)
#    ConfigPickupSolve = cell.CreateSolveType(ZOSAPI.Editors.SolveType.ConfigPickup)  # noqa
#    ConfigPickupSolve._S_ConfigPickup.Configuration = conf
#    ConfigPickupSolve._S_ConfigPickup.Operand = row_to_mirror
#    cell.SetSolveData(ConfigPickupSolve)
