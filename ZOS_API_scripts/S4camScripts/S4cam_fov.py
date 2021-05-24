import zmx_api
import glob
import os
from zmx_plot import mk_hex

fnames = glob.glob("*.zmx")
assert len(fnames) == 1
fname = os.path.abspath(fnames[0])

print("Opening file: %s" % fname)


def extract_values_MCE(TheSystem, row):
    MCE = TheSystem.MCE
    NCONF = MCE.NumberOfConfigurations
    op = MCE.GetOperandAt(row)
    values = [op.GetOperandCell(j).DoubleValue for j in range(1, NCONF+1)]
    return values


zos = zmx_api.PythonStandaloneApplication()
TheSystem = zos.TheSystem
TheSystem.LoadFile(fname, False)

row_x = 8
row_y = 9
row_semifov = 45

x_mm = extract_values_MCE(TheSystem, row_x)
y_mm = extract_values_MCE(TheSystem, row_y)
fov = extract_values_MCE(TheSystem, row_semifov)


mk_hex(x_mm, y_mm, fov, upper_lower=None,
       show=False, fig_title="Semi-fov",
       colorbar_label="semi-fov [deg]",
       plot_fname='./f_numbers/summary_semi_fov')
