import zmx_api
import zmx


def prepare_MF(MFE):
    MFE.RemoveOperandsAt(1, MFE.NumberOfOperands)

    for j in range(10):
        MFE.AddOperand()


def add_operands(MFE):
    #  set merit function x, y position
    surf_wedge = zmx.get_lens_surfaces(TheSystem, material='alumina')[0][0]

    row = MFE.GetOperandAt(2)
    row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.CVIG)

    row = MFE.GetOperandAt(3)
    row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.SVIG)

    row = MFE.GetOperandAt(4)
    row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAX)
    cell = row.GetOperandCell(ZOSAPI.Editors.MFE.MeritColumn.Param1)
    cell.IntegerValue = 46
    row.Weight = 1.0

    row = MFE.GetOperandAt(5)
    row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAY)
    cell = row.GetOperandCell(ZOSAPI.Editors.MFE.MeritColumn.Param1)
    cell.IntegerValue = 46
    row.Weight = 1.0

    row = MFE.GetOperandAt(6)
    row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.PMGT)
    cell = row.GetOperandCell(ZOSAPI.Editors.MFE.MeritColumn.Param1)
    cell.IntegerValue = 17
    cell = row.GetOperandCell(ZOSAPI.Editors.MFE.MeritColumn.Param2)
    cell.IntegerValue = 2
    row.Weight = 1.0e10


def set_to_zero(MCE, mce_rows_to_vary, conf, initialcond):
    for j, mce_row in enumerate(mce_rows_to_vary):
        op = MCE.GetOperandAt(mce_row)
        op.GetOperandCell(conf).DoubleValue = initialcond[j]


TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

MCE = TheSystem.MCE
MFE = TheSystem.MFE

nconf = TheSystem.MCE.NumberOfConfigurations

mce_rows_to_vary = [22, 23]
initialcond = [0, 1e-5]

prepare_MF(MFE)
add_operands(MFE)


#  nconf = 1
for configuration in range(1, nconf + 1):
    o = MFE.GetOperandAt(1)
    c = o.GetCellAt(2)
    c.IntegerValue = configuration

    TheSystem.Tools.RemoveAllVariables()
    zmx.set_variables_or_const(mce_rows_to_vary, configuration,
                               MCE, ZOSAPI, vars=True)
    set_to_zero(MCE, mce_rows_to_vary, configuration, initialcond)
    zmx.zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=True)
