import clr
import os
import winreg
import pandas as pd
import sys
import glob
from progressbar import progressbar
import numpy as np

CyclesAuto = True  # how many cycles True takes the most time
RUN_OPTIMIZER = True
RUN_OPTIMIZER2ndRound = False
RUN_OPTIMIZER3rdRound = False
hammer_time_s = 0


def zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=True):
    print('\nRunning Local Optimization')
    LocalOpt = TheSystem.Tools.OpenLocalOptimization()
    print("\t Initial Merit Function: %1.10f" % LocalOpt.InitialMeritFunction)
    LocalOpt.Algorithm = ZOSAPI.Tools.Optimization.OptimizationAlgorithm.DampedLeastSquares  # noqa
    OptCycles = ZOSAPI.Tools.Optimization.OptimizationCycles
    if CyclesAuto:
        LocalOpt.Cycles = OptCycles.Automatic
    else:
        LocalOpt.Cycles = OptCycles.Fixed_5_Cycles  # noqa
#        LocalOpt.Cycles = OptCycles.Fixed_50_Cycles  # noqa
#        LocalOpt.Cycles = OptCycles.Fixed_10_Cycles
    LocalOpt.NumberOfCores = 8
    LocalOpt.RunAndWaitForCompletion()
    print("\t Final Merit Function: %1.10f" % LocalOpt.CurrentMeritFunction)
    LocalOpt.Close()


def zemax_run_hammer(TheSystem, time_s=120):
    print('\nRunning Hammer Optimization')
    HammerOpt = TheSystem.Tools.OpenHammerOptimization()
    print('\tInitial Merit Function: % 1.10f' % HammerOpt.InitialMeritFunction)
    HammerOpt.RunAndWaitWithTimeout(time_s)
    HammerOpt.Cancel()
    HammerOpt.WaitForCompletion()
    print("Final Merit Function: %1.10f" % HammerOpt.CurrentMeritFunction)
    HammerOpt.Close()


def set_variables_or_const(mcerow_variables, conf, mce, ZOSAPI, vars=True):
    for mcerow_variable in mcerow_variables:
        mcerow = mce.GetOperandAt(mcerow_variable)  # set variables
        mcecell = mcerow.GetOperandCell(conf)
        if vars:
            solve = mcecell.CreateSolveType(ZOSAPI.Editors.SolveType.Variable)  # noqa
        else:
            solve = mcecell.CreateSolveType(ZOSAPI.Editors.SolveType.Fixed)
        mcecell.SetSolveData(solve)


def set_rows_zero(mcerow_zeros, conf, mce, ZOSAPI):
    for mce_row in mcerow_zeros:
        mcerow = mce.GetOperandAt(mce_row)
        mcecell = mcerow.GetOperandCell(conf)
        mcecell.DoubleValue = 0.0


def set_rows_constant(df, conf, mce, ZOSAPI):
    mcerows = df.mcerow.values
    initial_values = df.initial_value.values

    for j, mce_row in enumerate(mcerows):
        zmx_mce_row = mce.GetOperandAt(mce_row)
        mcecell = zmx_mce_row.GetOperandCell(conf)
        mcecell.DoubleValue = initial_values[j]


aKey = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),
                      r"Software\Zemax", 0, winreg.KEY_READ)
zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
NetHelper = os.path.join(os.sep, zemaxData[0],
                         r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
winreg.CloseKey(aKey)

# add the NetHelper DLL for locating the OpticStudio install folder
clr.AddReference(NetHelper)
import ZOSAPI_NetHelper  # noqa

pathToInstall = ''
success = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(pathToInstall)

zemaxDir = ''
if success:
    zemaxDir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory()
    print('Found OpticStudio at:   %s' + zemaxDir)
else:
    raise Exception('Cannot find OpticStudio')

# load the ZOS-API assemblies
clr.AddReference(os.path.join(os.sep, zemaxDir, r'ZOSAPI.dll'))
clr.AddReference(os.path.join(os.sep, zemaxDir, r'ZOSAPI_Interfaces.dll'))
import ZOSAPI  # noqa

TheConnection = ZOSAPI.ZOSAPI_Connection()
if TheConnection is None:
    raise Exception("Unable to intialize NET connection to ZOSAPI")

TheApplication = TheConnection.ConnectAsExtension(0)
if TheApplication is None:
    raise Exception("Unable to acquire ZOSAPI application")


if TheApplication.IsValidLicenseForAPI==False:  # noqa
    raise Exception("License is not valid for ZOSAPI use."
                    "  Make sure you have enabled 'Programming"
                    " > Interactive Extension' from the OpticStudio GUI.")

TheSystem = TheApplication.PrimarySystem
if TheSystem is None:
    raise Exception("Unable to acquire Primary system")
print('Connected to OpticStudio')

# The connection should now be ready to use.  For example:
print('Serial #: ', TheApplication.SerialCode)

# Insert Code Here
mce = TheSystem.MCE
mfe = TheSystem.MFE

if len(sys.argv) == 2:
    mf_path = sys.argv[1]
else:
    mf_path = glob.glob('groups_info/*.MF')
    mf_path = os.path.abspath(mf_path[0])

assert len(glob.glob('groups_info/initial_values_it1.csv')) == 1
assert len(glob.glob('groups_info/initial_values_it2.csv')) == 1

print("using merit function in:\n%s" % mf_path)
#
group_leaders = pd.read_csv('./groups_info/group_leaders.csv').leader.values
groups = pd.read_csv('./groups_info/group_leaders.csv').group.values
df_variables = pd.read_csv('groups_info/variables.csv')
df_group_info = pd.read_csv('groups_info/85cam_groups.csv')
mcerow_variables_first_it = df_variables.mcerow_variable_first_it.values
mcerow_variables_second_it = df_variables.mcerow_variable_second_it.values
mcerow_variables_third_it = df_variables.mcerow_variable_third_it.values

mcerow_variables_first_it = mcerow_variables_first_it[np.isfinite(mcerow_variables_first_it)].astype(int)  # noqa
mcerow_variables_second_it = mcerow_variables_second_it[np.isfinite(mcerow_variables_second_it)].astype(int)  # noqa
mcerow_variables_third_it = mcerow_variables_third_it[np.isfinite(mcerow_variables_third_it)].astype(int)  # noqa
df_initial_values_it1 = pd.read_csv('groups_info/initial_values_it1.csv')
df_initial_values_it2 = pd.read_csv('groups_info/initial_values_it2.csv')

#  swap configuration, load merit function and set it to evaluate the leader
for j, group_leader in progressbar(enumerate(group_leaders)):
    group_leader = group_leaders[j]  # evaluate this configuration
    current_group = df_group_info.query(
                        'config == %i' % group_leader).group.values[0]  # noqa
    print("\n*************************************************************")
    print("Running on group %i" % current_group)
    mce.SetCurrentConfiguration(group_leader)
    mfe.LoadMeritFunction(mf_path)

    # point to the configuration to evaluate, rm all vars and set the lowest
    # conf to variable
    mfe.GetOperandAt(1).GetOperandCell(2).IntegerValue = group_leader  # evalgl
    TheSystem.Tools.RemoveAllVariables()
    conf_to_vary = df_group_info.query('group == %i' % current_group).config.min()  # noqa

    # First iteration set variables to optimize and initial values
    set_variables_or_const(mcerow_variables_first_it, conf_to_vary,
                           mce, ZOSAPI, vars=True)
    set_rows_constant(df_initial_values_it1, conf_to_vary, mce, ZOSAPI)

    if RUN_OPTIMIZER:
        print("First round of optimization")
        zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=CyclesAuto)
        if hammer_time_s > 0:
            zemax_run_hammer(TheSystem, time_s=hammer_time_s)
            zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=CyclesAuto)
    TheSystem.Tools.RemoveAllVariables()

    if RUN_OPTIMIZER and RUN_OPTIMIZER2ndRound:
        print('Second round of optimization')
        set_variables_or_const(mcerow_variables_second_it, conf_to_vary,
                               mce, ZOSAPI, vars=True)
        set_rows_constant(df_initial_values_it2, conf_to_vary, mce, ZOSAPI)
        zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=CyclesAuto)
        for j in range(1):
            zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=CyclesAuto)

    if RUN_OPTIMIZER and RUN_OPTIMIZER3rdRound:
        print("Third round of optimization")
        set_variables_or_const(mcerow_variables_third_it, conf_to_vary,
                               mce, ZOSAPI, vars=True)
        for j in range(3):
            zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=CyclesAuto)

    TheSystem.Tools.RemoveAllVariables()
TheSystem.Save()
