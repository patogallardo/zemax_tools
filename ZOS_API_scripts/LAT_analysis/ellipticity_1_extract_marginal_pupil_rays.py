''' From TMA design, export rays from pupil plane.

This script will use the fields in the field editor and extract
a circle in the pupil. Will save everything in a zdf file.
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

    TheSystem.SystemData.Fields.Normalization = 0  # force circular norm

    nsur = TheSystem.LDE.NumberOfSurfaces
    
    #explore surfaces and extract mirror names and surface numbers
    TheLDE = TheSystem.LDE
    
    mirrors = []
    mirror_names = []
    nPupil = None
    for j in range(1, nsur):
        if TheLDE.GetSurfaceAt(j).Material == 'MIRROR':
            mirrors.append(j)
            mirror_names.append(TheLDE.GetSurfaceAt(j).Comment)
        if 'Pupil' in TheLDE.GetSurfaceAt(j).Comment:
            nPupil = j
            print("Pupil in surface %i" % nPupil)
    assert nPupil is not None #check that we actually found the pupil
    
    #! [e22s01_py]
    # Set up Batch Ray Trace
    raytrace = TheSystem.Tools.OpenBatchRayTrace()

# Determine maximum field
    num_fields = TheSystem.SystemData.Fields.NumberOfFields
#store field labeled 1 to be center field    
    field1 = [TheSystem.SystemData.Fields.GetField(1).X,
              TheSystem.SystemData.Fields.GetField(1).Y]
    
    
    max_field = 0.0
    for i in range(1, num_fields + 1):
        r_field = mt.sqrt(TheSystem.SystemData.Fields.GetField(i).Y**2 + 
                          TheSystem.SystemData.Fields.GetField(i).X**2)
        if (r_field > max_field):
            max_field = r_field

    #now get the fields from the field editor
    Hx, Hy = np.empty(num_fields), np.empty(num_fields)
    for i in range(1, num_fields+1):
        Hx[i-1] = TheSystem.SystemData.Fields.GetField(i).X/max_field
        Hy[i-1] = TheSystem.SystemData.Fields.GetField(i).Y/max_field
    
#center around first field
    center_field_x_deg = TheSystem.SystemData.Fields.GetField(1).X
    center_field_y_deg = TheSystem.SystemData.Fields.GetField(1).Y

#define field positions
#    assert delta_xy_deg < max_field # check that deltaxydeg is within maxfield

    hx_arr = Hx
    hy_arr = Hy
    assert len(hx_arr) == len(hy_arr)
#end define field positions

    normUnPolData = raytrace.CreateNormUnpol(len(hx_arr) * len(pxpys), 
                                             constants.RaysType_Real, nPupil)
#    max_wave = TheSystem.SystemData.Wavelengths.NumberOfWavelengths

    # Initialize x/y image plane arrays
    x_ary = np.empty([len(pxpys)*len(hx_arr)])# center field +4 extreme fields
    y_ary = np.empty([len(pxpys)*len(hy_arr)])

    error_code = np.empty([len(pxpys)*len(hy_arr)], dtype=np.int32)
    vignette_code = np.empty([len(pxpys)*len(hy_arr)], dtype=np.int32)
    l = np.empty([len(pxpys)*len(hy_arr)], dtype=np.float32)
    m = np.empty([len(pxpys)*len(hy_arr)], dtype=np.float32)
    n = np.empty([len(pxpys)*len(hy_arr)], dtype=np.float32)

    px_output = np.empty([len(pxpys) * len(hx_arr)], dtype=np.float32)
    py_output = np.empty([len(pxpys) * len(hx_arr)], dtype=np.float32)
    hx_output = np.empty([len(pxpys) * len(hx_arr)], dtype=np.float32)
    hy_output = np.empty([len(pxpys) * len(hx_arr)], dtype=np.float32)

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

    ray_counter = 0
    for pxpy in pxpys:
        px, py = pxpy
        for j in range(len(hx_arr)):
            px_output[ray_counter], py_output[ray_counter] = px, py
            hx_output[ray_counter], hy_output[ray_counter] = hx_arr[j], hy_arr[j]
            normUnPolData.AddRay(waveNumber, hx_arr[j], hy_arr[j], px, py, constants.OPDMode_None)
            ray_counter += 1

    print('running raytrace...')
    baseTool = CastTo(raytrace, 'ISystemTool')
    baseTool.RunAndWaitForCompletion()

#! [e22s05_py]
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
    fname_out = 'ray_db_pupil.hdf'
    df.to_hdf(fname_out, key='df', complevel=9)

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
    # Note that it closes down the server instance of OpticStudio, so you for maximum performance do not do
    # this until you need to.

    #del zosapi
    #zosapi = None
