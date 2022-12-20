import zmx_api
import zmx  # noqa
from progressbar import progressbar
import os
import numpy as np

mce_rows_to_optimize = [1, 19, 20]
PRECISE_VIGNETTING = True

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

MFE = TheSystem.MFE
MCE = TheSystem.MCE
MF_DIROUT = './center_pri_footprint/'

Nconf = 85
# Nconf = 7

for active_conf in progressbar(range(1, Nconf + 1)):
    mf_fnameout = os.path.abspath(os.path.join(MF_DIROUT,
                                  "MF_conf%02i.MF" % active_conf))
    MFE.LoadMeritFunction(mf_fnameout)

    op_svig = MFE.GetOperandAt(6)
    op_svig.GetOperandCell(2).IntegerValue = 1

# check that we found a solution and run optimizer again if not
    MFE.CalculateMeritFunction()
    Nop = MFE.NumberOfOperands
    FAILED = False
    for j in range(4):
        op = MFE.GetOperandAt(Nop - j)
        contribution = op.Contribution
        FAILED = FAILED or (contribution > 1e-7)
        if contribution > 1e-7:
            print("contribution %i: contribution %1.2e" % (j,
                                           contribution)) # noqa
    op_margin = MFE.GetOperandAt(Nop - 5)
    reached_target = np.isclose(op_margin.Value,
                                op_margin.Target, atol=10)
    FAILED = FAILED or not reached_target

    if FAILED:
        print("\nFAILED_CAM: %i" % active_conf)
        TheSystem.Tools.RemoveAllVariables()
        zmx.set_variables_or_const(mce_rows_to_optimize,
                                   active_conf,
                                   MCE, ZOSAPI, vars=True)
        zmx.zemax_run_hammer(TheSystem,
                             time_s=900)
