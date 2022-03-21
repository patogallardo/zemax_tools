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

extent = [-6, 6, -6, 6]
fig, axs = plt.subplots(nrows=3, ncols=3,
                        figsize=(6.0, 7.5),
                        subplot_kw={'xticks': np.arange(-6, 9, 3),
                                    'yticks': np.arange(-6, 9, 3)})
vmin, vmax = -75, 0
for ax, z in zip(axs.flat, zs):
    im = ax.imshow(10 * np.log10(z),
                   cmap='viridis',
                   extent=extent,
                   vmin=vmin,
                   vmax=vmax)
    ax.grid(color='gray',
            alpha=0.35)
#    ax.set_title(str(j))

# cbar_ax = fig.add_axes([0.15, 0.07, 0.7, 0.015])
# fig.colorbar(im, cax=cbar_ax, orientation='horizontal')
plt.subplots_adjust(left=0.05,
                    right=0.99,
                    top=0.99,
#                    bottom=0.05,  # noqa
                    hspace=0.05,
                    wspace=0.2)

fig.colorbar(im, ax=axs,
             orientation='horizontal',
             fraction=0.02,
             label='dB',
             aspect=20,
             pad=0.09)

# plt.tight_layout()
if show:
    plt.show()
else:
    plt.savefig('beams.pdf')
    plt.close()
