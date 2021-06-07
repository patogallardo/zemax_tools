import clr
import os
import winreg
import pandas as pd  # noqa
import glob
import zmx

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

# constants
lyot_surf = 64
mce_row_wedge_rot = 6
mce_row_wedge_tilt = 5

initial_rot = 180
initial_tilt = 1e-2

# Insert Code Here
fnames = glob.glob('*.zmx')
assert len(fnames) == 1
fname = fnames[0]
print("Opening: %s" % fname)
TheSystem.LoadFile(os.path.abspath(fname), False)

MFE = TheSystem.MFE
mce = TheSystem.MCE

MFE.RemoveOperandsAt(1, MFE.NumberOfOperands)

MFE.AddOperand()
MFE.AddOperand()
MFE.AddOperand()
MFE.AddOperand()
MFE.AddOperand()
MFE.AddOperand()

#  set merit function x, y position
row = MFE.GetOperandAt(2)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAX)
cell = row.GetOperandCell(ZOSAPI.Editors.MFE.MeritColumn.Param1)
cell.IntegerValue = lyot_surf
row.Weight = 1.0

row = MFE.GetOperandAt(3)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAY)
cell = row.GetOperandCell(ZOSAPI.Editors.MFE.MeritColumn.Param1)
cell.IntegerValue = lyot_surf
row.Weight = 1.0

row = MFE.GetOperandAt(4)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.MCOL)
row.GetOperandCell(ZOSAPI.Editors.MFE.MeritColumn.Param1).IntegerValue = 8
row.Target = 360
row.Weight = 0

row = MFE.GetOperandAt(5)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.MCOG)
row.GetOperandCell(ZOSAPI.Editors.MFE.MeritColumn.Param1).IntegerValue = 7
row.Target = 0
row.Weight = 100

nconfigs = mce.NumberOfConfigurations
mce_rows_configs = [mce_row_wedge_rot, mce_row_wedge_tilt]
for configuration in range(1, nconfigs+1):
    # set variables
    TheSystem.Tools.RemoveAllVariables()
    zmx.set_variables_or_const(mce_rows_configs,
                               configuration, mce, ZOSAPI, vars=True)
    MFE.GetOperandAt(1).GetOperandCell(2).IntegerValue = configuration
    MFE.GetOperandAt(4).GetOperandCell(3).IntegerValue = configuration
    MFE.GetOperandAt(5).GetOperandCell(3).IntegerValue = configuration

    mce.GetOperandAt(mce_row_wedge_rot).GetOperandCell(configuration).DoubleValue = initial_rot  # noqa
    mce.GetOperandAt(mce_row_wedge_tilt).GetOperandCell(configuration).DoubleValue = initial_tilt  # noqa

    zmx.zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=True)

    # check if tilt is negative and make it positive if so
    mcerow = mce.GetOperandAt(mce_row_wedge_tilt)
    mcecell = mcerow.GetOperandCell(configuration)
    if mcecell.DoubleValue < 0:
        mcecell.DoubleValue = -1.0 * mcecell.DoubleValue
        mcerow = mce.GetOperandAt(mce_row_wedge_rot)
        mcecell = mcerow.GetOperandCell(configuration)
        mcecell.DoubleValue = mcecell.DoubleValue + 180

    # makes the rotation a nice number
    mcerow = mce.GetOperandAt(mce_row_wedge_rot)
    mcecell = mcerow.GetOperandCell(configuration)
    mcecell.DoubleValue = mcecell.DoubleValue % 360.
