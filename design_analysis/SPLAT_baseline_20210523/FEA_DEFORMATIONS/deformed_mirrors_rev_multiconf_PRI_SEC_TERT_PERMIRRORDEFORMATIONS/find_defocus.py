'''Find defocus for LAT
P. Gallardo 2021-10-22
'''
import zmx_api
import zmx

MC_row_toopt = [7]


TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()
MCE = TheSystem.MCE

TheMFE = TheSystem.MFE
OptWizard = TheMFE.SEQOptimizationWizard
Nconf = MCE.NumberOfConfigurations

# Nconf = 2 + 3  # comment out for production run
for currentconf in range(2, Nconf-3+1):  # dont optimize the last three
    # Optimize for smallest RMS Spot, which is "Data" = 1
    TheMFE.RemoveOperandsAt(1, TheMFE.NumberOfOperands)
    for j in range(12):
        TheMFE.AddOperand()
    OptWizard.Data = 1
    OptWizard.OverallWeight = 1
    # Gaussian Quadrature with 3 rings (refers to index number = 2)
    OptWizard.Ring = 2
    # Set air & glass boundaries
    OptWizard.IsGlassUsed = False
    OptWizard.IsAirUsed = False
    OptWizard.IsAssumeAxialSymmetryUsed = False
    # Startat
    OptWizard.StartAt = 10
    OptWizard.Configuration = currentconf
    # And click OK!
    OptWizard.Apply()
    TheSystem.Tools.RemoveAllVariables()
    zmx.set_variables_or_const(MC_row_toopt,
                               currentconf,
                               MCE,
                               ZOSAPI,
                               vars=True)
    zmx.zemax_optimize(TheSystem, ZOSAPI)

# TheSystem.SaveAs(SampleFile)
