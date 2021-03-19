import clr
import os
import winreg
import pandas as pd  # noqa
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import glob

#  plt.rcParams.update({"text.usetex": True})

aKey = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),
                      r"Software\Zemax", 0, winreg.KEY_READ)
zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
NetHelper = os.path.join(os.sep, zemaxData[0],
                         r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
winreg.CloseKey(aKey)

# add the NetHelper DLL for locating the OpticStudio install folder
clr.AddReference(NetHelper)
import ZOSAPI_NetHelper  # noqa

pathToInstall = ''
success = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(pathToInstall)

zemaxDir = ''
if success:
    zemaxDir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory()
    print('Found OpticStudio at:   %s' + zemaxDir)
else:
    raise Exception('Cannot find OpticStudio')

# load the ZOS-API assemblies
clr.AddReference(os.path.join(os.sep, zemaxDir, r'ZOSAPI.dll'))
clr.AddReference(os.path.join(os.sep, zemaxDir, r'ZOSAPI_Interfaces.dll'))
import ZOSAPI  # noqa

TheConnection = ZOSAPI.ZOSAPI_Connection()
if TheConnection is None:
    raise Exception("Unable to intialize NET connection to ZOSAPI")

TheApplication = TheConnection.ConnectAsExtension(0)
if TheApplication is None:
    raise Exception("Unable to acquire ZOSAPI application")


if TheApplication.IsValidLicenseForAPI==False:  # noqa
    raise Exception("License is not valid for ZOSAPI use."
                    "  Make sure you have enabled 'Programming"
                    " > Interactive Extension' from the OpticStudio GUI.")

TheSystem = TheApplication.PrimarySystem
if TheSystem is None:
    raise Exception("Unable to acquire Primary system")
print('Connected to OpticStudio')

# The connection should now be ready to use.  For example:
print('Serial #: ', TheApplication.SerialCode)

# Insert Code Here
targetdirs = ["CAD", 'CAD/sag_tables']
for targetdir in targetdirs:
    if not os.path.exists(targetdir):
        os.mkdir(targetdir)


def mk_tex(tex_table, label, targetdir):
    '''Write the tex file with the table and compile it'''
    tex_out_fname = os.path.join(targetdir,
                                 "%s_shape_table.tex" % label)

    out_str = ("\\documentclass[convert={convertexe={magick.exe}}]{standalone}"  # noqa
               "\n\\usepackage{booktabs}"
               "\n\\begin{document}")
    out_str += tex_table + "\n\\end{document}"
    with open(tex_out_fname, "w") as f:
        f.write(out_str)
    print(out_str)
    subprocess.run('pdflatex --shell-escape %s_shape_table.tex' % label,
                   cwd=targetdir)


fnames = glob.glob('./*.zmx')
assert len(fnames) == 1
fname = os.path.abspath(fnames[0])
print("Opening: %s" % fname)

show = False
lde = TheSystem.LDE
mce = TheSystem.MCE

surfaces_to_evaluate = [44, 50, 58]
sag_sign = [+1, -1, +1]
labels = ['L1', 'L2', 'L3']
xlim = [-100, 100]
ylim = [0, 10]

sags = [] * len(surfaces_to_evaluate)

configuration = 1
mce.SetCurrentConfiguration(configuration)

for j in range(len(surfaces_to_evaluate)):
    surface = surfaces_to_evaluate[j]

    s = lde.GetSurfaceAt(surface)
    semiDia = s.SemiDiameter
    rs = np.linspace(-semiDia, semiDia, 500)
    sag_x = np.array([lde.GetSag(surface, r, 0.0, 0, 0)[1] for r in rs])
    sag_y = np.array([lde.GetSag(surface, 0.0, r, 0, 0)[1] for r in rs])

    rs_coarse = np.arange(0, semiDia+10, 10)
    sag_x_coarse = np.abs(np.array([lde.GetSag(surface, r, 0.0, 0, 0)[1]
                                    for r in rs_coarse]))
    sag_y_coarse = np.abs(np.array([lde.GetSag(surface, 0.0, r, 0, 0)[1]
                                    for r in rs_coarse]))
    col_names = ["r=%i mm" % r for r in rs_coarse]
    df = pd.DataFrame([sag_x_coarse, sag_y_coarse],
                      index=['x', 'y'],
                      columns=col_names)
    print(df)
    df.to_csv(os.path.join(targetdirs[1], "%s_shape_table.csv" % labels[j]))

    tex_str = df.to_latex(float_format="%.3f")
    mk_tex(tex_str, labels[j], targetdirs[1])

    plt.figure(figsize=[10, 3.5])
    plt.plot(rs, sag_x * sag_sign[j], label='x')
    plt.plot(rs, sag_y * sag_sign[j], label='y')

    plt.legend(loc='lower right')
    plt.grid()
    plt.xticks(np.arange(-100, 110, 10))
    plt.title(labels[j])

    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.xlabel('r [mm]')
    plt.ylabel('sag [mm]')
    plt.tight_layout()
    if show:
        plt.show()
    else:
        plt.savefig(os.path.join(targetdirs[1],
                                 './%s_lens_shape.png' % labels[j]),
                    dpi=300)
        plt.close()
