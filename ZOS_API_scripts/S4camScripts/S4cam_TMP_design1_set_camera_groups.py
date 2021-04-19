'''Interactive extension script.
This script takes one zmx file with 85 configurations and one csv file
wich contains the grouping information.

It sets the pickups that tie the first configuration in the group with
the rest of configurations in that group.

Which configuration operands are mirrored is controlled in the list
rows_to_mirror defined below.

Remember that in the future we will want to make this homogeneous between
the CD and TMP design, for which we will need to add more rows in the
TMP multiconfiguration file.
'''
import clr, os, winreg  # noqa
import pandas as pd
import progressbar
import numpy as np
# rows to miror: number of configuration row to pickup from the first
# configuration in the group. Use this to set which configurations
# pickup the value in the only configuration that is being optimized.
df_variables = pd.read_csv('groups_info/variables.csv')
mce_row_vars_1it = df_variables.mcerow_variable_first_it.values
mce_row_vars_2it = df_variables.mcerow_variable_second_it.values
mce_row_vars_1it = mce_row_vars_1it[np.isfinite(mce_row_vars_1it)]
mce_row_vars_1it = mce_row_vars_1it.astype(int)
mce_row_vars_2it = mce_row_vars_2it.astype(int)

rows_to_mirror = np.sort(np.append(mce_row_vars_1it, mce_row_vars_2it))

# This boilerplate requires the 'pythonnet' module.
# The following instructions are for installing the 'pythonnet' module via pip:
#    1. Ensure you are running Python 3.4, 3.5, 3.6, or 3.7. PythonNET does not work with Python 3.8 yet.  # noqa
#    2. Install 'pythonnet' from pip via a command prompt (type 'cmd' from the start menu or press Windows + R and type 'cmd' then enter)  # noqa
#
#        python -m pip install pythonnet

# determine the Zemax working directory
aKey = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),
                      r"Software\Zemax", 0, winreg.KEY_READ)  # noqa
zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
NetHelper = os.path.join(os.sep, zemaxData[0],
                         r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
winreg.CloseKey(aKey)

# add the NetHelper DLL for locating the OpticStudio install folder
clr.AddReference(NetHelper)
import ZOSAPI_NetHelper  # noqa

pathToInstall = ''
# uncomment the following line to use a specific instance of the ZOS-API
# assemblies pathToInstall = r'C:\C:\Program Files\Zemax OpticStudio'

# connect to OpticStudio
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
    raise Exception("License is not valid for ZOSAPI use."
                    "  Make sure you have enabled 'Programming"
                    "> Interactive Extension' from the OpticStudio GUI.")

TheSystem = TheApplication.PrimarySystem
if TheSystem is None:
    raise Exception("Unable to acquire Primary system")
print('Connected to OpticStudio')

# The connection should now be ready to use.  For example:
print('Serial #: ', TheApplication.SerialCode)

# Insert Code Here
TheMCE = TheSystem.MCE
nconfs = TheMCE.NumberOfConfigurations


def setpickup(conf_row, conf_col, target_conf, TheMCE=TheMCE):
    '''Sets pickup, needs:
    conf_row: configuration number to set the pickup
    conf_col: configuration column to set the pickup
    target_conf: configuration that we are copying
    TheMCE: the MCE
    '''
    mce_row = TheMCE.GetOperandAt(conf_row)
    mce_cell = mce_row.GetOperandCell(conf_col)
    ConfigPickupSolve = mce_cell.CreateSolveType(
                    ZOSAPI.Editors.SolveType.ConfigPickup)  # noqa
    ConfigPickupSolve.Configuration = target_conf
    ConfigPickupSolve.Operand = conf_row
    mce_cell.SetSolveData(ConfigPickupSolve)


def setconstant(row_to_mirror, target_conf, TheMCE=TheMCE):
    '''Sets to constant the first configuration in the group.
    NOTE: in zemax, pickups need to go from a high number to a low conf
    number, this means that all the followers in a group need to refer to
    the lowest configuration number in that group.
    '''
    mce_row = TheMCE.GetOperandAt(row_to_mirror)
    mce_cell = mce_row.GetOperandCell(target_conf)
    ConfigFixedSolve = mce_cell.CreateSolveType(
                ZOSAPI.Editors.SolveType.Fixed)  # noqa
    mce_cell.SetSolveData(ConfigFixedSolve)


def set_constants(target_conf, rows_to_mirror=rows_to_mirror):
    '''Sets one configuration operand to a constant value.'''
    for row_to_mirror in rows_to_mirror:
        setconstant(row_to_mirror, target_conf)


def set_pickups(confs_to_set_pickup, target_conf,
                rows_to_mirror=rows_to_mirror):
    for conf_to_set_pickup in progressbar.progressbar(confs_to_set_pickup):
        for row_to_mirror in rows_to_mirror:
            setpickup(row_to_mirror, conf_to_set_pickup,
                      target_conf)


df = pd.read_csv('./groups_info/85cam_groups.csv')
groups = df.group.unique()

for groupnumber in groups:  # set group leader fixed
    df_currentgroup = df.query('group==%i' % groups[groupnumber])
    set_constants(target_conf=df_currentgroup.config.values[0],
                  rows_to_mirror=rows_to_mirror)

for j, groupnumber in enumerate(groups):  # set pickups
    df_currentgroup = df.query('group==%i' % groups[groupnumber])
    set_pickups(confs_to_set_pickup=df_currentgroup.config.values[1:],
                target_conf=df_currentgroup.config.values[0])
