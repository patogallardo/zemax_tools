import zmx_api
import numpy as np
import os
import matplotlib.pyplot as plt
from progressbar import progressbar
from skimage.feature import canny
from skimage.measure import EllipseModel

show = False
TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()  # noqa

Wavelengths = TheSystem.SystemData.Wavelengths
Fields = TheSystem.SystemData.Fields
MCE = TheSystem.MCE
NumberOfConfigurations = TheSystem.MCE.NumberOfConfigurations

NumberOfWavelengths = Wavelengths.NumberOfWavelengths
FieldNumbers = [1, 2, 3, 4, 5, 6, 7,
                20, 23, 26, 29]  # slow run
# FieldNumbers = [1, 2, 20]  # fast run


def get_ellipse(x, y, beam_linear, level=0.5):
    mask = beam_linear > level
    xx, yy = np.meshgrid(x, y)
    ed = canny(mask, sigma=1)
    x_ed, y_ed = xx[ed], yy[ed]
    data = np.vstack((x_ed, y_ed))
    ellipse = EllipseModel()
    ellipse.estimate(data.T)
    x_c, y_c, semi_x, semi_y, theta = ellipse.params
    return ellipse


if not os.path.exists('./psf2d'):
    os.mkdir('./psf2d')

FieldNumber = 1
WavelengthNumber = 1
UsePol = True
NormalizeToOne = 1
zs = []
# get analysis
Analyses = TheSystem.Analyses

# DELETE THESE TWO LINES FOR PRODUCTION
# NumberOfConfigurations = 2
# FieldNumbers = [1, 3, 4]

semi_a = np.zeros([NumberOfConfigurations, len(FieldNumbers)])
semi_b = np.zeros([NumberOfConfigurations, len(FieldNumbers)])
for configuration in progressbar(range(1, NumberOfConfigurations + 1)):
    MCE.SetCurrentConfiguration(configuration)
    for field_counter, FieldNumber in enumerate(FieldNumbers):
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
        x, y = np.zeros(Nx), np.zeros(Ny)

        for i in range(Nx):
            x[i] = g.X(i)
        for i in range(Ny):
            y[i] = g.Y(i)

        for i in range(Ny):
            for j in range(Nx):
                z[i, j] = g.Z(i, j)
        zs.append(z)
        win.Close()

        extent = [-6, 6, -6, 6]
        plt.figure(figsize=(5, 4))
        vmin, vmax = -75, 0

        beam_linear = z
        beam_db = 10 * np.log10(z)

        ellipse = get_ellipse(x, y, beam_linear)
        a, b = ellipse.params[2], ellipse.params[3]
        semi_a[configuration-1, field_counter] = ellipse.params[2]
        semi_b[configuration-1, field_counter] = ellipse.params[3]

        c = plt.pcolormesh(x, y, beam_db,
                           cmap='viridis',
                           vmin=vmin,
                           vmax=vmax)
        plt.contour(x, y,
                    beam_linear,
                    levels=[0.5])
        plt.grid(color='gray', alpha=0.35)
        plt.colorbar(c, label='dB', aspect=20, pad=0.09)
        plt.title("Cam: %02i, Field: %02i" % (configuration,
                                              FieldNumber))
        long = max(a, b)
        short = min(a, b)
        plt.figtext(0.49, 0.75,
                    "a: %1.3f arcmin\nb: %1.3f arcmin\na/b=%1.2f" % (long, short, long/short))  # noqa
        plt.xlim([-3, 3])
        plt.ylim([-3, 3])
        plt.xlabel('x [arcmin]')
        plt.ylabel('y [arcmin]')
        if show:
            plt.show()
        else:
            fnameout = "cam_%02i_field_%02i.pdf" % (configuration,
                                                    FieldNumber)
            plt.savefig('./psf2d/%s.pdf' % fnameout)
            plt.savefig('./psf2d/%s.png' % fnameout)
            plt.close()

np.savez("psf2d/arrays.npz", semi_a=semi_a, semi_b=semi_b)
