import os
import pandas as pd  # noqa
import numpy as np
import matplotlib.pyplot as plt  # noqa
import subprocess
import glob
import zmx
import zmx_api

#  plt.rcParams.update({"text.usetex": True})
zos = zmx_api.PythonStandaloneApplication()
TheSystem = zos.TheSystem
# Insert Code Here
targetdirs = ["CAD", 'CAD/sag_tables']
for targetdir in targetdirs:
    if not os.path.exists(targetdir):
        os.mkdir(targetdir)


def mk_tex(tex_table, label, targetdir):
    '''Write the tex file with the table and compile it'''
    tex_out_fname = os.path.join(targetdir,
                                 "%s_surface_values_table.tex" % label)

    out_str = ("\\documentclass[convert={convertexe={magick.exe}}]{standalone}"  # noqa
               "\n\\usepackage{booktabs}"
               "\n\\usepackage{cmbright}"
               "\n\\begin{document}")
    out_str += tex_table + "\n\\end{document}"
    with open(tex_out_fname, "w") as f:
        f.write(out_str)
    print(out_str)
    subprocess.run('pdflatex --shell-escape %s_surface_values_table.tex' % label,  # noqa
                   cwd=targetdir)


fnames = glob.glob('./*.zmx')
assert len(fnames) == 1
fname = os.path.abspath(fnames[0])
print("Opening: %s" % fname)
TheSystem.LoadFile(fname, False)

show = False
lde = TheSystem.LDE
mce = TheSystem.MCE

mirror_names, mirror_surfaces = zmx.get_mirror_surfaces(TheSystem)  # noqa

xlim = [-5000, 5000]
ylim = [-5000, 5000]
semiDia = 2500

sags = [] * len(mirror_surfaces)


for j in range(len(mirror_surfaces)):
    surface = mirror_surfaces[j]

    s = lde.GetSurfaceAt(surface)

    rs_coarse = np.arange(-semiDia, semiDia+10, 500)
    sag_x_coarse = np.array([lde.GetSag(surface, r, 0.0, 0, 0)[1]
                             for r in rs_coarse])
    sag_y_coarse = np.array([lde.GetSag(surface, 0.0, r, 0, 0)[1]
                             for r in rs_coarse])

    col_names = ["r=%i mm" % r for r in rs_coarse]
    df = pd.DataFrame([sag_x_coarse, sag_y_coarse],
                      index=['(r, 0)', '(0, r)'],
                      columns=col_names)
    print(df)
    df.to_csv(os.path.join(targetdirs[1],
                           "%s_surface_values_table.csv" % mirror_names[j]))

    name = {"prime": "M1", "second": "M2", "tert": "M3"}
    tex_str = df.to_latex(float_format="%.3f")
    tex_str = tex_str.replace("{}",
                              "\\bf{%s}" % name[mirror_names[j]])
    mk_tex(tex_str, mirror_names[j], targetdirs[1])
