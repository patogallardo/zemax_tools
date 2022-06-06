import numpy as np
import glob
import re
import matplotlib.pyplot as plt
import os

show = False
fnames = glob.glob('crosspol/cam_*_field_*.txt')
fnames.sort()

Ts = np.zeros(len(fnames))
for j, fname in enumerate(fnames):
    with open(fname, 'r', encoding='utf-16le') as f:
        for line in f:
            if "Transmission" in line:
                transmission_line = line
                found = re.findall("\d+\.\d+", transmission_line)
                assert len(found) == 1
                T = float(found[0])
                Ts[j] = T


T_db = 10 * np.log10(1-Ts/100)
table = "N fields:%i\nmin: %1.2f dB\nmax:%1.2f dB" % (len(Ts), min(T_db),
                                                      max(T_db))

plt.hist(T_db,
         histtype="step",
         color='black',
         density=False,
         bins=15)
plt.figtext(0.15, 0.75, table)
plt.xlabel('Cross pol [dB]')
plt.ylabel('count [-]')
if show:
    plt.show()
else:
    plt.savefig("crosspol/crosspol_hist.pdf")
    plt.close()

fnameout = os.path.abspath("./crosspol/crosspol_output.npz")
np.savez(fnameout, T_db=T_db)
