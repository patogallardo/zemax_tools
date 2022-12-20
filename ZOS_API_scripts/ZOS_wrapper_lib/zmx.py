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


def zemax_run_hammer(TheSystem, time_s=120):
    print('\nRunning Hammer Optimization')
    HammerOpt = TheSystem.Tools.OpenHammerOptimization()
    print('\tInitial Merit Function: % 1.10f' % HammerOpt.InitialMeritFunction)
    HammerOpt.RunAndWaitWithTimeout(time_s)
    HammerOpt.Cancel()
    HammerOpt.WaitForCompletion()
    print("Final Merit Function: %1.10f" % HammerOpt.CurrentMeritFunction)
    HammerOpt.Close()


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


def zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=True,
                   algorithm="DLS"):
    print('\nRunning Local Optimization')
    LocalOpt = TheSystem.Tools.OpenLocalOptimization()
    print("\t Initial Merit Function: %1.10f" % LocalOpt.InitialMeritFunction)
    if algorithm == "DLS":
        LocalOpt.Algorithm = ZOSAPI.Tools.Optimization.OptimizationAlgorithm.DampedLeastSquares  # noqa
    elif algorithm == "OD":
        LocalOpt.Algorithm = ZOSAPI.Tools.Optimization.OptimizationAlgorithm.OrthogonalDescent  # noqa
    print("Using method: %s" % algorithm)
    OptCycles = ZOSAPI.Tools.Optimization.OptimizationCycles
    if CyclesAuto:
        LocalOpt.Cycles = OptCycles.Automatic
    else:
#        LocalOpt.Cycles = OptCycles.Fixed_5_Cycles  # noqa
#        LocalOpt.Cycles = OptCycles.Fixed_50_Cycles  # noqa
        LocalOpt.Cycles = OptCycles.Fixed_10_Cycles
    LocalOpt.NumberOfCores = 32
    LocalOpt.RunAndWaitForCompletion()
    print("\t Final Merit Function: %1.10f" % LocalOpt.CurrentMeritFunction)
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


def populate_MFE_with_blanks(MFE, nblanks=100):
    MFE.RemoveOperandsAt(1, MFE.NumberOfOperands)
    for j in range(nblanks):
        MFE.AddOperand()


def set_MFE_row(operandType, row, MFE, ZOSAPI, param1val=None, param2val=None,
                param3val=None, param4val=None, param5val=None,
                param6val=None,
                weight=0.0,
                target=None):
    param1 = ZOSAPI.Editors.MFE.MeritColumn.Param1
    param2 = ZOSAPI.Editors.MFE.MeritColumn.Param2
    param3 = ZOSAPI.Editors.MFE.MeritColumn.Param3
    param4 = ZOSAPI.Editors.MFE.MeritColumn.Param4
    param5 = ZOSAPI.Editors.MFE.MeritColumn.Param5
    param6 = ZOSAPI.Editors.MFE.MeritColumn.Param6

    row = MFE.GetOperandAt(row)
    row.ChangeType(operandType)
    params = [param1, param2, param3, param4, param5, param6]
    paramVals = [param1val, param2val, param3val,
                 param4val, param5val, param6val]
    for j, param in enumerate(params):
        if paramVals[j] is not None:
            cell = row.GetOperandCell(param)
            if type(paramVals[j]) == int:
                cell.IntegerValue = paramVals[j]
            if type(paramVals[j]) == float:
                cell.DoubleValue = paramVals[j]
    if row.TypeName == "BLNK" and type(param1val) is str:
        cell = row.GetOperandCell(1)
        cell.Value = param1val
    row.Weight = weight
    if target is not None:
        row.Target = target
    if weight != 0:
        row.RowColor = ZOSAPI.Common.ZemaxColor.Color3
    elif row.TypeName != 'BLNK':
        row.RowColor = ZOSAPI.Common.ZemaxColor.Color7
