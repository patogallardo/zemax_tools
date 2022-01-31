import zmx_api
import zmx  # noqa
from progressbar import progressbar
import os
import numpy as np

mce_rows_to_optimize = [1, 2, 3, 19, 20]

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()
TheSystem.LoadFile('circular_stop/TMP_baseline_rev_multicam_test4_elliptical_2groups_groupleaders_8_39.zos', False)  # noqa

MFE = TheSystem.MFE
MCE = TheSystem.MCE
MF_DIROUT = './center_pri_footprint/'

Nconf = 85
# Nconf = 10


def do_we_need_to_reoptimize(MFE):
    """returns True if we need to reoptimize.
       returns False if we reached a viable solution.
    """
    # check that we found a solution and run optimizer again if not
    MFE.CalculateMeritFunction()
    Nop = MFE.NumberOfOperands
    REOPTIMIZE = False
    for j in range(6):
        op = MFE.GetOperandAt(Nop - j)
        contribution = op.Contribution
        print("Contribution %i: %1.2e" % (j, contribution))
        REOPTIMIZE = REOPTIMIZE or (contribution > 1e-7)
    op_margin = MFE.GetOperandAt(Nop - 7)
    reached_target = np.isclose(op_margin.Value,
                                op_margin.Target, atol=10)
    print("Margin: %1.2e" % op_margin.Value)
    REOPTIMIZE = REOPTIMIZE or not reached_target

    op_equa = MFE.GetOperandAt(Nop - 8)
    reached_target = op_equa.Value < 10
    print("Avg Deviation from edge shape: %1.2f" % op_equa.Value)
    REOPTIMIZE = REOPTIMIZE or not reached_target
    return REOPTIMIZE


for active_conf in progressbar(range(1, Nconf + 1)):
    mf_fnameout = os.path.abspath(os.path.join(MF_DIROUT,
                                  "MF_conf%02i.MF" % active_conf))
    MFE.LoadMeritFunction(mf_fnameout)
    TheSystem.Tools.RemoveAllVariables()

    op_svig = MFE.GetOperandAt(6)
    op_svig.GetOperandCell(2).IntegerValue = 1

    zmx.set_variables_or_const(mce_rows_to_optimize,
                               active_conf,
                               MCE, ZOSAPI, vars=True)
    zmx.zemax_optimize(TheSystem, ZOSAPI,
                       algorithm="DLS")

    REOPTIMIZE = do_we_need_to_reoptimize(MFE)
    if REOPTIMIZE:
        print("reoptimizing...")
        zmx.set_variables_or_const(mce_rows_to_optimize,
                                   active_conf,
                                   MCE, ZOSAPI, vars=True)
        zmx.zemax_optimize(TheSystem, ZOSAPI,
                           algorithm="OD",
                           CyclesAuto=True)

        REOPTIMIZE = do_we_need_to_reoptimize(MFE)
        if REOPTIMIZE:
            print("reoptimizing...")
            zmx.set_variables_or_const(mce_rows_to_optimize,
                                       active_conf,
                                       MCE, ZOSAPI, vars=True)
            zmx.zemax_optimize(TheSystem, ZOSAPI,
                               algorithm="DLS",
                               CyclesAuto=True)
            REOPTIMIZE = do_we_need_to_reoptimize(MFE)
            if REOPTIMIZE:
                print("reoptimizing one last time...")
                zmx.set_variables_or_const(mce_rows_to_optimize,
                                           active_conf,
                                           MCE, ZOSAPI, vars=True)
                zmx.zemax_run_hammer(TheSystem,
                                     time_s=15 * 60)

if not os.path.exists('./elliptical_stop'):
    os.mkdir('./elliptical_stop')
fnameout = os.path.join(os.path.abspath("./"),
                        "elliptical_stop\\elliptical_stop_set.zos")
TheSystem.SaveAs(fnameout)
