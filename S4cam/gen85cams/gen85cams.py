import clr, os, winreg
from itertools import islice
from hexlattice import *
import time

t1 = time.time()

# This boilerplate requires the 'pythonnet' module.
# The following instructions are for installing the 'pythonnet' module via pip:
#    1. Ensure you are running Python 3.4, 3.5, 3.6, or 3.7. PythonNET does not work with Python 3.8 yet.
#    2. Install 'pythonnet' from pip via a command prompt (type 'cmd' from the start menu or press Windows + R and type 'cmd' then enter)
#
#        python -m pip install pythonnet

# determine the Zemax working directory
aKey = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER), r"Software\Zemax", 0, winreg.KEY_READ)
zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
NetHelper = os.path.join(os.sep, zemaxData[0], r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
winreg.CloseKey(aKey)

# add the NetHelper DLL for locating the OpticStudio install folder
clr.AddReference(NetHelper)
import ZOSAPI_NetHelper

pathToInstall = ''
# uncomment the following line to use a specific instance of the ZOS-API assemblies
#pathToInstall = r'C:\C:\Program Files\Zemax OpticStudio'

# connect to OpticStudio
success = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(pathToInstall);

zemaxDir = ''
if success:
    zemaxDir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory();
    print('Found OpticStudio at:   %s' + zemaxDir);
else:
    raise Exception('Cannot find OpticStudio')

# load the ZOS-API assemblies
clr.AddReference(os.path.join(os.sep, zemaxDir, r'ZOSAPI.dll'))
clr.AddReference(os.path.join(os.sep, zemaxDir, r'ZOSAPI_Interfaces.dll'))
import ZOSAPI

TheConnection = ZOSAPI.ZOSAPI_Connection()
if TheConnection is None:
    raise Exception("Unable to intialize NET connection to ZOSAPI")

TheApplication = TheConnection.ConnectAsExtension(0)
if TheApplication is None:
    raise Exception("Unable to acquire ZOSAPI application")

if TheApplication.IsValidLicenseForAPI == False:
    raise Exception("License is not valid for ZOSAPI use.  Make sure you have enabled 'Programming > Interactive Extension' from the OpticStudio GUI.")

TheSystem = TheApplication.PrimarySystem
if TheSystem is None:
    raise Exception("Unable to acquire Primary system")

def reshape(data, x, y, transpose = False):
    """Converts a System.Double[,] to a 2D list for plotting or post processing
    
    Parameters
    ----------
    data      : System.Double[,] data directly from ZOS-API 
    x         : x width of new 2D list [use var.GetLength(0) for dimension]
    y         : y width of new 2D list [use var.GetLength(1) for dimension]
    transpose : transposes data; needed for some multi-dimensional line series data
    
    Returns
    -------
    res       : 2D list; can be directly used with Matplotlib or converted to
                a numpy array using numpy.asarray(res)
    """
    if type(data) is not list:
        data = list(data)
    var_lst = [y] * x;
    it = iter(data)
    res = [list(islice(it, i)) for i in var_lst]
    if transpose:
        return self.transpose(res);
    return res
    
def transpose(data):
    """Transposes a 2D list (Python3.x or greater).  
    
    Useful for converting mutli-dimensional line series (i.e. FFT PSF)
    
    Parameters
    ----------
    data      : Python native list (if using System.Data[,] object reshape first)    
    
    Returns
    -------
    res       : transposed 2D list
    """
    if type(data) is not list:
        data = list(data)
    return list(map(list, zip(*data)))

print('Connected to OpticStudio')

# The connection should now be ready to use.  For example:
print('Serial #: ', TheApplication.SerialCode)

fname = r'C:\Users\pgall\Documents\wilson\code\zemax_tools\S4cam\gen85cams\ID12_onecam_togenerate85.zmx'
print("Opening file: %s" %fname)
TheSystem.LoadFile(fname, False)

TheMCE = TheSystem.MCE
assert TheMCE.NumberOfConfigurations == 1

#these specify where to put the cameras

row_cam_centerx = 10
row_cam_centery = 11

row_field_centerx = 2
row_field_centery = 3

scalex = -0.99/250 # approximate scale at focal plane
scaley = 0.99/250


df = gen85CamPosition(scale=219/np.sqrt(3)) # nrings = 1, -> center camera
cam_centerxs = df.x.values
cam_centerys = df.y.values

def make_rows_fixed(rows):
    ''' Gets a list of rows and makes the last configuration
    a fixed number in the configuration editor.
    '''
    for row in rows:
        op = TheMCE.GetOperandAt(row)
        config = TheMCE.NumberOfConfigurations
        cell = op.GetCellAt(config)
        cell.MakeSolveFixed() # make it fixed

def values_from_cam_centers(cam_centerx, cam_centery, scalex, scaley):
    values_to_set = [cam_centerx, cam_centery, 
                     scalex * cam_centerx, scaley * cam_centery]
    return values_to_set

def set_values(rows_to_set, values_to_set, TheMCE):
    for j, row in enumerate(rows_to_set):
        op = TheMCE.GetOperandAt(row)
        config = TheMCE.NumberOfConfigurations
        cell = op.GetCellAt(config)
        cell.DoubleValue = values_to_set[j]

#make rows fixed
rows_to_set = [row_cam_centerx, row_cam_centery,
                 row_field_centerx, row_field_centery]

for cam_centerx, cam_centery in zip(cam_centerxs, cam_centerys):
        #copy current configuration
    TheMCE.AddConfiguration(True)
    values = values_from_cam_centers(cam_centerx, cam_centery,
                                         scalex, scaley)
    make_rows_fixed(rows_to_set)
    set_values(rows_to_set, values, TheMCE)

TheMCE.DeleteConfiguration(1)
t2 = time.time()
print("Took: %1.2f s" %(t2-t1))
# Insert Code Here
