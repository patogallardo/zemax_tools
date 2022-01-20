import zmx_api
import zmx  # noqa
from progressbar import progressbar
import os

mce_rows_to_optimize = [1, 19, 20]

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

MFE = TheSystem.MFE
MCE = TheSystem.MCE
MF_DIROUT = './center_pri_footprint/'

for active_conf in progressbar(range(1, 86)):
    mf_fnameout = os.path.abspath(os.path.join(MF_DIROUT,
                                  "MF_conf%02i.MF" % active_conf))
    MFE.LoadMeritFunction(mf_fnameout)
    TheSystem.Tools.RemoveAllVariables()
    zmx.set_variables_or_const(mce_rows_to_optimize,
                               active_conf,
                               MCE, ZOSAPI, vars=True)
    zmx.zemax_optimize(TheSystem, ZOSAPI)
