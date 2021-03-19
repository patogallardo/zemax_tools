'''From a TMA design, export polynomial definition to a
pickle file that can be processed later.

see: export_poly_surfaces2.py for postprocessing. '''

import clr
import os
import winreg
import matplotlib.pyplot as plt  # noqa
import sys
import pandas as pd
import glob

configuration = 1

if len(sys.argv) == 2:  # optional support for specifying filename
    fname = sys.argv[1]
else:
    print('No file name provided, searching current directory')
    fnames = glob.glob('*.zmx')
    assert len(fnames) == 1
    fname = fnames[0]
projectName = fname
fname = os.path.abspath(fname)
print("opening: %s" % fname)


# check output dirs
dir_out = "CAD/surface_definitions"
if not os.path.exists('CAD'):
    os.mkdir("CAD")
if not os.path.exists(dir_out):
    os.mkdir(dir_out)


class PythonStandaloneApplication(object):
    class LicenseException(Exception):
        pass

    class ConnectionException(Exception):
        pass

    class InitializationException(Exception):
        pass

    class SystemNotPresentException(Exception):
        pass

    def __init__(self, path=None):
        # determine location of ZOSAPI_NetHelper.dll & add as reference
        aKey = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER), r"Software\Zemax", 0, winreg.KEY_READ)  # noqa
        zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
        NetHelper = os.path.join(os.sep, zemaxData[0],
                                 r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
        winreg.CloseKey(aKey)
        clr.AddReference(NetHelper)
        import ZOSAPI_NetHelper

        # Find the installed version of OpticStudio
        if path is None:
            isInitialized = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize()
        else:
            # Note -- uncomment the following line to use a custom initialization path  # noqa
            isInitialized = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(path)  # noqa

        # determine the ZOS root directory
        if isInitialized:
            dir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory()
        else:
            raise PythonStandaloneApplication.InitializationException("Unable to locate Zemax OpticStudio.  Try using a hard-coded path.")  # noqa

        # add ZOS-API referencecs
        clr.AddReference(os.path.join(os.sep, dir, "ZOSAPI.dll"))
        clr.AddReference(os.path.join(os.sep, dir, "ZOSAPI_Interfaces.dll"))
        import ZOSAPI

        # create a reference to the API namespace
        self.ZOSAPI = ZOSAPI

        # create a reference to the API namespace
        self.ZOSAPI = ZOSAPI

        # Create the initial connection class
        self.TheConnection = ZOSAPI.ZOSAPI_Connection()

        if self.TheConnection is None:
            raise PythonStandaloneApplication.ConnectionException("Unable to initialize .NET connection to ZOSAPI")  # noqa

        self.TheApplication = self.TheConnection.CreateNewApplication()
        if self.TheApplication is None:
            raise PythonStandaloneApplication.InitializationException("Unable to acquire ZOSAPI application")  # noqa

        if self.TheApplication.IsValidLicenseForAPI == False:  # noqa
            raise PythonStandaloneApplication.LicenseException("License is not valid for ZOSAPI use")  # noqa

        self.TheSystem = self.TheApplication.PrimarySystem
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException("Unable to acquire Primary system")  # noqa

    def __del__(self):
        if self.TheApplication is not None:
            self.TheApplication.CloseApplication()
            self.TheApplication = None

        self.TheConnection = None

    def OpenFile(self, filepath, saveIfNeeded):
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException("Unable to acquire Primary system")  # noqa
        self.TheSystem.LoadFile(filepath, saveIfNeeded)

    def CloseFile(self, save):
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException("Unable to acquire Primary system")  # noqa
        self.TheSystem.Close(save)

    def SamplesDir(self):
        if self.TheApplication is None:
            raise PythonStandaloneApplication.InitializationException("Unable to acquire ZOSAPI application")  # noqa

        return self.TheApplication.SamplesDir

    def ExampleConstants(self):
        if self.TheApplication.LicenseStatus == self.ZOSAPI.LicenseStatusType.PremiumEdition:  # noqa
            return "Premium"
        elif self.TheApplication.LicenseStatus == self.ZOSAPI.LicenseStatusTypeProfessionalEdition:  # noqa
            return "Professional"
        elif self.TheApplication.LicenseStatus == self.ZOSAPI.LicenseStatusTypeStandardEdition:   # noqa
            return "Standard"
        else:
            return "Invalid"


if __name__ == '__main__':
    zos = PythonStandaloneApplication()
    # use http://matplotlib.org/ to plot 2D graph
    # need to install this package before running this code

    # load local variables
    zosapi = zos.ZOSAPI
    TheApplication = zos.TheApplication
    TheSystem = zos.TheSystem
    sampleDir = TheApplication.SamplesDir

    # Set up primary optical system
    testFile = fname
    TheSystem.LoadFile(testFile, False)

    TheSystem.MCE.SetCurrentConfiguration(configuration)

    nsur = TheSystem.LDE.NumberOfSurfaces

    # explore surfaces and extract mirror names and surface numbers
    TheLDE = TheSystem.LDE

    lens_surfaces = []
    lens_names = []
#   identify mirror names and surface numbers
    for j in range(1, nsur):
        if TheLDE.GetSurfaceAt(j).Material == 'SILICON_COLD':
            lens_surfaces.append(j)
            lens_names.append(TheLDE.GetSurfaceAt(j).Comment)
#   Extract all the mirror cells up to Ncol
    assert len(lens_surfaces) == 3
    lens_surfaces[1] = lens_surfaces[1] + 1  # second lens curved on the back
    Ncol = 100
    lenses_data = []
    apertures = []  # aperture objects

    for lensSurface in lens_surfaces:  # iterate over mirrors
        s = TheLDE.GetSurfaceAt(lensSurface)

        TypeName = s.TypeName

        colNames = ['SurfType']
        colValues = [TypeName]

        for col in range(1, Ncol):  # iterate over columns
            c = s.GetSurfaceCell(col)
            if "(unused)" not in c.Header:
                colNames.append(c.Header)
                if c.DataType == 0:
                    colval = c.IntegerValue
                elif c.DataType == 1:
                    colval = c.DoubleValue
                else:
                    colval = c.Value
                colValues.append(colval)
        lens_data = pd.Series(colValues, index=colNames)
        lenses_data.append(lens_data)

    fname_out = 'lens_surface_data'
    df = pd.DataFrame(lenses_data)
    df.to_csv(os.path.join(dir_out, fname_out + '.csv'))
