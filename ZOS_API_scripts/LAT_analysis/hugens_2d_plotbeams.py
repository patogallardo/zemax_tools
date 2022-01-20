import zmx_api
import numpy as np
import os
import matplotlib.pyplot as plt
from progressbar import progressbar

show = False
TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()  # noqa

Wavelengths = TheSystem.SystemData.Wavelengths
Fields = TheSystem.SystemData.Fields
MCE = TheSystem.MCE
NumberOfConfigurations = TheSystem.MCE.NumberOfConfigurations

NumberOfWavelengths = Wavelengths.NumberOfWavelengths
NumberOfFields = Fields.NumberOfFields

if not os.path.exists('./psf2d'):
    os.mkdir('./psf2d')
if not os.path.exists('./psf2d/data'):
    os.mkdir('./psf2d/data')

FieldNumber = 1
WavelengthNumber = 1
UsePol = True
NormalizeToOne = 1
zs = []
# get analysis
Analyses = TheSystem.Analyses
for FieldNumber in progressbar(range(1, NumberOfFields + 1)):
    win = Analyses.New_HuygensPsf()
    settings = win.GetSettings()

    settings.Field.SetFieldNumber(FieldNumber)
    settings.Wavelength.SetWavelengthNumber(WavelengthNumber)
    settings.SampleSize = ZOSAPI.Analysis.SampleSizes.S_128x128
    settings.ImageSampleSize = ZOSAPI.Analysis.SampleSizes.S_128x128

    settings.Type = ZOSAPI.Analysis.Settings.HuygensPsfTypes.Linear # Y_Linear  # noqa
    settings.UsePolarization = UsePol
    settings.Normalize = NormalizeToOne
    settings.UseCentroid = True
    settings.ImageDelta = 6.0/129.
    settings.Configuration = 1

    win.ApplyAndWaitForCompletion()
    res = win.GetResults()
    g = res.DataGrids[0]
    Nx = g.Nx
    Dx = g.Dx
    Ny = g.Ny
    z = np.zeros([Nx, Ny])
    for i in range(Ny):
        for j in range(Nx):
            z[i, j] = g.Z(i, j)
    zs.append(z)
    win.Close()


fig, axs = plt.subplots(nrows=3, ncols=3,
                        figsize=(7.5, 6),
                        subplot_kw={'xticks': [],
                                    'yticks': []})

for ax, z in zip(axs.flat, zs):
    im = ax.imshow(np.log10(z), cmap='viridis')
#    ax.set_title(str(j))

cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
fig.colorbar(im, cax=cbar_ax)

# plt.tight_layout()
if show:
    plt.show()
else:
    plt.savefig('beams.pdf')
    plt.close()
