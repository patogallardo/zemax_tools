import numpy as np


def get_mirror_surfaces(TheSystem, material="MIRROR"):
    '''Gets mirror surfaces'''
    lde = TheSystem.LDE
    mce = TheSystem.MCE

    configuration = 1
    mce.SetCurrentConfiguration(configuration)

    nsurf = lde.NumberOfSurfaces

    mirror_surfaces = []
    mirror_names = []

    for surface in range(1, nsurf):
        s = lde.GetSurfaceAt(surface)
        if material.lower() in s.Material.lower():
            mirror_names.append(s.Comment)
            mirror_surfaces.append(surface)

    return mirror_names, mirror_surfaces


def get_lens_surfaces(TheSystem, material="silicon_cold"):
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
        if material in s.Material.lower():
            lens_names.append(s.Comment)
            lens_surfaces.append(surface)
            if np.isinf(s.Radius):
                lens_curved_surfaces.append(surface + 1)
            else:
                lens_curved_surfaces.append(surface)
    return lens_surfaces, lens_curved_surfaces, lens_names


def zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=True):
    print('Running Local Optimization')
    LocalOpt = TheSystem.Tools.OpenLocalOptimization()
    LocalOpt.Algorithm = ZOSAPI.Tools.Optimization.OptimizationAlgorithm.DampedLeastSquares  # noqa
    OptCycles = ZOSAPI.Tools.Optimization.OptimizationCycles
    if CyclesAuto:
        LocalOpt.Cycles = OptCycles.Automatic
    else:
        LocalOpt.Cycles = OptCycles.Fixed_5_Cycles
    LocalOpt.NumberOfCores = 8
    LocalOpt.RunAndWaitForCompletion()
    LocalOpt.Close()


def set_variables_or_const(mcerow_variables, conf, mce, ZOSAPI, vars=True):
    for mcerow_variable in mcerow_variables:
        mcerow = mce.GetOperandAt(mcerow_variable)  # set variables
        mcecell = mcerow.GetOperandCell(conf)
        if vars:
            solve = mcecell.CreateSolveType(ZOSAPI.Editors.SolveType.Variable)  # noqa
        else:
            solve = mcecell.CreateSolveType(ZOSAPI.Editors.SolveType.Fixed)
        mcecell.SetSolveData(solve)


def set_rows_zero(mcerow_zeros, conf, mce, ZOSAPI):
    for mce_row in mcerow_zeros:
        mcerow = mce.GetOperandAt(mce_row)
        mcecell = mcerow.GetOperandCell(conf)
        mcecell.DoubleValue = 0.0
