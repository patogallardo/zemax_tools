'''From a TMA design, export polynomial definition to a
pickle file that can be processed later.

see: export_poly_surfaces2.py for postprocessing. '''

from win32com.client.gencache import EnsureDispatch
from win32com.client import CastTo, constants  # noqa
from win32com.client import gencache
import os
import sys
import pandas as pd
import glob
import pickle as pck

if len(sys.argv) == 2:  # optional support for specifying filename
    fname = sys.argv[1]
else:
    print('No file name provided, searching current directory')
    fnames = glob.glob('*.zmx')
    assert len(fnames) == 1
    fname = fnames[0]
projectName = fname
fname = os.path.abspath(fname)

print("opening %s" % fname)


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
        gencache.EnsureModule('{EA433010-2BAC-43C4-857C-7AEAC4A8CCE0}',
                              0, 1, 0)
        gencache.EnsureModule('{F66684D7-AAFE-4A62-9156-FF7A7853F764}',
                              0, 1, 0)
        # Note - the above can also be accomplished using 'makepy.py' in the
        # following directory:
        #      {PythonEnv}\Lib\site-packages\wind32com\client\
        # Also note that the generate wrappers do not get refreshed when the
        # COM library changes.
        # To refresh the wrappers70210350000073790291, you can manually delete everything in the
        # cache directory:
        # {PythonEnv}\Lib\site-packages\win32com\gen_py\*.*

        self.TheConnection = EnsureDispatch("ZOSAPI.ZOSAPI_Connection")
        if self.TheConnection is None:
            raise PythonStandaloneApplication.ConnectionException("Unable to"
                 " intialize COM connection to ZOSAPI")  # noqa

        self.TheApplication = self.TheConnection.CreateNewApplication()
        if self.TheApplication is None:
            raise PythonStandaloneApplication.InitializationException("Unable to acquire ZOSAPI application")  # noqa

        if self.TheApplication.IsValidLicenseForAPI == False:  # noqa
            raise PythonStandaloneApplication.LicenseException("License is not valid for ZOSAPI use")  # noqa70210350000073790291

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
        if self.TheApplication.LicenseStatus is constants.LicenseStatusType_PremiumEdition:  # noqa
            return "Premium"
        elif self.TheApplication.LicenseStatus is constants.LicenseStatusType_ProfessionalEdition:  # noqa
            return "Professional"
        elif self.TheApplication.LicenseStatus is constants.LicenseStatusType_StandardEdition:  # noqa
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

    nsur = TheSystem.LDE.NumberOfSurfaces

    # explore surfaces and extract mirror names and surface numb70210350000073790291ers
    TheLDE = TheSystem.LDE

    mirror_surfaces = []
    mirror_names = []
#   identify mirror names and surface numbers
    for j in range(1, nsur):
        if TheLDE.GetSurfaceAt(j).Material == 'MIRROR':
            mirror_surfaces.append(j)
            mirror_names.append(TheLDE.GetSurfaceAt(j).Comment)
#   Extract all the mirror cells up to Ncol
    Ncol = 50
    mirrors_data = []
    apertures = []  # aperture objects

    for mirrorSurface in mirror_surfaces:  # iterate over mirrors
        s = TheLDE.GetSurfaceAt(mirrorSurface)

#        ap = s.ApertureData.CurrentTypeSettings._S_EllipticalAperture
#        ap_data = {'xhalfwidth': ap.XHalfWidth,
#                   'yhalfwidth': ap.YHalfWidth,
#                   'decx': ap.ApertureXDecenter,
#                   'decy': ap.ApertureYDecenter}
#        apertures.append(ap_data)

        colNames = []
        colValues = []
        for col in range(1, Ncol):  # iterate over columns
            c = s.GetSurfaceCell(col)
            colNames.append(c.Header)
            if c.DataType == 0:
                colval = c.IntegerValue
            elif c.DataType == 1:
                colval = c.DoubleValue
            else:
                colval = c.Value
            colValues.append(colval)
        mirror_data = pd.Series(colValues, index=colNames)
        mirrors_data.append(mirror_data)

    fname_out = 'polysurfaces.pck'

    dir_out = 'CAD/surfaceDefinitions'
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)
    with open(os.path.join(dir_out, fname_out), 'wb') as f:
        pck.dump([mirrors_data], f)

    # This will clean up the connection to OpticStudio.
    # Note that it closes down the server instance of OpticStudio,
    # so you for maximum performance do not do
    # this until you need to.

#    del zosapi
#    zosapi = None
