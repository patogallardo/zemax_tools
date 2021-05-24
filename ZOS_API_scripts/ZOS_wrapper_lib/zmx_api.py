import clr
import os
import winreg


def connect_zmx_interactive():
    # determine the Zemax working directory
    aKey = winreg.OpenKey(winreg.ConnectRegistry(None,
                                                 winreg.HKEY_CURRENT_USER),
                          r"Software\Zemax", 0, winreg.KEY_READ)
    zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
    NetHelper = os.path.join(os.sep,
                             zemaxData[0],
                             r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
    winreg.CloseKey(aKey)

    # add the NetHelper DLL for locating the OpticStudio install folder
    clr.AddReference(NetHelper)
    import ZOSAPI_NetHelper

    pathToInstall = ''
    # uncomment the following line to use a specific instance of the
    # ZOS-API assemblies
    # pathToInstall = r'C:\C:\Program Files\Zemax OpticStudio'

    # connect to OpticStudio
    success = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(pathToInstall)

    zemaxDir = ''
    if success:
        zemaxDir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory()
        print('Found OpticStudio at:   %s' + zemaxDir)
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

    if TheApplication.IsValidLicenseForAPI is False:
        raise Exception("License is not valid for ZOSAPI use.  Make sure you"
                        " have enabled 'Programming > Interactive Extension'"
                        " from the OpticStudio GUI.")

    TheSystem = TheApplication.PrimarySystem
    if TheSystem is None:
        raise Exception("Unable to acquire Primary system")
    print('Connected to OpticStudio')
    # The connection should now be ready to use.  For example:
    print('Serial #: ', TheApplication.SerialCode)
    return TheSystem, ZOSAPI, ZOSAPI_NetHelper


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
        aKey = winreg.OpenKey(winreg.ConnectRegistry(None,
              winreg.HKEY_CURRENT_USER), r"Software\Zemax", 0, winreg.KEY_READ)  # noqa
        zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
        NetHelper = os.path.join(os.sep, zemaxData[0],
                                 r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
        winreg.CloseKey(aKey)
        clr.AddReference(NetHelper)
        import ZOSAPI_NetHelper
        self.ZOSAPI_NetHelper = ZOSAPI_NetHelper

        # Find the installed version of OpticStudio
        # if len(path) == 0:
        if path is None:
            isInitialized = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize()
        else:
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
            raise PythonStandaloneApplication.ConnectionException("Unable to"
                    " initialize .NET connection to ZOSAPI")  # noqa

        self.TheApplication = self.TheConnection.CreateNewApplication()
        if self.TheApplication is None:
            raise PythonStandaloneApplication.InitializationException("Unable"
                    " to acquire ZOSAPI application")  # noqa

        if self.TheApplication.IsValidLicenseForAPI is False:
            raise PythonStandaloneApplication.LicenseException("License is"
                    " not valid for ZOSAPI use")  # noqa

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
        elif self.TheApplication.LicenseStatus == self.ZOSAPI.LicenseStatusTypeStandardEdition:  # noqa
            return "Standard"
        else:
            return "Invalid"

        zos = PythonStandaloneApplication()
        return zos


def connect_zmx_standalone():
    zos = PythonStandaloneApplication()
    return zos.TheSystem, zos.ZOSAPI, zos.ZOSAPI_NetHelper
    #    return zos.TheSystem, zos.ZOSAPI, zos.ZOSAPI_NetHelper
