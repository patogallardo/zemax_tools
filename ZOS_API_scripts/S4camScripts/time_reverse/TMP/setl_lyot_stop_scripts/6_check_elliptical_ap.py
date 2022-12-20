import zmx_api
import zmx  # noqa
from progressbar import progressbar
import os
import numpy as np

mce_rows_to_optimize = [1, 2, 3, 19, 20]
PRECISE_VIGNETTING = True

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

MFE = TheSystem.MFE
MCE = TheSystem.MCE
MF_DIROUT = './center_pri_footprint/'

Nconf = 85
# Nconf = 7


def vary_vars(MCE, mce_rows_to_optimize, active_conf):
    print("Varying a bit starting point")
    op1_row = MCE.GetOperandAt(mce_rows_to_optimize[0])
    cell1 = op1_row.GetOperandCell(active_conf)
    cell1.DoubleValue = cell1.DoubleValue - 1.0
    cell1.DoubleValue = 38.0

    op2_row = MCE.GetOperandAt(mce_rows_to_optimize[1])
    cell2 = op2_row.GetOperandCell(active_conf)
    cell2.DoubleValue = cell2.DoubleValue - 1.0
    cell2.DoubleValue = 38.0

#    op3_row = MCE.GetOperandAt(mce_rows_to_optimize[2])
#    cell3 = op3_row.GetOperandCell(active_conf)
#    cell3.DoubleValue = 0.0


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
                                op_margin.Target, atol=20)
    print("Margin: %1.2e" % op_margin.Value)
    REOPTIMIZE = REOPTIMIZE or not reached_target

    op_equa = MFE.GetOperandAt(Nop - 8)
    reached_target = op_equa.Value < 20
    print("Avg Deviation from edge shape: %1.2f" % op_equa.Value)
    REOPTIMIZE = REOPTIMIZE or not reached_target
    if REOPTIMIZE:
        print("Not OK.")
    else:
        print("Passed, OK.")
    return REOPTIMIZE


for active_conf in progressbar(range(1, Nconf + 1)):
    mf_fnameout = os.path.abspath(os.path.join(MF_DIROUT,
                                  "MF_conf%02i.MF" % active_conf))
    MFE.LoadMeritFunction(mf_fnameout)
    TheSystem.Tools.RemoveAllVariables()

    op_svig = MFE.GetOperandAt(6)
    op_svig.GetOperandCell(2).IntegerValue = 1

# check that we found a solution and run optimizer again if not
    REOPTIMIZE = do_we_need_to_reoptimize(MFE)

    if REOPTIMIZE:
        print("Reoptimizing:")
        print("\nFAILED_CAM: %i" % active_conf)
        vary_vars(MCE, mce_rows_to_optimize, active_conf)
        TheSystem.Tools.RemoveAllVariables()
        zmx.set_variables_or_const(mce_rows_to_optimize,
                                   active_conf,
                                   MCE, ZOSAPI, vars=True)
        zmx.zemax_optimize(TheSystem, ZOSAPI,
                           algorithm='DLS',
                           CyclesAuto=False)
        zmx.zemax_optimize(TheSystem, ZOSAPI,
                           algorithm='DLS',
                           CyclesAuto=False)

        REOPTIMIZE = do_we_need_to_reoptimize(MFE)

        if REOPTIMIZE:
            print("Reoptimizing:")
            print("\nFAILED_CAM: %i" % active_conf)
            #vary_vars(MCE, mce_rows_to_optimize, active_conf)
            TheSystem.Tools.RemoveAllVariables()
            zmx.set_variables_or_const(mce_rows_to_optimize,
                                       active_conf,
                                       MCE, ZOSAPI, vars=True)
            zmx.zemax_optimize(TheSystem, ZOSAPI,
                               algorithm='DLS',
                               CyclesAuto=True)
            REOPTIMIZE = do_we_need_to_reoptimize(MFE)
            if REOPTIMIZE:
                print("Reoptimizing cam %i:" % active_conf)
#                vary_vars(MCE, mce_rows_to_optimize, active_conf)
                TheSystem.Tools.RemoveAllVariables()
                zmx.set_variables_or_const(mce_rows_to_optimize,
                                           active_conf,
                                           MCE, ZOSAPI, vars=True)
                zmx.zemax_optimize(TheSystem, ZOSAPI,
                                   algorithm='OD',
                                   CyclesAuto=False)
                REOPTIMIZE = do_we_need_to_reoptimize(MFE)
                if REOPTIMIZE:
                    print("Reoptimizing cam %i:" % active_conf)
                    print("I'm giving up after this!")
                    vary_vars(MCE, mce_rows_to_optimize, active_conf)
                    TheSystem.Tools.RemoveAllVariables()
                    zmx.set_variables_or_const(mce_rows_to_optimize,
                                               active_conf,
                                               MCE, ZOSAPI, vars=True)
                    zmx.zemax_optimize(TheSystem, ZOSAPI,
                                       algorithm='DSL',
                                       CyclesAuto=True)
