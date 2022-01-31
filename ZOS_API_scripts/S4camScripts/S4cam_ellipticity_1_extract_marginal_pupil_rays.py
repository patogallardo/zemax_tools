''' From TMA design, export rays from pupil plane.

This script will use the fields in the field editor and extract
a circle in the pupil. Will save everything in a zdf file.
'''

from win32com.client.gencache import EnsureDispatch
from win32com.client import CastTo, constants
from win32com.client import gencache
import os
import numpy as np
import sys
import pandas as pd
import math as mt
import glob
import warnings
import progressbar

if len(sys.argv) == 2:  # optional support for specifying filename
    fname = sys.argv[1]
else:
    print('No file name provided, searching current directory')
    fnames = glob.glob('*.zos')
    assert len(fnames) == 1
    fname = fnames[0]
projectName = fname
fname = os.path.abspath(fname)

print("opening %s" % fname)

# list of pupil positions to sample
Nsamples = 20  # use Nsamples for the ring and one for the chief ray
theta = np.linspace(0, 2*np.pi, Nsamples)
pxpys = list(zip(np.cos(theta), np.sin(theta)))


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
            raise PythonStandaloneApplication.ConnectionException("Unable"
            "to intialize COM connection to ZOSAPI")  # noqa

        self.TheApplication = self.TheConnection.CreateNewApplication()
        if self.TheApplication is None:
            raise PythonStandaloneApplication.InitializationException("Unable"
            " to acquire ZOSAPI application")  # noqa

        if self.TheApplication.IsValidLicenseForAPI is False:
            raise PythonStandaloneApplication.LicenseException("License"
            " is not valid for ZOSAPI use")  # noqa

        self.TheSystem = self.TheApplication.PrimarySystem
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException(
                    "Unable to acquire Primary system")  # noqa

    def __del__(self):
        if self.TheApplication is not None:
            self.TheApplication.CloseApplication()
            self.TheApplication = None

        self.TheConnection = None

    def OpenFile(self, filepath, saveIfNeeded):
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException(
                    "Unable to acquire Primary system")  # noqa
        self.TheSystem.LoadFile(filepath, saveIfNeeded)

    def CloseFile(self, save):
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException(
                    "Unable to acquire Primary system")  # noqa
        self.TheSystem.Close(save)

    def SamplesDir(self):
        if self.TheApplication is None:
            raise PythonStandaloneApplication.InitializationException(
                    "Unable to acquire ZOSAPI application")  # noqa

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
    Fields = TheSystem.SystemData.Fields
    TheApplication = zosapi.TheApplication

    # Set up primary optical system
    testFile = fname
    TheSystem.LoadFile(testFile, False)

    TheSystem.SystemData.Fields.Normalization = 0  # force circular norm
    nsur = TheSystem.LDE.NumberOfSurfaces
    nconf = TheSystem.MCE.NumberOfConfigurations

#  explore surfaces and extract mirror names and surface numbers
    TheLDE = TheSystem.LDE
    MCE = TheSystem.MCE

    mirrors = []
    mirror_names = []
    nPupil = None
    for j in range(1, nsur):
        if TheLDE.GetSurfaceAt(j).Material == 'MIRROR':
            mirrors.append(j)
            mirror_names.append(TheLDE.GetSurfaceAt(j).Comment)
        if 'test_f_ellipticity' in TheLDE.GetSurfaceAt(j).Comment:
            nPupil = j
            print("Pupil in surface %i" % nPupil)
    assert nPupil is not None  # check that we actually found the pupil

    # Set up Batch Ray Trace

    for configuration in progressbar.progressbar(range(1, nconf+1, 1)):
        MCE.SetCurrentConfiguration(configuration)
        Fields.ClearVignetting()
        Fields.SetVignetting()
        raytrace = TheSystem.Tools.OpenBatchRayTrace()
