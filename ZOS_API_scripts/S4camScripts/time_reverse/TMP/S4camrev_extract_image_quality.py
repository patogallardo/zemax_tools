import clr
import os
import winreg
from itertools import islice
import sys
import glob
import numpy as np
import matplotlib.pyplot as plt  # noqa
from progressbar import progressbar

sampling = 50
field_size = 65.0


def f(h):
    r = abs(MFE.GetOperandValue(REAX, img_sur, 1, h, 0, 0, 0, 0, 0)) - 65
    return r


def check_args(argv):
    if len(argv) == 2:
        fname = argv[1]
    else:
        print("no fname given, searching this directory")
        fnames = glob.glob('*.zos')
        if len(fnames) == 0:
            fnames = glob.glob("*.zmx")  # legacy mode
        assert len(fnames) == 1
        fname = fnames[0]
    return fname


def get_norm_angle(Fields):
    nfields = Fields.NumberOfFields
    r_max = 0
    for nfield in range(1, nfields + 1):
        field = Fields.GetField(nfield)
        r = np.sqrt(field.X**2 + field.Y**2)
        if r > r_max:
            r_max = r
    return r_max


def getStrehls(TheSystem, wavelengthNumber):
    analysis = TheSystem.Analyses.New_Analysis(RMSFieldMap)
    settings = analysis.GetSettings()
    settings.Field.SetFieldNumber(1)
    settings.Surface.SetSurfaceNumber(img_sur)
    settings.Wavelength.SetWavelengthNumber(wavelengthNumber)
    settings.UsePolarization = False
    settings.RemoveVignettingFactors = False

    settings.X_FieldSampling = sampling
    settings.Y_FieldSampling = sampling

    settings.X_FieldSize = field_size
    settings.Y_FieldSize = field_size

    analysis.ApplyAndWaitForCompletion()

    g = analysis.GetResults().GetDataGrid(0)
    assert g.Nx == g.Ny == sampling
    z = np.zeros([sampling, sampling])

    for i in range(sampling):
        for j in range(sampling):
            z[i, j] = g.Z(i, j)

    x, y = np.zeros(sampling), np.zeros(sampling)
    for i in range(sampling):
        x[i] = g.X(i)
        y[i] = g.Y(i)
    analysis.Close()

    return x, y, z


fname = check_args(sys.argv)
print("Using fname: %s" % fname)
fname = os.path.abspath(fname)


