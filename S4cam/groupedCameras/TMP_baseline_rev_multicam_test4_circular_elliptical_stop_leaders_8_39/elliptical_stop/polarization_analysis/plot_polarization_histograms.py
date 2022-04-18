'''Opens results from distorted mirrors and plots histograms of polarization
leakage'''
import matplotlib.pyplot as plt
import numpy as np
import os

fname1 = os.path.abspath("./crosspol/crosspol_output.npz")
fname2 = os.path.abspath("../gravitational_thermal_deformations/polarization/crosspol/crosspol_output.npz")  # noqa

pols1 = np.load(fname1)["T_db"]
pols2 = np.load(fname2)["T_db"]

plt.hist(pols1, histtype='step')
plt.hist(pols2, histtype='step')

plt.savefig("polarization_histograms.pdf")