# Determine maximum field
        num_fields = TheSystem.SystemData.Fields.NumberOfFields
    # store field labeled 1 to be center field
        field1 = [TheSystem.SystemData.Fields.GetField(1).X,
                  TheSystem.SystemData.Fields.GetField(1).Y]

        max_field = 0.0
        for i in range(1, num_fields + 1):
            r_field = mt.sqrt(TheSystem.SystemData.Fields.GetField(i).Y**2 +
                              TheSystem.SystemData.Fields.GetField(i).X**2)
            if (r_field > max_field):
                max_field = r_field

    # now get the fields from the field editor
        Hx, Hy = np.empty(num_fields), np.empty(num_fields)
        for i in range(1, num_fields+1):
            Hx[i-1] = TheSystem.SystemData.Fields.GetField(i).X/max_field
            Hy[i-1] = TheSystem.SystemData.Fields.GetField(i).Y/max_field
    # center around first field
        center_field_x_deg = TheSystem.SystemData.Fields.GetField(1).X
        center_field_y_deg = TheSystem.SystemData.Fields.GetField(1).Y
    # define field positions
    # assert delta_xy_deg < max_field # check that deltaxydeg is within maxfield  # noqa

        hx_arr = Hx
        hy_arr = Hy
        assert len(hx_arr) == len(hy_arr)
    # end define field positions

        normUnPolData = raytrace.CreateNormUnpol(len(hx_arr) * len(pxpys),
                                                 constants.RaysType_Real, nPupil)  # noqa
    #    max_wave = TheSystem.SystemData.Wavelengths.NumberOfWavelengths

        # Initialize x/y image plane arrays
        x_ary = np.empty([len(pxpys)*len(hx_arr)])  # center field +4 extreme flds  # noqa
        y_ary = np.empty([len(pxpys)*len(hy_arr)])

        error_code = np.empty([len(pxpys)*len(hy_arr)], dtype=np.int32)
        vignette_code = np.empty([len(pxpys)*len(hy_arr)], dtype=np.int32)

        l = np.empty([len(pxpys)*len(hy_arr)], dtype=np.float32)  # noqa
        m = np.empty([len(pxpys)*len(hy_arr)], dtype=np.float32)
        n = np.empty([len(pxpys)*len(hy_arr)], dtype=np.float32)

        px_output = np.empty([len(pxpys) * len(hx_arr)], dtype=np.float32)
        py_output = np.empty([len(pxpys) * len(hx_arr)], dtype=np.float32)
        hx_output = np.empty([len(pxpys) * len(hx_arr)], dtype=np.float32)
        hy_output = np.empty([len(pxpys) * len(hx_arr)], dtype=np.float32)
        field_number = np.empty([len(pxpys) * len(hx_arr)], dtype=np.int32)

        if TheSystem.SystemData.Fields.GetFieldType() == constants.FieldType_Angle:  # noqa
            field_type = 'Angle'
        elif TheSystem.SystemData.Fields.GetFieldType() == constants.FieldType_ObjectHeight:  # noqa
            field_type = 'Height'
        elif TheSystem.SystemData.Fields.GetFieldType() == constants.FieldType_ParaxialImageHeight:  # noqa
            field_type = 'Height'
        elif TheSystem.SystemData.Fields.GetFieldType() == constants.FieldType_RealImageHeight:  # noqa
            field_type = 'Height'
    # Adding Rays to Batch, varying normalised object height hy
        normUnPolData.ClearData()
        waveNumber = 1

        ray_counter = 0
        for pxpy in pxpys:
            px, py = pxpy
            for j in range(len(hx_arr)):
                px_output[ray_counter], py_output[ray_counter] = px, py
                hx_output[ray_counter], hy_output[ray_counter] = hx_arr[j], hy_arr[j]  # noqa
                field_number[ray_counter] = j + 1
                normUnPolData.AddRay(waveNumber, hx_arr[j], hy_arr[j], px, py, constants.OPDMode_None)  # noqa
                ray_counter += 1

        baseTool = CastTo(raytrace, 'ISystemTool')
        baseTool.RunAndWaitForCompletion()

    # Read batch raytrace and display results
        normUnPolData.StartReadingResults()
        output = normUnPolData.ReadNextResult()

        j = 0
        while output[0]:                                # success
            error_code[j] = output[2]
            vignette_code[j] = output[3]
            x_ary[j] = output[4]   # X
            y_ary[j] = output[5]   # Y
            l[j] = output[7]
            m[j] = output[8]
            n[j] = output[9]
            output = normUnPolData.ReadNextResult()
            j += 1
        baseTool.Close()  # this is important for MC

        hx_deg = max_field * hx_output
        hy_deg = max_field * hy_output

        package = {'hx_deg': hx_deg,
                   'hy_deg': hy_deg,
                   'x_pos': x_ary,
                   'y_pos': y_ary,
                   'px': px_output,
                   'py': py_output,
                   'error_code': error_code,
                   'vignette_code': vignette_code,
                   'l': l,
                   'm': m,
                   'n': n,
                   'field_number': field_number}
        df = pd.DataFrame(package)
        if not os.path.exists('f_numbers'):
            os.mkdir("f_numbers")
        fname_out = 'f_numbers/ray_db_pupil.hdf'
        df.to_hdf(fname_out, key='df%02i' % (configuration),
                  complevel=9)

        system_variables = {'project_name': projectName,
                            'center_field_x': field1[0],
                            'center_field_y': field1[1],
                            'max_field': max_field}

        warnings.filterwarnings("ignore")
    df_variables = pd.Series(system_variables)
    df_variables.to_hdf(fname_out, key='system_variables')

#    df_mirror_data = pd.DataFrame(mirror_data)
#    df_mirror_data.to_hdf(fname_out, key='mirror_data')
    # This will clean up the connection to OpticStudio.
    # del zosapi
    # zosapi = None
