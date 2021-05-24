import zmx_api
import zmx
NCONF = 85

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

MC_ROWS_TO_OPTIMIZE = [11, 12, 45]
LDE_ROW_TO_OPTIMIZE = 39  # thickness


TheSystem.Tools.RemoveAllVariables()
for conf in range(1, NCONF + 1):
    zmx.set_variables_or_const(MC_ROWS_TO_OPTIMIZE, conf,
                               TheSystem.MCE, ZOSAPI, vars=True)

s = TheSystem.LDE.GetSurfaceAt(LDE_ROW_TO_OPTIMIZE)
solve = s.ThicknessCell.CreateSolveType(ZOSAPI.Editors.SolveType.Variable)
s.ThicknessCell.SetSolveData(solve)


#zmx.zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=True)
