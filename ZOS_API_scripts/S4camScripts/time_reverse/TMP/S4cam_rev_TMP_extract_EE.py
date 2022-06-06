import zmx_api
import numpy as np
import os
import matplotlib.pyplot as plt  # noqa
from progressbar import progressbar


show = False
TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()  # noqa

Wavelengths = TheSystem.SystemData.Wavelengths
Fields = TheSystem.SystemData.Fields
MCE = TheSystem.MCE
NumberOfConfigurations = TheSystem.MCE.NumberOfConfigurations

NumberOfWavelengths = Wavelengths.NumberOfWavelengths

if not os.path.exists('./encircled_energies'):
    os.mkdir('./encircled_energies')

WavelengthNumber = 1
UsePol = True
Analyses = TheSystem.Analyses
FieldNumbers = np.array([1, 2, 3, 4, 5, 6, 8, 9, 12, 15, 18, 22, 25, 28, 31, 32, 35, 38, 41])  # noqa
ys = []

# comment this line for production
# NumberOfConfigurations = 2

for configuration in progressbar(range(1, NumberOfConfigurations + 1)):
    MCE.SetCurrentConfiguration(configuration)
    y_thiscam = []
    for field_counter, FieldNumber in enumerate(FieldNumbers):
        win = Analyses.New_DiffractionEncircledEnergy()
        settings = win.GetSettings()

        settings.Field.SetFieldNumber(FieldNumber)
        settings.Wavelength.SetWavelengthNumber(WavelengthNumber)
        settings.SampleSize = ZOSAPI.Analysis.SampleSizes.S_128x128
        settings.HuygensSample = ZOSAPI.Analysis.SampleSizes.S_128x128
        settings.Type = ZOSAPI.Analysis.Settings.EncircledEnergy.EncircledEnergyTypes.Encircled # Y_Linear  # noqa
        settings.ReferTo = ZOSAPI.Analysis.Settings.EncircledEnergy.ReferToTypes.Centroid  # noqa
        settings.UseHuygensPSF = True
        settings.UsePolarization = True
        settings.RadiusMaximum = 10

        win.ApplyAndWaitForCompletion()
        res = win.GetResults()
        g = res.DataSeries[0]

        Nx = g.XData.Length
        x, y = np.zeros(Nx), np.zeros(Nx)

        for i in range(Nx):
            x[i] = g.XData.Data[i]
            y[i] = g.YData.Data[i, 0]
        win.Close()

        y_thiscam.append(y)
    ys.append(y_thiscam)

ys = np.array(ys)
np.savez('./encircled_energies/ee.npz',
         ys=ys, x=x)
