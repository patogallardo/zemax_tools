'''Extracts coordinate systems from all mirrors in various formats.
'''
import sys
import glob
from zmx_api import connect_zmx_interactive
import os
import numpy as np
import pandas as pd


def get_rot_mat_origin(LDE, surface):
    globalMatrix = LDE.GetGlobalMatrix(surface,  # zeros seem pointless
                                       0, 0, 0, 0, 0, 0, 0, 0,
                                       0, 0, 0, 0)[1:]
    RotMat = np.reshape(globalMatrix[:9], [3, 3])
    origin = np.array(globalMatrix[9:])
    return RotMat, origin


TheSystem, ZOSAPI, ZOSAPI_NetHelper = connect_zmx_interactive()

if len(sys.argv) == 2:  # optional support for specifying filename
    fname = sys.argv[1]
else:
    print('No file name provided, searching current directory')
    fnames = glob.glob('*.zmx')
    assert len(fnames) == 1
    fname = fnames[0]
fname = os.path.abspath(fname)
print("opening: %s" % fname)

TheSystem.LoadFile(fname, False)
LDE = TheSystem.LDE

surfaces_to_extract = []
for j in range(1, LDE.NumberOfSurfaces):
    s = LDE.GetSurfaceAt(j)
    c = s.Comment
    if (s.Material.lower() == 'mirror' or
            c == "Front of cryo plate" or c == "TMP_image"):
        surfaces_to_extract.append(j)

surface_names = []
for surface_num in surfaces_to_extract:
    surface_names.append(LDE.GetSurfaceAt(surface_num).Comment)

position_angles_table = []
RotMats = []
for j, surface_num in enumerate(surfaces_to_extract):
    name = surface_names[j]
    RotMat, origin = get_rot_mat_origin(LDE, surface_num)
    x_angle = np.rad2deg(np.arctan2(-1 * RotMat[1, 2], RotMat[2, 2]))

    row = [name, origin[0], origin[1], origin[2], x_angle]
    position_angles_table.append(row)
    RotMats.append(RotMat)

df = pd.DataFrame(position_angles_table,
                  columns=['surface', 'X[mm]', 'Y[mm]', 'Z[mm]',
                           'alpha [deg]'])
tex_str = df.to_latex(float_format="%.3f", index=False)
tex_str = tex_str.replace("{}",
                          "\\bf{%s}" % fname.split("\\")[-1].replace(
                              "_", "\\textunderscore "))
tex_str = tex_str.replace("alpha", "$\\alpha$")
with open("coordinate_sys_pos_rot_angles.tex", 'w') as f:  # noqa
    f.write(tex_str)


for j, RotMat in enumerate(RotMats):
    df = pd.DataFrame(RotMat)
    fname_out = surface_names[j] + "_rotmat.tex" # noqa
    df.to_latex(fname_out,
                float_format="%.5f", index=False, header=False)
