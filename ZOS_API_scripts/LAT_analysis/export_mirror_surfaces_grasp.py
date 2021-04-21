'''Export mirror mesh and rotational data.'''

import clr
import os
import winreg
import matplotlib.pyplot as plt  # noqa
import sys
import numpy as np
import glob
import zmx

configuration = 1

if len(sys.argv) == 2:  # optional support for specifying filename
    fname = sys.argv[1]
else:
    print('No file name provided, searching current directory')
    fnames = glob.glob('*.zmx')
    assert len(fnames) == 1
    fname = fnames[0]
projectName = fname
fname = os.path.abspath(fname)
print("opening: %s" % fname)


def get_rot_mat_origin(LDE, surface):
    globalMatrix = LDE.GetGlobalMatrix(surface,  # zeros seem pointless
                                       0, 0, 0, 0, 0, 0, 0, 0,
                                       0, 0, 0, 0)[1:]
    RotMat = np.reshape(globalMatrix[:9], [3, 3])
    origin = np.array(globalMatrix[9:])
    return RotMat, origin


def mk_rot_mat_file(RotMat, origin, name):
    lines = []
    lines.append(name)
    lines.append('mm')
    lines.append(", ".join(["%1.10e" % origin[j]
                            for j in range(len(origin))]))
    RotMat = RotMat.T
    for i in range(len(RotMat) - 1):
        lines.append(", ".join(["%.10e" % RotMat[i, j]
                                for j in range(len(origin))]))
    txt = "\n".join(lines)

    with open('./grasp_analysis/sfc/%s.cor' % name, 'w') as f:
        f.write(txt)


# check output dirs
dir_out = "grasp_analysis/sfc"
if not os.path.exists('grasp_analysis'):
    os.mkdir("grasp_analysis")
if not os.path.exists(dir_out):
    os.mkdir(dir_out)


class PythonStandaloneApplication(object):
    class LicenseException(Exception):
        pass

    class ConnectionException(Exception):
        pass

    class InitializationException(Exception):
        pass

    class SystemNotPresentException(Exception):
        pass

    def __init__(self, path=None):
        # determine location of ZOSAPI_NetHelper.dll & add as reference
        aKey = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER), r"Software\Zemax", 0, winreg.KEY_READ)  # noqa
        zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
        NetHelper = os.path.join(os.sep, zemaxData[0],
                                 r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
        winreg.CloseKey(aKey)
        clr.AddReference(NetHelper)
        import ZOSAPI_NetHelper

        # Find the installed version of OpticStudio
        if path is None:
            isInitialized = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize()
        else:
            # Note -- uncomment the following line to use a custom initialization path  # noqa
            isInitialized = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(path)  # noqa

        # determine the ZOS root directory
        if isInitialized:
            dir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory()
        else:
            raise PythonStandaloneApplication.InitializationException("Unable to locate Zemax OpticStudio.  Try using a hard-coded path.")  # noqa

        # add ZOS-API referencecs
        clr.AddReference(os.path.join(os.sep, dir, "ZOSAPI.dll"))
        clr.AddReference(os.path.join(os.sep, dir, "ZOSAPI_Interfaces.dll"))
        import ZOSAPI

        # create a reference to the API namespace
        self.ZOSAPI = ZOSAPI

        # create a reference to the API namespace
        self.ZOSAPI = ZOSAPI

        # Create the initial connection class
        self.TheConnection = ZOSAPI.ZOSAPI_Connection()

        if self.TheConnection is None:
            raise PythonStandaloneApplication.ConnectionException("Unable to initialize .NET connection to ZOSAPI")  # noqa

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
        if self.TheApplication.LicenseStatus == self.ZOSAPI.LicenseStatusType.PremiumEdition:  # noqa
            return "Premium"
        elif self.TheApplication.LicenseStatus == self.ZOSAPI.LicenseStatusTypeProfessionalEdition:  # noqa
            return "Professional"
        elif self.TheApplication.LicenseStatus == self.ZOSAPI.LicenseStatusTypeStandardEdition:   # noqa
            return "Standard"
        else:
            return "Invalid"


def save_srf_file(x, y, zs, name):
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    Nx, Ny = len(x), len(y)
    name = name.replace(' ', "_")

    lines = []
    lines.append("%s" % name)
    lines.append("%1.10e, %1.10e, %1.10e, %1.10e" % (x_min, y_min,
                                                     x_max, y_max))
    lines.append("%i, %i" % (Nx, Ny))

    for i in range(Nx):
        sl = zs[i, :]
        line = ", ".join("%1.10e" % number for number in sl)
        lines.append(line)

    txt = "\n".join(lines)
    with open('./grasp_analysis/sfc/' + name + '.sfc', 'w') as f:
        f.write(txt)


r_mirror = 3000
Nsamp = 100
if __name__ == '__main__':
    zos = PythonStandaloneApplication()
    # use http://matplotlib.org/ to plot 2D graph
    # need to install this package before running this code

    # load local variables
    zosapi = zos.ZOSAPI
    TheApplication = zos.TheApplication
    TheSystem = zos.TheSystem

    # Set up primary optical system
    testFile = fname
    TheSystem.LoadFile(testFile, False)

    TheSystem.MCE.SetCurrentConfiguration(configuration)

    nsur = TheSystem.LDE.NumberOfSurfaces

    # explore surfaces and extract mirror names and surface numbers
    LDE = TheSystem.LDE

#   identify mirror names and surface numbers
    m_names, m_surfs = zmx.get_mirror_surfaces(TheSystem)

    for mirror_number in range(len(m_surfs)):
        surface = m_surfs[mirror_number]
        name = m_names[mirror_number]

        s = LDE.GetSurfaceAt(surface)
        x = np.linspace(-r_mirror, r_mirror, Nsamp)
        y = np.linspace(-r_mirror, r_mirror, Nsamp)

        zs = np.empty([Nsamp, Nsamp])

        for i in range(Nsamp):
            for j in range(Nsamp):
                zs[i, j] = LDE.GetSag(surface,
                                      x[i],
                                      y[j],
                                      0, 0)[1]
        save_srf_file(x, y, zs, name)
        # Make plots
        plt.pcolor(x, y, zs)
        plt.colorbar(label='sag [mm]')
        plt.savefig('grasp_analysis/sfc/%s.png' % m_names[mirror_number],
                    dpi=150)
        plt.close()
        # end plots

        # Export coordinate frames
        RotMat, origin = get_rot_mat_origin(LDE, surface)
        mk_rot_mat_file(RotMat, origin, name.replace(' ', '_'))
