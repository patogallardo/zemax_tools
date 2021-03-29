import glob
import os
import subprocess
import sys

scripts_path = r"C:\Users\pgall\Documents\Zemax\Macros"
fnames = glob.glob('*.zmx')
assert len(fnames) == 1
fname = os.path.abspath(fnames[0])
assert len(sys.argv) == 2
zpl_script = sys.argv[1]
print(zpl_script)
cwd = os.path.abspath('./')

opticstudio = r'C:\Program Files\Zemax OpticStudio\OpticStudio.exe'

command = [opticstudio,
           r'-zpl=%s' % os.path.join(scripts_path, zpl_script),
           r'-vFileName=%s' % fname]
print(command)
p = subprocess.Popen(command,
                     cwd=cwd)
p.wait()
