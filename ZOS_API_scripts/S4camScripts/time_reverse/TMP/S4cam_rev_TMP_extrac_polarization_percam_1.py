import zmx_api
import os
from progressbar import progressbar
from skimage.feature import canny
from skimage.measure import EllipseModel

show = False
TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()  # noqa

Wavelengths = TheSystem.SystemData.Wavelengths
Fields = TheSystem.SystemData.Fields
MCE = TheSystem.MCE
NumberOfConfigurations = TheSystem.MCE.NumberOfConfigurations
NumberOfSurfaces = TheSystem.LDE.NumberOfSurfaces

NumberOfWavelengths = Wavelengths.NumberOfWavelengths
FieldNumbers = [1, 2, 3, 4, 5, 6, 7,
                20, 23, 26, 29]  # slow run
# FieldNumbers = [1, 2, 20]  # fast run


if not os.path.exists('./crosspol'):
    os.mkdir('./crosspol')

WavelengthNumber = 1
UsePol = True
zs = []
# get analysis
Analyses = TheSystem.Analyses

#  NumberOfConfigurations = 1  # delete for production
for configuration in progressbar(range(1, NumberOfConfigurations + 1)):
    MCE.SetCurrentConfiguration(configuration)
    Fields.ClearVignetting()
    Fields.SetVignetting()
    for field_counter, FieldNumber in enumerate(FieldNumbers):
        analysis = Analyses.New_Analysis(ZOSAPI.Analysis.AnalysisIDM.PolarizationPupilMap)  # noqa
        analysis.Terminate()
        analysis.WaitForCompletion()
        settings = analysis.GetSettings()

        cfgFile = os.environ.get('Temp') + 'pol.cfg'
        settings.SaveTo(cfgFile)

        settings.ModifySettings(cfgFile, 'PPM_SAMP', '9')
        settings.ModifySettings(cfgFile, 'PPM_FIELD', '%i' % FieldNumber)
        settings.ModifySettings(cfgFile, 'PPM_WAVE', '1')
        settings.ModifySettings(cfgFile, 'PPM_SURFACE', '%i' % NumberOfSurfaces)  # noqa
        settings.ModifySettings(cfgFile, 'PPM_JX', '1')
        settings.ModifySettings(cfgFile, 'PPM_JY', '0')
        settings.ModifySettings(cfgFile, 'PPM_PX', '0')
        settings.ModifySettings(cfgFile, 'PPM_PY', '0')
        settings.ModifySettings(cfgFile, 'PPM_ADDCONFIG', '')
        settings.ModifySettings(cfgFile, 'PPM_SUBCONFIGS', '')

        settings.LoadFrom(cfgFile)
        analysis.ApplyAndWaitForCompletion()
        res = analysis.GetResults()

        abspath = os.path.abspath('./')
        fnameout = abspath + "\\crosspol\\cam_%02i_field_%02i.txt" % (configuration,  # noqa
                                        FieldNumber)  # noqa
        res.GetTextFile(fnameout)
        analysis.Close()
