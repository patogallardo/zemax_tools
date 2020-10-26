import clr, os, winreg
from itertools import islice
import shutil
import pandas as pd

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

#some handy functions
def makeVariableOrFixed(TheSystem, conf, operand, 
                        variable=True):
    '''Receives TheMCE, configuration and operand
    and makes them variable'''
    TheMCE = TheSystem.MCE
    op = TheMCE.GetOperandAt(operand)
    cell = op.GetOperandCell(conf)
    if variable:
        cell.MakeSolveVariable()
    else:
        cell.MakeSolveFixed()

def setVariable(TheSystem, conf, operands):
    '''Gets a list of configurations and operands and makes them
    variable
    '''
    tools = TheSystem.Tools
    tools.RemoveAllVariables()

    for operand in operands:
        makeVariableOrFixed(TheSystem, conf, operand,
                            variable=True)
    
def setFixed(TheSystem, confs, operands):
    '''Sets to fixed configurations in conf for the operands in operands
    '''
    tools = TheSystem.Tools
    tools.RemoveAllVariables()

    for conf in confs:
        for operand in operands:
            makeVariableOrFixed(TheSystem, conf, operand, 
                                variable=False)

# Insert Code Here
CAMPOS_FNAME = './85cam_groups.csv'
shutil.copyfile('../groupCameras/85cam_groups.csv', CAMPOS_FNAME)
df = pd.read_csv(CAMPOS_FNAME)

TheMCE = TheSystem.MCE
NCONF = TheMCE.NumberOfConfigurations
NOPERANDS = TheMCE.NumberOfOperands

groupsOfCams = df.group.unique()
g = df.groupby('group')

vars_tooptimize = pd.read_excel('./listofvariables.xlsx').iloc[0].values

group = 0 # vary this to change groups

confs = g.groups[group].values[1:] + 1
setFixed(TheSystem, confs, operands=vars_tooptimize)

setVariable(TheSystem, 
            conf=g.groups[group].values[0] + 1, 
            operands=vars_tooptimize)
