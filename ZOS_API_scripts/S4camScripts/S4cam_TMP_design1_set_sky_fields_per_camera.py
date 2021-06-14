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

# Insert Code Here
fnames = glob.glob('*.zmx')
assert len(fnames) == 1
fname = fnames[0]
print("Opening: %s" % fname)
TheSystem.LoadFile(os.path.abspath(fname), False)

surf_wedge = zmx.get_lens_surfaces(TheSystem, material='alumina')[0][0]
mce_rows_sky_fields = [2, 3]

MFE = TheSystem.MFE
mce = TheSystem.MCE

MFE.RemoveOperandsAt(1, MFE.NumberOfOperands)

MFE.AddOperand()
MFE.AddOperand()
MFE.AddOperand()

#  set merit function x, y position
row = MFE.GetOperandAt(2)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAX)
cell = row.GetOperandCell(ZOSAPI.Editors.MFE.MeritColumn.Param1)
cell.IntegerValue = surf_wedge
row.Weight = 1.0

row = MFE.GetOperandAt(3)
row.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAY)
cell = row.GetOperandCell(ZOSAPI.Editors.MFE.MeritColumn.Param1)
cell.IntegerValue = surf_wedge
row.Weight = 1.0

nconfigs = mce.NumberOfConfigurations
for configuration in range(1, nconfigs+1):
    # set variables
    TheSystem.Tools.RemoveAllVariables()
    zmx.set_variables_or_const(mce_rows_sky_fields,
                               configuration, mce, ZOSAPI, vars=True)
    MFE.GetOperandAt(1).GetOperandCell(2).IntegerValue = configuration

    zmx.zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=True)
