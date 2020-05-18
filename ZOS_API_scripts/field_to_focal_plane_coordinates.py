''' From TMA design, export rays from normalized sky coordinates to focal plane coordinates.


'''

from win32com.client.gencache import EnsureDispatch, EnsureModule
from win32com.client import CastTo, constants
from win32com.client import gencache
import os
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import pandas as pd

fname = sys.argv[1]
fname = os.path.abspath(fname)

print("opening %s" %fname)

#parameters of the extraction

hx_min = -6.5/14.5
hx_max = 6.5/14.5
hy_min = -14.5/14.5
hy_max = -6.0/14.5
N_points = 300

meshgrid = np.meshgrid(np.linspace(hx_min, hx_max, N_points), np.linspace(hy_min, hy_max, N_points))

hx_arr = meshgrid[0].flatten()
hy_arr = meshgrid[1].flatten()
assert len(hx_arr) == len(hy_arr)

#end parameters

# Notes
#
# The python project and script was tested with the following tools:
#       Python 3.4.3 for Windows (32-bit) (https://www.python.org/downloads/) - Python interpreter
#       Python for Windows Extensions (32-bit, Python 3.4) (http://sourceforge.net/projects/pywin32/) - for COM support
#       Microsoft Visual Studio Express 2013 for Windows Desktop (https://www.visualstudio.com/en-us/products/visual-studio-express-vs.aspx) - easy-to-use IDE
#       Python Tools for Visual Studio (https://pytools.codeplex.com/) - integration into Visual Studio
#
# Note that Visual Studio and Python Tools make development easier, however this python script should should run without either installed.

class PythonStandaloneApplication(object):
    class LicenseException(Exception):
        pass

    class ConnectionException(Exception):
        pass

    class InitializationException(Exception):
        pass

    class SystemNotPresentException(Exception):
        pass

    def __init__(self):
        # make sure the Python wrappers are available for the COM client and
        # interfaces
        gencache.EnsureModule('{EA433010-2BAC-43C4-857C-7AEAC4A8CCE0}', 0, 1, 0)
        gencache.EnsureModule('{F66684D7-AAFE-4A62-9156-FF7A7853F764}', 0, 1, 0)
        # Note - the above can also be accomplished using 'makepy.py' in the
        # following directory:
        #      {PythonEnv}\Lib\site-packages\wind32com\client\
        # Also note that the generate wrappers do not get refreshed when the
        # COM library changes.
        # To refresh the wrappers, you can manually delete everything in the
        # cache directory:
        #	   {PythonEnv}\Lib\site-packages\win32com\gen_py\*.*
        
        self.TheConnection = EnsureDispatch("ZOSAPI.ZOSAPI_Connection")
        if self.TheConnection is None:
            raise PythonStandaloneApplication.ConnectionException("Unable to intialize COM connection to ZOSAPI")

        self.TheApplication = self.TheConnection.CreateNewApplication()
        if self.TheApplication is None:
            raise PythonStandaloneApplication.InitializationException("Unable to acquire ZOSAPI application")

        if self.TheApplication.IsValidLicenseForAPI == False:
            raise PythonStandaloneApplication.LicenseException("License is not valid for ZOSAPI use")

        self.TheSystem = self.TheApplication.PrimarySystem
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException("Unable to acquire Primary system")

    def __del__(self):
        if self.TheApplication is not None:
            self.TheApplication.CloseApplication()
            self.TheApplication = None

        self.TheConnection = None

    def OpenFile(self, filepath, saveIfNeeded):
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException("Unable to acquire Primary system")
        self.TheSystem.LoadFile(filepath, saveIfNeeded)

    def CloseFile(self, save):
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException("Unable to acquire Primary system")
        self.TheSystem.Close(save)

    def SamplesDir(self):
        if self.TheApplication is None:
            raise PythonStandaloneApplication.InitializationException("Unable to acquire ZOSAPI application")

        return self.TheApplication.SamplesDir

    def ExampleConstants(self):
        if self.TheApplication.LicenseStatus is constants.LicenseStatusType_PremiumEdition:
            return "Premium"
        elif self.TheApplication.LicenseStatus is constants.LicenseStatusType_ProfessionalEdition:
            return "Professional"
        elif self.TheApplication.LicenseStatus is constants.LicenseStatusType_StandardEdition:
            return "Standard"
        else:
            return "Invalid"