class PythonStandaloneApplication2(object):
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
        aKey = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),  # noqa
                              r"Software\Zemax", 0, winreg.KEY_READ)
        zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
        NetHelper = os.path.join(os.sep, zemaxData[0],
                                 r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
        winreg.CloseKey(aKey)
        clr.AddReference(NetHelper)
        import ZOSAPI_NetHelper  # noqa
        # Find the installed version of OpticStudio
        if path is None:
            isInitialized = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize()
        else:
            # Note -- uncomment the following line to use a custom init
            isInitialized = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(path)  # noqa
        # determine the ZOS root directory
        if isInitialized:
            dir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory()
        else:
            raise PythonStandaloneApplication2.InitializationException(
                    "Unable to locate Zemax OpticStudio. Try a hard-coded path.")  # noqa

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
            raise PythonStandaloneApplication2.ConnectionException(
                    "Unable to initialize .NET connection to ZOSAPI")  # noqa

        self.TheApplication = self.TheConnection.CreateNewApplication()
        if self.TheApplication is None:
            raise PythonStandaloneApplication2.InitializationException(
                    "Unable to acquire ZOSAPI application")  # noqa

        if self.TheApplication.IsValidLicenseForAPI is False:
            raise PythonStandaloneApplication2.LicenseException(
                    "License is not valid for ZOSAPI use")  # noqa

        self.TheSystem = self.TheApplication.PrimarySystem
        if self.TheSystem is None:
            raise PythonStandaloneApplication2.SystemNotPresentException(
                    "Unable to acquire Primary system")  # noqa

    def __del__(self):
        if self.TheApplication is not None:
            self.TheApplication.CloseApplication()
            self.TheApplication = None

        self.TheConnection = None

    def OpenFile(self, filepath, saveIfNeeded):
        if self.TheSystem is None:
            raise PythonStandaloneApplication2.SystemNotPresentException(
                    "Unable to acquire Primary system")  # noqa
        self.TheSystem.LoadFile(filepath, saveIfNeeded)

    def CloseFile(self, save):
        if self.TheSystem is None:
            raise PythonStandaloneApplication2.SystemNotPresentException(
                    "Unable to acquire Primary system")  # noqa
        self.TheSystem.Close(save)

    def SamplesDir(self):
        if self.TheApplication is None:
            raise PythonStandaloneApplication2.InitializationException(
                    "Unable to acquire ZOSAPI application")  # noqa

        return self.TheApplication.SamplesDir

    def ExampleConstants(self):
        if self.TheApplication.LicenseStatus == self.ZOSAPI.LicenseStatusType.PremiumEdition:  # noqa
            return "Premium"
        elif self.TheApplication.LicenseStatus == self.ZOSAPI.LicenseStatusTypeProfessionalEdition:  # noqa
            return "Professional"
        elif self.TheApplication.LicenseStatus == self.ZOSAPI.LicenseStatusTypeStandardEdition:  # noqa
            return "Standard"
        else:
            return "Invalid"

    def reshape(self, data, x, y, transpose=False):
        """Converts a System.Double[,] to a 2D list for plotting or post processing

        Parameters
        ----------
        data      : System.Double[,] data directly from ZOS-API
        x         : x width of new 2D list [use var.GetLength(0) for dimension]
        y         : y width of new 2D list [use var.GetLength(1) for dimension]
        transpose : transposes data; needed for some multi-dimensional line
                    series data

        Returns
        -------
        res       : 2D list; can be directly used with Matplotlib or converted
                    to
                    a numpy array using numpy.asarray(res)
        """
        if type(data) is not list:
            data = list(data)
        var_lst = [y] * x
        it = iter(data)
        res = [list(islice(it, i)) for i in var_lst]
        if transpose:
            return self.transpose(res)
        return res

    def transpose(self, data):
        """Transposes a 2D list (Python3.x or greater).

        Useful for converting mutli-dimensional line series (i.e. FFT PSF)

        Parameters
        ----------
        data      : Python native list (if using System.Data[,] object reshape first)   # noqa

        Returns
        -------
        res       : transposed 2D list
        """
        if type(data) is not list:
            data = list(data)
        return list(map(list, zip(*data)))


if __name__ == '__main__':
    zos = PythonStandaloneApplication2()

    # load local variables
    ZOSAPI = zos.ZOSAPI
    TheApplication = zos.TheApplication
    TheSystem = zos.TheSystem
    MCE = TheSystem.MCE
    LDE = TheSystem.LDE
    MFE = TheSystem.MFE
    Fields = TheSystem.SystemData.Fields
    RMSFieldMap = ZOSAPI.Analysis.AnalysisIDM.RMSFieldMap
    REAX = ZOSAPI.Editors.MFE.MeritOperandType.REAX

    TheSystem.LoadFile(fname, False)
    nsur = TheSystem.LDE.NumberOfSurfaces
    img_sur = nsur - 1
    nfields = Fields.NumberOfFields
    nconf = TheSystem.MCE.NumberOfConfigurations
    Wavelengths = TheSystem.SystemData.Wavelengths
    nwavelengths = Wavelengths.NumberOfWavelengths
    assert nwavelengths == 3  # check zmx file to contain 3 wavelenghts

    # cycle through configurations and save strehls

    for wavelengthNumber in range(1, 3+1):
        zs = np.zeros([nconf, sampling, sampling])
        for current_conf in progressbar(range(1, nconf+1)):
            MCE.SetCurrentConfiguration(current_conf)
            Fields.ClearVignetting()
            Fields.SetVignetting()
            x, y, z = getStrehls(TheSystem, wavelengthNumber)
            zs[current_conf-1, :, :] = z

        normalization_fp = get_norm_angle(Fields)

        # save everything
        w = Wavelengths.GetWavelength(wavelengthNumber)
        folderOut = 'strehls_%1.0fmm' % (w.Wavelength/1000.)
        if not os.path.exists(folderOut):
            os.mkdir(folderOut)
        np.savez_compressed('%s/strehls.npz' % folderOut, x=x, y=y, zs=zs,
                            wavelength=w.Wavelength/1000.)
# Note that it closes down the server instance of OpticStudio,
# so you for maximum performance do not do
# this until you need to.
#    del zos
#    zos = None
