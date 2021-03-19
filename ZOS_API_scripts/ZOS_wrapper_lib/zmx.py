import numpy as np


def get_lens_surfaces(TheSystem):
    '''Gets TheSystem and returns a list of the surface numbers
    containing a lens with curvature in it.'''
    lde = TheSystem.LDE
    mce = TheSystem.MCE

    configuration = 1
    mce.SetCurrentConfiguration(configuration)

    nsurf = lde.NumberOfSurfaces

    lens_surfaces = []
    lens_curved_surfaces = []
    lens_names = []
    for surface in range(1, nsurf):
        s = lde.GetSurfaceAt(surface)
        if "silicon_cold" in s.Material.lower():
            lens_names.append(s.Comment)
            lens_surfaces.append(surface)
            if np.isinf(s.Radius):
                lens_curved_surfaces.append(surface + 1)
            else:
                lens_curved_surfaces.append(surface)
    return lens_surfaces, lens_curved_surfaces, lens_names
