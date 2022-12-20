import zmx_api
import zmx  # noqa
from progressbar import progressbar
import os  # noqa


TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

print("Working on current file. You should save when done.")

MFE = TheSystem.MFE
MCE = TheSystem.MCE
Fields = TheSystem.SystemData.Fields
NumFields = Fields.NumberOfFields

Nconf = 85
MCE_row_start = 27
if MCE.NumberOfOperands > MCE_row_start:
    print("Deleting operands...")
    for j in progressbar(range(MCE.NumberOfOperands - MCE_row_start + 1)):
        MCE.RemoveOperandAt(MCE_row_start)

MCE.AddOperand()

print("Adding MC operands...")
for fieldNum in progressbar(range(NumFields)):
    row = MCE.AddOperand()
    row.ChangeType(ZOSAPI.Editors.MCE.MultiConfigOperandType.FTAN)
    row.Param1 = fieldNum

    row = MCE.AddOperand()
    row.ChangeType(ZOSAPI.Editors.MCE.MultiConfigOperandType.FVCX)
    row.Param1 = fieldNum

    row = MCE.AddOperand()
    row.ChangeType(ZOSAPI.Editors.MCE.MultiConfigOperandType.FVCY)
    row.Param1 = fieldNum

    row = MCE.AddOperand()
    row.ChangeType(ZOSAPI.Editors.MCE.MultiConfigOperandType.FVDX)
    row.Param1 = fieldNum

    row = MCE.AddOperand()
    row.ChangeType(ZOSAPI.Editors.MCE.MultiConfigOperandType.FVDY)
    row.Param1 = fieldNum

print("Setting vignetting...")
for active_conf in progressbar(range(1, Nconf + 1)):
    MCE.SetCurrentConfiguration(active_conf)
    Fields.ClearVignetting()
    Fields.SetVignetting()
