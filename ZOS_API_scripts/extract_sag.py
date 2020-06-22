''' From a TMA design, extract image quality form an rms
field map.

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
import glob

if len(sys.argv) == 2:
    fname = sys.argv[1]
else:
    fnames = glob.glob('*.zmx')
    assert len(fnames) == 1
    fname = fnames[0]
    print('No filename provided, using %s' %fname)
fname = os.path.abspath(fname)

print('Sag for all mirrors.')

print("opening %s" %fname)

#parameters of the extraction

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
    testFile = fname
    TheSystem.LoadFile(testFile, False)
    TheLDE = TheSystem.LDE

    nsur = TheSystem.LDE.NumberOfSurfaces


    mirrors = []
    mirror_names = []
    for j in range(1, nsur):
        if TheLDE.GetSurfaceAt(j).Material == 'MIRROR':
            mirrors.append(j)
            mirror_names.append(TheLDE.GetSurfaceAt(j).Comment)

    zs = []
    xs = []
    ys = []

    for mirror_number in mirrors:
        analysis = TheSystem.Analyses.New_SurfaceSag()

        analysis.Terminate()
        analysis.WaitForCompletion()
        analysisSettings = analysis.GetSettings()

        SamplesFolder = TheApplication.SamplesDir
        cfgFile = SamplesFolder + "\\API\\Python\\sag.cfg"
        analysisSettings.SaveTo(cfgFile)

        analysisSettings.ModifySettings(cfgFile, 
                                        "SRS_SURF", "%i" %mirror_number)
        analysisSettings.LoadFrom(cfgFile)
    
        analysis.ApplyAndWaitForCompletion()
    
        res = analysis.GetResults()
        r = res.GetDataGrid(0)

        minx = r.MinX
        miny = r.MinY
        Nx = r.Nx
        Ny = r.Ny
    
        z = r.Values
        z = np.array(z)
        zs.append(z)

        x = np.array([r.X(j) for j in range(Nx)])
        y = np.array([r.Y(j) for j in range(Ny)])

        xs.append(x)
        ys.append(y)

        xx, yy = np.meshgrid(x,y)
        xx = xx.flatten()
        yy = yy.flatten()
        zz = z.flatten()
    


#    del zosapi
#    zosapi = None
