''' From TMA design, export rays from normalized sky coordinates to
focal plane coordinates.
This script will use field position 1 to get Hx, Hy.
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

delta_xy_deg = 0.5  # center field plus minus delta
N_points = 100

# list of pupil positions to sample
pxpys = [[0, 0], [0, 1], [0, -1], [1, 0], [-1, 0]]


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
        gencache.EnsureModule('{EA433010-2BAC-43C4-857C-7AEAC4A8CCE0}', 0, 1, 0)  # noqa
        gencache.EnsureModule('{F66684D7-AAFE-4A62-9156-FF7A7853F764}', 0, 1, 0)  # noqa
        # Note - the above can also be accomplished using 'makepy.py' in the
        # following directory:
        #      {PythonEnv}\Lib\site-packages\wind32com\client\
        # Also note that the generate wrappers do not get refreshed when the
        # COM library changes.
        # To refresh the wrappers, you can manually delete everything in the
        # cache directory:
        # #########{PythonEnv}\Lib\site-packages\win32com\gen_py\*.*
        self.TheConnection = EnsureDispatch("ZOSAPI.ZOSAPI_Connection")
        if self.TheConnection is None:
            raise PythonStandaloneApplication.ConnectionException("Unable to"
                               " intialize COM connection to ZOSAPI")  # noqa

        self.TheApplication = self.TheConnection.CreateNewApplication()
        if self.TheApplication is None:
            raise PythonStandaloneApplication.InitializationException("Unable"
                        " to acquire ZOSAPI application") # noqa

        if self.TheApplication.IsValidLicenseForAPI is False:
            raise PythonStandaloneApplication.LicenseException("License is not"
                    " valid for ZOSAPI use")  # noqa

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
                    "Unable to acquire Primary system")
        self.TheSystem.LoadFile(filepath, saveIfNeeded)

    def CloseFile(self, save):
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException(
                    "Unable to acquire Primary system")
        self.TheSystem.Close(save)

    def SamplesDir(self):
        if self.TheApplication is None:
            raise PythonStandaloneApplication.InitializationException(
                    "Unable to acquire ZOSAPI application")

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
    sampleDir = TheApplication.SamplesDir
    testFile = fname
    TheSystem.LoadFile(testFile, False)

    TheSystem.SystemData.Fields.Normalization = 0  # force radial normalization

    nsur = TheSystem.LDE.NumberOfSurfaces

    # explore surfaces and extract mirror names and surface numbers
    TheLDE = TheSystem.LDE
    MCE = TheSystem.MCE

    mirrors = []
    mirror_names = []
    for j in range(1, nsur):
        if TheLDE.GetSurfaceAt(j).Material == 'MIRROR':
            mirrors.append(j)
            mirror_names.append(TheLDE.GetSurfaceAt(j).Comment)
# Determine maximum field
    num_fields = TheSystem.SystemData.Fields.NumberOfFields
    nconf = MCE.NumberOfConfigurations
# store field labeled 1 to be center field
# Set up Batch Ray Trace

    TheSystem.SystemData.RayAiming.RayAiming = 2  # 2: real, 1: paraxial 0:off
    TheSystem.SystemData.Aperture.ApertureType = 3  # float by stop size
#    for conf in range(1, nconf + 1):    # see ZOSAPI.SystemData Namespace Ref
    for conf in range(1, 2):
        MCE.SetCurrentConfiguration(conf)  # changes configuration
        TheSystem.SystemData.Fields.SetVignetting()  # set vignetting
        print("Current configuration: %i" % MCE.CurrentConfiguration)
        raytrace = TheSystem.Tools.OpenBatchRayTrace()

        field1 = [TheSystem.SystemData.Fields.GetField(1).X,
                  TheSystem.SystemData.Fields.GetField(1).Y]

        max_field = 0.0
        for i in range(1, num_fields + 1):
            r_field = mt.sqrt(TheSystem.SystemData.Fields.GetField(i).Y**2 +
                              TheSystem.SystemData.Fields.GetField(i).X**2)
            if (r_field > max_field):
                max_field = r_field
    # center around first field
        center_field_x_deg = TheSystem.SystemData.Fields.GetField(1).X
        center_field_y_deg = TheSystem.SystemData.Fields.GetField(1).Y
        print('CenterField x: %1.3f, CenterField y: %1.3f' % (center_field_x_deg,  # noqa
                                                center_field_y_deg))  # noqa
        print('Max Field: %1.3f' % max_field)
        print("Nconf: %i" % nconf)
    # define field positions
    # assert delta_xy_deg < max_field # check that deltaxydeg is within maxfiel

        hx_min, hx_max = [(center_field_x_deg - delta_xy_deg)/max_field,
                          (center_field_x_deg + delta_xy_deg)/max_field]

        hy_min, hy_max = [(center_field_y_deg - delta_xy_deg)/max_field,
                          (center_field_y_deg + delta_xy_deg)/max_field]

        meshgrid = np.meshgrid(np.linspace(hx_min, hx_max, N_points),
                               np.linspace(hy_min, hy_max, N_points))

        hx_arr = meshgrid[0].flatten()
        hy_arr = meshgrid[1].flatten()

        # remove anything beyond hx,hy = 1
        sel = hx_arr**2 + hy_arr**2 < 1.0
        hx_arr = hx_arr[sel]
        hy_arr = hy_arr[sel]
        # end remove
        assert len(hx_arr) == len(hy_arr)
    # end define field positions
    #    max_rays = 30
        normUnPolData = raytrace.CreateNormUnpol(len(hx_arr) * len(pxpys),
                                                 constants.RaysType_Real, nsur)
    #    max_wave = TheSystem.SystemData.Wavelengths.NumberOfWavelengths
        # Initialize x/y image plane arrays
        x_ary = np.empty([len(pxpys)*len(hx_arr)])
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

        if TheSystem.SystemData.Fields.GetFieldType() == constants.FieldType_Angle: # noqa
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
                normUnPolData.AddRay(waveNumber, hx_arr[j], hy_arr[j], px, py, constants.OPDMode_None) # noqa
                ray_counter += 1

        print('running raytrace...')
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
                   'n': n}
        df = pd.DataFrame(package)
        fname_out = 'ray_db.hdf'
        df.to_hdf(fname_out, key='conf_%02i' % conf, complevel=9)
        baseTool.Close()

    system_variables = {'project_name': projectName,
                        'center_field_x': field1[0],
                        'center_field_y': field1[1],
                        'max_field': max_field}

    warnings.filterwarnings("ignore")
    df_variables = pd.Series(system_variables)
    df_variables.to_hdf(fname_out, key='system_variables')

    mirror_data = {'mirror_name': mirror_names,
                   'mirror_surface': mirrors}
    df_mirror_data = pd.DataFrame(mirror_data)
    df_mirror_data.to_hdf(fname_out, key='mirror_data')
    # This will clean up the connection to OpticStudio.
    # Note that it closes down the server instance of OpticStudio,
    # so you for maximum performance do not do
    # this until you need to.
#    del zosapi
#    zosapi = None
