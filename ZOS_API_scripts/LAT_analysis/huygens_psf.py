import zmx_api
import numpy as np
import os
from progressbar import progressbar

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()  # noqa

Wavelengths = TheSystem.SystemData.Wavelengths
Fields = TheSystem.SystemData.Fields
MCE = TheSystem.MCE
NumberOfConfigurations = TheSystem.MCE.NumberOfConfigurations

NumberOfWavelengths = Wavelengths.NumberOfWavelengths
NumberOfFields = Fields.NumberOfFields

if not os.path.exists('./psfcut'):
    os.mkdir('./psfcut')
if not os.path.exists('./psfcut/data'):
    os.mkdir('./psfcut/data')


def get_huygens_cross(TheSystem, FieldNumber,
                      WavelengthNumber,
                      UsePol=True,
                      NormalizeToOne=True):
    Analyses = TheSystem.Analyses
    win = Analyses.New_HuygensPsfCrossSection()
    settings = win.GetSettings()

    settings.Field.SetFieldNumber(FieldNumber)
    settings.Wavelength.SetWavelengthNumber(WavelengthNumber)
    settings.SampleSize = ZOSAPI.Analysis.SampleSizes.S_128x128
    settings.ImageSampleSize = ZOSAPI.Analysis.SampleSizes.S_128x128
    settings.Type = ZOSAPI.Analysis.Settings.PsfTypes.Y_Logarithmic # Y_Linear  # noqa
    settings.UsePolarization = UsePol
    settings.Normalize = NormalizeToOne

    win.ApplyAndWaitForCompletion()
    res = win.GetResults()

    length = res.GetDataSeries(0).XData.Length
    x, y = np.zeros(length), np.zeros(length)

    for j in range(length):
        x[j] = res.GetDataSeries(0).XData.Data[j]
        y[j] = res.GetDataSeries(0).YData.Data[j, 0]
    win.Close()
    return x, y


for Nconf in progressbar(range(1, NumberOfConfigurations+1)):
    MCE.SetCurrentConfiguration(Nconf)
    for NWavelength in range(1, 2):  # NumberOfWavelengths):
        wl = TheSystem.SystemData.Wavelengths.GetWavelength(NWavelength).Wavelength  # noqa
        normalized_to_one = []
        normalized_to_strehl = []
        for Nfield in range(1, NumberOfFields + 1):
            x, y_strehl = get_huygens_cross(TheSystem,
                                            FieldNumber=Nfield,
                                            WavelengthNumber=NWavelength,
                                            UsePol=True,
                                            NormalizeToOne=False)
            normalized_to_strehl.append(y_strehl)
        normalized_to_strehl = np.array(normalized_to_strehl).T
        np.savez('./psfcut/data/conf%02i_wl%04ium.npz' % (Nconf,
                                                    int(wl)),  # noqa
                 psf=normalized_to_strehl,
                 x=x)
