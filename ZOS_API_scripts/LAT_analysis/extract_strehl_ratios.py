''' From a TMA design, extract image quality form an rms
field map.

'''

from win32com.client.gencache import EnsureDispatch
from win32com.client import CastTo, constants
from win32com.client import gencache
import os
import numpy as np
import sys
import pandas as pd
import glob

if len(sys.argv) == 2:
    fname = sys.argv[1]
else:
    fnames = glob.glob('*.zmx')
    assert len(fnames) == 1
    fname = fnames[0]
    print('No filename provided, using %s' % fname)
fname = os.path.abspath(fname)

print('Exporting Strehl ratios for field 1.\n\nRemember to check zmx file.')

print("opening %s" % fname)

# parameters of the extraction

sampling = 400  # number of samples to be extracted
field_semi_width = 7


# end parameters
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
        # To refresh the wrappers, you can manually delete everything in the
        # cache directory:
        # {PythonEnv}\Lib\site-packages\win32com\gen_py\*.*

        self.TheConnection = EnsureDispatch("ZOSAPI.ZOSAPI_Connection")
        if self.TheConnection is None:
            raise PythonStandaloneApplication.ConnectionException("Unable to intialize COM connection to ZOSAPI")  # noqa

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

    num_fields = TheSystem.SystemData.Fields.NumberOfFields
    max_field = 0.0
    for i in range(1, num_fields + 1):
        if (abs(TheSystem.SystemData.Fields.GetField(i).Y) > max_field):
            max_field = abs(TheSystem.SystemData.Fields.GetField(i).Y)
# ! [e22s03_py]

    if TheSystem.SystemData.Fields.GetFieldType() == constants.FieldType_Angle:
        field_type = 'Angle'
    elif TheSystem.SystemData.Fields.GetFieldType() == constants.FieldType_ObjectHeight:  # noqa
        field_type = 'Height'
    elif TheSystem.SystemData.Fields.GetFieldType() == constants.FieldType_ParaxialImageHeight:  # noqa
        field_type = 'Height'
    elif TheSystem.SystemData.Fields.GetFieldType() == constants.FieldType_RealImageHeight:  # noqa
        field_type = 'Height'

    analysis = TheSystem.Analyses.New_RMSFieldMap()
    analysis.Terminate()
    analysis.WaitForCompletion()
    analysisSettings = analysis.GetSettings()

    newSettings = analysis.GetSettings()
    rms_settings = CastTo(newSettings, "IAS_RMSFieldMap")
    rms_settings.Field.SetFieldNumber(1)
    rms_settings.Surface.SetSurfaceNumber(nsur)
    rms_settings.Wavelength.SetWavelengthNumber(1)
    rms_settings.UsePolarization = False
    rms_settings.RemoveVignettingFactors = False

    rms_settings.X_FieldSampling = sampling
    rms_settings.Y_FieldSampling = sampling

    rms_settings.X_FieldSize = field_semi_width
    rms_settings.Y_FieldSize = field_semi_width

    analysis.ApplyAndWaitForCompletion()

    res = analysis.GetResults()
    r = res.GetDataGrid(0)
    res = r.Values
    z = np.array(res)
    x = np.linspace(-field_semi_width, field_semi_width, sampling)
    y = np.linspace(-field_semi_width, field_semi_width, sampling)
    minx = r.MinX
    miny = r.MinY

    xx, yy = np.meshgrid(x, y)
    xx = xx.flatten()
    yy = yy.flatten()
    zz = z.flatten()

    toStore = {'xx_deg': xx, 'yy_deg': yy, 'z_strehl': zz}
    df = pd.DataFrame(toStore)
    fname_out = 'strehl_map.hdf'
    df.to_hdf(fname_out, key='df')
    print("File %s written" % fname_out)

    del zosapi
    zosapi = None
