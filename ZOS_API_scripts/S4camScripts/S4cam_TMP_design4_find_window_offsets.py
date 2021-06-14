import zmx_api
import zmx

c = zmx_api.connect_zmx_interactive()
TheSystem, ZOSAPI, ZOSAPI_NetHelper = c
MCE, MFE = TheSystem.MCE, TheSystem.MFE

window_entrance_surface = 28
offset_x_mce_row = 11
offset_y_mce_row = 12
NCONF = MCE.NumberOfConfigurations
NMFEOPERANDS = MFE.NumberOfOperands

# remove all operands
for j in range(1, NMFEOPERANDS + 1):
    MFE.RemoveOperandAt(j)
# end remove all operands

# initialize merit function
for j in range(5):
    MFE.AddOperand()


for currentconf in range(1, NCONF + 1):
    # set conf and remove all vars
    TheSystem.Tools.RemoveAllVariables()
    op = MFE.GetOperandAt(1)
    op.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.CONF)
    op.GetOperandCell(2).IntegerValue = currentconf

    # add REAX operand
    op = MFE.GetOperandAt(2)
    op.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAX)
    op.GetOperandCell(2).IntegerValue = window_entrance_surface
    op.GetOperandCell(3).IntegerValue = 1
    op.Target = 0.0
    op.Weight = 1.0

    # add REAY operand
    op = MFE.GetOperandAt(3)
    op.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAY)
    op.GetOperandCell(2).IntegerValue = window_entrance_surface
    op.GetOperandCell(3).IntegerValue = 1
    op.Target = 0.0
    op.Weight = 1.0

    zmx.set_variables_or_const([offset_x_mce_row, offset_y_mce_row],
                               currentconf,
                               MCE,
                               ZOSAPI,
                               vars=True)

    zmx.zemax_optimize(TheSystem, ZOSAPI)
