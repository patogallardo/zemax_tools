import clr
import os
import winreg
import pandas as pd  # noqa
import glob


def export_cad(rays, TheSystem):
    '''Receives the lens surface, configuration and lens name and makes a
    cad file for it'''
    ToolExportCAD = TheSystem.Tools.OpenExportCAD()
    nsurf = TheSystem.LDE.NumberOfSurfaces
    if rays:
        ToolExportCAD.NumberOfRays = 5
    else:
        ToolExportCAD.NumberOfRays = 0
    ToolExportCAD.FirstSurface = 1
    ToolExportCAD.LastSurface = nsurf
    ToolExportCAD.RayLayer = 0
    ToolExportCAD.LensLayer = 0
    ToolExportCAD.DummyThickness = 1
    ToolExportCAD.SplineSegments = ZOSAPI.Tools.General.SplineSegmentsType.N_032  # noqa
    ToolExportCAD.FileType = ZOSAPI.Tools.General.CADFileType.STEP
    ToolExportCAD.SetSingleConfiguration(1)

    ToolExportCAD.SurfacesAsSolids = True
    ToolExportCAD.ScatterNSCRays = False
    ToolExportCAD.ExportDummySurfaces = False
    ToolExportCAD.SplitNSCRays = False
    ToolExportCAD.UsePolarization = False

    current_path = os.path.abspath('./')
    target_path = os.path.join(current_path, "CAD")
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    if rays:
        targetFileName = 'lat_cad_withrays.STP'
    else:
        targetFileName = 'lat_cad_norays.STP'

    ToolExportCAD.OutputFileName = os.path.join(target_path, targetFileName)
    print('Starting exporting...')

    ToolExportCAD.Run()
    runstatus = ToolExportCAD.WaitWithTimeout(float(3 * 60))

    # Report the status
    if runstatus == ZOSAPI.Tools.RunStatus.Completed:
        print('Completed!')
    elif runstatus == ZOSAPI.Tools.RunStatus.FailedToStart:
        print('Failed To Start!')
    elif runstatus == ZOSAPI.Tools.RunStatus.InvalidTimeout:
        print('Invalid Timeout')
    else:
        print('Timed Out!')

    print('Progress: ', ToolExportCAD.Progress)
    # If the exporting is not completed and can be cancelled, cancel the work
    if (runstatus != ZOSAPI.Tools.RunStatus.Completed and ToolExportCAD.CanCancel):  # noqa
        ToolExportCAD.Cancel()
    # Close the tool
    ToolExportCAD.Close()


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

fnames = glob.glob('*.zmx')
assert len(fnames) == 1
print("Loading \n%s" % fnames[0])
TheSystem.LoadFile(os.path.abspath(fnames[0]), False)
# Insert Code Here

import zmx  # noqa

export_cad(rays=True, TheSystem=TheSystem)
export_cad(rays=False, TheSystem=TheSystem)
