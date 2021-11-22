import zmx_api
import zmx  # noqa
import os

mcerow_variables = [1]

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

MFE = TheSystem.MFE
MCE = TheSystem.MCE

mf_path = os.path.abspath('adjust_circular_stop_MF_envelope.MF')
MFE.LoadMeritFunction(mf_path)

for conf_num in range(1, MCE.NumberOfConfigurations+1):
    TheSystem.Tools.RemoveAllVariables()
    MFE.GetOperandAt(1).GetOperandCell(2).IntegerValue = conf_num
    zmx.set_variables_or_const(mcerow_variables,
                               conf_num,
                               MCE, ZOSAPI, vars=True)
    zmx.zemax_optimize(TheSystem, ZOSAPI)
