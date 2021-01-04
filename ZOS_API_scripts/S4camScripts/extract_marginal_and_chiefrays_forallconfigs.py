''' From TMA design, export rays from normalized sky coordinates to focal plane coordinates.

This script will use field position 1 to get Hx, Hy.
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
from progressbar import progressbar as pb

if os.path.exists('./ray_db.hdf'):
    os.remove('./ray_db.hdf')
if len(sys.argv) == 2: # optional support for specifying filename 
    fname = sys.argv[1]
else:
    print('No file name provided, searching current directory')
    fnames = glob.glob('*.zmx')
    assert len(fnames) == 1
    fname = fnames[0]
projectName = fname
fname = os.path.abspath(fname)

print("opening %s" %fname)

delta_xy_deg = 0.39 # center field plus minus delta
N_points = 40

# list of pupil positions to sample
pxpys = [[0, 0],[0,1],[0,-1],[1,0],[-1,0]] # 1% smaller to avoid vignetting at the stop


def run_raytrace(TheSystem, hx_arr, hy_arr, nsur, 
                 configurationRange):
    dfs = []
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

    # Adding Rays to Batch, varying normalised object height hy

    assert len(configurationRange) == 2
    for configurationNumber in pb(range(configurationRange[0], configurationRange[1]+1)):
        TheSystem.MCE.SetCurrentConfiguration(configurationNumber)

        TheSystem.SystemData.Fields.SetVignetting()

        raytrace = TheSystem.Tools.OpenBatchRayTrace()
        normUnPolData = raytrace.CreateNormUnpol(len(hx_arr) * len(pxpys), 
                                             constants.RaysType_Real, nsur)
     
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
                #! [e22s04_py]
        
        print('running raytrace...')
        baseTool = CastTo(raytrace, 'ISystemTool')
        baseTool.RunAndWaitForCompletion()
    
        normUnPolData.StartReadingResults()
        output = normUnPolData.ReadNextResult()
    
        j=0
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
                   'n':n}
        df = pd.DataFrame(package) # end extracting rays
        r = np.sqrt(df['x_pos'].values**2+df['y_pos'].values**2)
        sel = r < 85

        dfs.append(df.iloc[sel])
        baseTool.Close()
    return dfs


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

    TheSystem.SystemData.Fields.Normalization = 0 # force radial normalization
#    TheSystem.SystemData.RayAiming.RayAiming = 2 # enable ray aiming
#    TheSystem.SystemData.Aperture.ApertureType = 3 # float by stop
#    surface = TheSystem.LDE.GetSurfaceAt(56) #stop at surface 56
#    surface.IsStop = True

    nsur = TheSystem.LDE.NumberOfSurfaces
    nconf = TheSystem.MCE.NumberOfConfigurations
    print("Number of confs: %i" %nconf)
    
    #explore surfaces and extract mirror names and surface numbers
    TheLDE = TheSystem.LDE
    
    mirrors = []
    mirror_names = []
    for j in range(1, nsur):
        if TheLDE.GetSurfaceAt(j).Material == 'MIRROR':
            mirrors.append(j)
            mirror_names.append(TheLDE.GetSurfaceAt(j).Comment)
        
    
    #! [e22s01_py]
    # Set up Batch Ray Trace
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
#center around first field
    center_field_x_deg = TheSystem.SystemData.Fields.GetField(1).X
    center_field_y_deg = TheSystem.SystemData.Fields.GetField(1).Y
    print('CenterField x: %1.3f, CenterField y: %1.3f' % (center_field_x_deg, center_field_y_deg) )
    print('Max Field: %1.3f' %max_field)

    
#define field positions
#    assert delta_xy_deg < max_field # check that deltaxydeg is within maxfield

    hx_min, hx_max = [(center_field_x_deg - delta_xy_deg)/max_field,
                      (center_field_x_deg + delta_xy_deg)/max_field]

    hy_min, hy_max = [(center_field_y_deg - delta_xy_deg)/max_field,
                      (center_field_y_deg + delta_xy_deg)/max_field]

    meshgrid = np.meshgrid(np.linspace(hx_min, hx_max, N_points), 
                           np.linspace(hy_min, hy_max, N_points))

    hx_arr = meshgrid[0].flatten()
    hy_arr = meshgrid[1].flatten()
    assert len(hx_arr) == len(hy_arr)

    
    dfs = []
    dfs = run_raytrace(TheSystem, hx_arr, hy_arr, nsur,
                      configurationRange=[1, 19])


    fname_out = 'ray_db.hdf'
    for j, df in enumerate(dfs):
        df.to_hdf(fname_out, key='df_%02i'%j, complevel=9)
    
    system_variables={'project_name': projectName,
                      'center_field_x': field1[0],
                      'center_field_y': field1[1],
                      'max_field': max_field}   

    warnings.filterwarnings("ignore")
    df_variables = pd.Series(system_variables)
    df_variables.to_hdf(fname_out, key='system_variables')

    mirror_data = {'mirror_name': mirror_names,
                   'mirror_surface': mirrors }
    df_mirror_data = pd.DataFrame(mirror_data)
    df_mirror_data.to_hdf(fname_out, key='mirror_data')

# debug plot
    dfq = dfs[0].query('px==0 and py==0')
    plt.hexbin(dfq.x_pos, dfq.y_pos, 
               dfq.vignette_code, gridsize=30); 
    plt.colorbar();
    plt.show()

    del zosapi
    zosapi = None
