# use this to open a 85cam_groups.csv configuration file and
# and to modify a zemax file with one configuration to gneerate the 85 cams.

# after running this, look for the script: set_fields_for_cams [TMP] in ZPL
import clr
import os
import winreg
import time
import pandas as pd
import sys

assert len(sys.argv) == 2  # need to specify a center cam filename

t1 = time.time()
CAMPOS_FNAME = './groups_info/85cam_groups.csv'  # this file needs to be
# in the working dir

# determine the Zemax working directory
aKey = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),
                      r"Software\Zemax", 0, winreg.KEY_READ)
zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
NetHelper = os.path.join(os.sep, zemaxData[0],
                r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')  # noqa
winreg.CloseKey(aKey)

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

if TheApplication.IsValidLicenseForAPI is False:
    raise Exception("License is not valid for ZOSAPI use.  Make sure you have enabled 'Programming > Interactive Extension' from the OpticStudio GUI.")  # noqa

TheSystem = TheApplication.PrimarySystem
if TheSystem is None:
    raise Exception("Unable to acquire Primary system")

print('Connected to OpticStudio')

# The connection should now be ready to use.  For example:
print('Serial #: ', TheApplication.SerialCode)

fname = sys.argv[1]
fname = os.path.abspath(fname)
#fname = r'C:\Users\pgall\Documents\wilson\code\zemax_tools\S4cam\gen85cams\TMP_Sm_FixA_centercam.zmx'  # noqa
print("Opening file: %s" % fname)
TheSystem.LoadFile(fname, False)

TheMCE = TheSystem.MCE
assert TheMCE.NumberOfConfigurations == 1

#  these specify where to put the cameras in the mce
row_cam_centerx = 10
row_cam_centery = 11

row_field_centerx = 2
row_field_centery = 3

scalex = -0.99/250  # approximate scale at focal plane
scaley = 0.99/250

df = pd.read_csv(CAMPOS_FNAME)
df.sort_values('config', inplace=True)

cam_centerxs = df.x.values
cam_centerys = df.y.values
configs = df.config.values


def make_rows_fixed(rows):
    ''' Gets a list of rows and makes the last configuration
    a fixed number in the configuration editor.
    '''
    for row in rows:
        op = TheMCE.GetOperandAt(row)
        config = TheMCE.NumberOfConfigurations
        cell = op.GetCellAt(config)
        cell.MakeSolveFixed()  # make it fixed


def values_from_cam_centers(cam_centerx, cam_centery, scalex, scaley):
    values_to_set = [cam_centerx, cam_centery,
                     scalex * cam_centerx, scaley * cam_centery]
    return values_to_set


def set_values(rows_to_set, values_to_set, TheMCE):
    for j, row in enumerate(rows_to_set):
        op = TheMCE.GetOperandAt(row)
        config = TheMCE.NumberOfConfigurations
        cell = op.GetCellAt(config)
        cell.DoubleValue = values_to_set[j]


#  make rows fixed
rows_to_set = [row_cam_centerx, row_cam_centery,
               row_field_centerx, row_field_centery]

for cam_centerx, cam_centery in zip(cam_centerxs, cam_centerys):
    #  copy current configuration
    TheMCE.AddConfiguration(True)
    values = values_from_cam_centers(cam_centerx, cam_centery,
                                     scalex, scaley)
    make_rows_fixed(rows_to_set)
    set_values(rows_to_set, values, TheMCE)

TheMCE.DeleteConfiguration(1)
t2 = time.time()
print("Took: %1.2f s" % (t2-t1))
