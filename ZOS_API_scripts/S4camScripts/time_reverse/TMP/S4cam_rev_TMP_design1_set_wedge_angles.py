import zmx_api
import zmx

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

MCE = TheSystem.MCE
MFE = TheSystem.MFE

nconf = TheSystem.MCE.NumberOfConfigurations

mce_rows_to_vary = [1, 17, 18, 20, 21]


for configuration in range(1, nconf + 1):
    o = MFE.GetOperandAt(1)
    c = o.GetCellAt(2)
    c.IntegerValue = configuration

    TheSystem.Tools.RemoveAllVariables()
    zmx.set_variables_or_const(mce_rows_to_vary, configuration,
                               MCE, ZOSAPI, vars=True)
    zmx.zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=True)
