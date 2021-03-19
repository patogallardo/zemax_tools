import clr
import os
import winreg
import pandas as pd  # noqa


def export_lens_cad(lens_surf, configuration, lens_name):
    '''Receives the lens surface, configuration and lens name and makes a
    cad file for it'''
    ToolExportCAD = TheSystem.Tools.OpenExportCAD()

    ToolExportCAD.NumberOfRays = 0
    ToolExportCAD.FirstSurface = lens_surf
    ToolExportCAD.LastSurface = lens_surf + 1
    ToolExportCAD.RayLayer = 1
    ToolExportCAD.LensLayer = 0
    ToolExportCAD.DummyThickness = 1
    ToolExportCAD.SplineSegments = ZOSAPI.Tools.General.SplineSegmentsType.N_032  # noqa
    ToolExportCAD.FileType = ZOSAPI.Tools.General.CADFileType.STEP
    ToolExportCAD.SetSingleConfiguration(configuration)

    ToolExportCAD.SurfacesAsSolids = True
    ToolExportCAD.ScatterNSCRays = False
    ToolExportCAD.ExportDummySurfaces = False
    ToolExportCAD.SplitNSCRays = False
    ToolExportCAD.UsePolarization = False

    current_path = os.path.abspath('./')
    target_path = os.path.join(current_path, "CAD")
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    targetFileName = 'conf_%i_%s.STP' % (configuration, lens_name)

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


# Insert Code Here

configuration = 1

import zmx  # noqa

lens_surfaces, lens_curved_surfaces, lens_names = zmx.get_lens_surfaces(TheSystem)  # noqa

for j in range(3):
    lens_surf = lens_surfaces[j]
    lens_name = lens_names[j]
    export_lens_cad(lens_surf, configuration, lens_name)