if __name__ == '__main__':
    zosapi = PythonStandaloneApplication()
    value = zosapi.ExampleConstants()

    if not os.path.exists(zosapi.TheApplication.SamplesDir + "\\API\\Python"):
        os.makedirs(zosapi.TheApplication.SamplesDir + "\\API\\Python")

    TheSystem = zosapi.TheSystem
    TheApplication = zosapi.TheApplication

    # Set up primary optical system
    sampleDir = TheApplication.SamplesDir
    testFile = fname
    TheSystem.LoadFile(testFile, False)

    #! [e22s01_py]
    # Set up Batch Ray Trace
    raytrace = TheSystem.Tools.OpenBatchRayTrace()
    nsur = TheSystem.LDE.NumberOfSurfaces
#    max_rays = 30
    normUnPolData = raytrace.CreateNormUnpol(len(hx_arr), constants.RaysType_Real, nsur)
    #! [e22s01_py]

    #! [e22s02_py]
    # Define batch ray trace constants
#    max_wave = TheSystem.SystemData.Wavelengths.NumberOfWavelengths
    num_fields = TheSystem.SystemData.Fields.NumberOfFields
    #! [e22s02_py]

    # Initialize x/y image plane arrays
    x_ary = np.empty([len(hx_arr)])
    y_ary = np.empty([len(hy_arr)])

    #! [e22s03_py]
    # Determine maximum field in Y only
    max_field = 0.0
    for i in range(1, num_fields + 1):
        if (abs(TheSystem.SystemData.Fields.GetField(i).Y) > max_field):
            max_field = abs(TheSystem.SystemData.Fields.GetField(i).Y)
    #! [e22s03_py]

    if TheSystem.SystemData.Fields.GetFieldType() == constants.FieldType_Angle:
        field_type = 'Angle'
    elif TheSystem.SystemData.Fields.GetFieldType() == constants.FieldType_ObjectHeight:
        field_type = 'Height'
    elif TheSystem.SystemData.Fields.GetFieldType() == constants.FieldType_ParaxialImageHeight:
        field_type = 'Height'
    elif TheSystem.SystemData.Fields.GetFieldType() == constants.FieldType_RealImageHeight:
        field_type = 'Height'


            # Adding Rays to Batch, varying normalised object height hy
    normUnPolData.ClearData()
    waveNumber = 1
    px, py = 0, 0

    for j in range(len(hx_arr)):
        normUnPolData.AddRay(waveNumber, hx_arr[j], hy_arr[j], px, py, constants.OPDMode_None)
            #! [e22s04_py]
    
    print('running raytrace...')
    baseTool = CastTo(raytrace, 'ISystemTool')
    baseTool.RunAndWaitForCompletion()

            #! [e22s05_py]
            # Read batch raytrace and display results
    normUnPolData.StartReadingResults()
    output = normUnPolData.ReadNextResult()

    j=0
    while output[0]:                                                    # success
        if ((output[2] == 0) and (output[3] == 0)):                     # ErrorCode & vignetteCode
            x_ary[j] = output[4]   # X
            y_ary[j] = output[5]   # Y
        else:
            x_ary[j] = np.nan
            y_ary[j] = np.nan
        output = normUnPolData.ReadNextResult()
        j += 1

    print("Ray: hx, hy = %1.3e, %1.3e" % (hx_arr[0], hy_arr[0]))
    print("x: %1.3e" % x_ary[0])
    print("y: %1.3e" % y_ary[0])
    #! [e22s07_py]

    hx_deg = max_field * hx_arr
    hy_deg = max_field * hy_arr

    package = {'hx_deg': hx_deg, 'hy_deg': hy_deg, 'x_pos': x_ary, 'y_pos': y_ary}
    df = pd.DataFrame(package)
    df.to_csv('%s_field_positions.csv' % (fname.split('\\')[-1].split('.zmx')[0]))

    # This will clean up the connection to OpticStudio.
    # Note that it closes down the server instance of OpticStudio, so you for maximum performance do not do
    # this until you need to.
    del zosapi
    zosapi = None

    
    # place plt.show() after clean up to release OpticStudio from memory
