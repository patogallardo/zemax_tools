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

FieldNumbers = [1, 3, 5, 9]
WavelengthNumber = 1
UsePol = True
NormalizeToOne = 1
zs = []
# get analysis
Analyses = TheSystem.Analyses
for FieldNumber in progressbar(FieldNumbers):
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
fig, axs = plt.subplots(nrows=2, ncols=4,
                        figsize=(6.0, 3.0),
                        subplot_kw={'xticks': np.arange(-6, 9, 3),
                                    'yticks': np.arange(-6, 9, 3)})
vmin, vmax = -75, 0
for j, (ax, z) in enumerate(zip(axs.flat[:len(FieldNumbers)], zs)):
    im = ax.imshow(10 * np.log10(z),
                   cmap='viridis',
                   extent=extent,
                   vmin=vmin,
                   vmax=vmax)

    ax.set_xticks([-3, 0, 3])
    ax.set_yticks([-3, 0, 3])
    ax.tick_params(axis="y",direction="in", pad=-12)
    ax.tick_params(axis='x', direction='in', pad=-12)

    if j != 0:
        ax.set_axis_off()
    ax.grid(color='gray',
            alpha=0.35)
#    ax.set_title(str(j))

# cbar_ax = fig.add_axes([0.15, 0.07, 0.7, 0.015])
# fig.colorbar(im, cax=cbar_ax, orientation='horizontal')
plt.subplots_adjust(left=0.0,
                    right=1.0,
                    top=1.0,
#                    bottom=0.05,  # noqa
                    hspace=0.00,
                    wspace=0.0)

#fig.colorbar(im, ax=axs,
#             orientation='horizontal',
#             fraction=0.02,
#             label='dB',
#             aspect=20,
#             pad=0.09)

img_fnames = ['spotdiags_forpaper/spotdiag_fld1.png',
              'spotdiags_forpaper/spotdiag_fld3.png',
              'spotdiags_forpaper/spotdiag_fld5.png',
              'spotdiags_forpaper/spotdiag_fld9.png']

import matplotlib.image as mpimg
top_margin = 80
bottom_margin = -372
left_margin = 315
right_margin = -450
for j in range(len(img_fnames)):
    fname_img = img_fnames[j]
    img = mpimg.imread(fname_img)
    ax = axs.flat[4+j]

    ax.imshow(img[top_margin:bottom_margin,
                  left_margin:right_margin])
    ax.set_axis_off()

plt.subplots_adjust(wspace=0, hspace=0, left=0, right=1, bottom=0, top=1)
# plt.tight_layout()
if show:
    plt.show()
else:
    plt.savefig('beams_and_spotdiags.pdf')
    plt.savefig('beams_and_spotdiags.png', dpi=400)
    plt.close()
