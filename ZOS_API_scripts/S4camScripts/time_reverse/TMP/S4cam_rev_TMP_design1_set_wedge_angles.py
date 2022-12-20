import zmx_api
import zmx
import os

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

MCE = TheSystem.MCE
MFE = TheSystem.MFE

nconf = TheSystem.MCE.NumberOfConfigurations

mce_rows_to_vary = [19, 20, 22, 23]

MFE.RemoveOperandsAt(1, MFE.NumberOfOperands)
mf_fname = os.path.join(os.path.abspath('./groups_info/'),
         'rough_prism_window_offset_align.MF')
MFE.LoadMeritFunction(mf_fname)

for configuration in range(1, nconf + 1):
    o = MFE.GetOperandAt(1)
    c = o.GetCellAt(2)
    c.IntegerValue = configuration

    TheSystem.Tools.RemoveAllVariables()
    zmx.set_variables_or_const(mce_rows_to_vary, configuration,
                               MCE, ZOSAPI, vars=True)
    zmx.zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=True)
