import clr
import os
import winreg
import pandas as pd
import numpy as np
import sys
import glob
from progressbar import progressbar

CyclesAuto = False  # how many cycles True takes the most time
RUN_OPTIMIZER = True
START_FROM_ZEROS = True


def zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=True):
    print('Running Local Optimization')
    LocalOpt = TheSystem.Tools.OpenLocalOptimization()
    LocalOpt.Algorithm = ZOSAPI.Tools.Optimization.OptimizationAlgorithm.DampedLeastSquares  # noqa
    OptCycles = ZOSAPI.Tools.Optimization.OptimizationCycles
    if CyclesAuto:
        LocalOpt.Cycles = OptCycles.Automatic
    else:
        LocalOpt.Cycles = OptCycles.Fixed_5_Cycles
    LocalOpt.NumberOfCores = 8
    LocalOpt.RunAndWaitForCompletion()
    LocalOpt.Close()


def set_variables_or_const(mcerow_variables, conf, mce, ZOSAPI, vars=True):
    for mcerow_variable in mcerow_variables:
        mcerow = mce.GetOperandAt(mcerow_variable)  # set variables
        mcecell = mcerow.GetOperandCell(conf_to_vary)
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
print("using merit function in:\n%s" % mf_path)
#
group_leaders = pd.read_csv('./groups_info/group_leaders.csv').leader.values
groups = pd.read_csv('./groups_info/group_leaders.csv').group.values
df_variables = pd.read_csv('groups_info/variables.csv')
df_group_info = pd.read_csv('groups_info/85cam_groups.csv')
mcerow_variables = df_variables.mcerow_variable.values  # noqa
mcerow_zeros = df_variables.mcerow_zero.values[np.isfinite(df_variables.mcerow_zero.values)].astype(int)  # noqa


#  swap configuration, load merit function and set it to evaluate the leader
for j, group_leader in progressbar(enumerate(group_leaders)):
    group_leader = group_leaders[j]  # evaluate this configuration
    current_group = df_group_info.query(
                        'config == %i' % group_leader).group.values[0]  # noqa
    print("Running on group %i" % current_group)
    mce.SetCurrentConfiguration(group_leader)
    mfe.LoadMeritFunction(mf_path)

    # point to the configuration to evaluate, rm all vars and set the lowest
    # conf to variable
    mfe.GetOperandAt(1).GetOperandCell(2).IntegerValue = group_leader  # evalgl
    TheSystem.Tools.RemoveAllVariables()
    conf_to_vary = df_group_info.query('group == %i' % current_group).config.min()  # noqa

    # iterate over mcerow_variables to set the list to variables
    set_variables_or_const(mcerow_variables, conf_to_vary,
                           mce, ZOSAPI, vars=True)

    if START_FROM_ZEROS:
        set_variables_or_const(mcerow_zeros, conf_to_vary,
                               mce, ZOSAPI, vars=False)
        set_rows_zero(mcerow_zeros, conf_to_vary, mce, ZOSAPI)

    if RUN_OPTIMIZER:
        zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=False)

    set_variables_or_const(mcerow_variables, conf_to_vary,
                           mce, ZOSAPI, vars=True)

    if RUN_OPTIMIZER:
        zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=CyclesAuto)
