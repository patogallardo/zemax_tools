'''Opens chief ray director angles produced by ZPL script

Author: Patricio Gallardo
03/17/2018'''
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import GrasPy
import pandas as pd
import re

class chiefRays():
    def __init__(self, fname):
        self.fname = fname
        self.title = fname.split(".txt")[0]
        self.conf_string = re.match(".*(Conf[0-9][0-9]).*", fname).groups(1)[0]
        df = pd.read_csv(fname, 
                         encoding = 'utf_16', 
                         delim_whitespace=True)
        df['angle'] = 90 - np.rad2deg(
                          np.arccos(
                          np.sqrt(df.l**2 + df.m**2)/df.n )) 
        self.df = df

    def plotMap(self, show=False):
        '''Quick implementation, fix later'''
        plt.figure()
        df = self.df
        plt.hexbin(x=df.Hx.values, 
                   y=df.Hy.values, 
                   C=df["angle"],
                   gridsize=50,
                   cmap='inferno')
        plt.colorbar(label='Chief Ray Angle [deg]')
        plt.title("Chief Ray Angle of Incidence "+self.conf_string)
        if show:
            plt.show()
        else:
            plt.savefig("ChiefRayAngleOfIncidence_"
                        +self.conf_string + ".png", dpi=300)
            plt.close()
    def plotHist(self, show=False):

        df = self.df
        values = df['angle'].values

        pct16 = np.percentile(values, 16)
        pct84 = np.percentile(values, 84)
        median = np.median(values)

        plt.figure()
        plt.hist(values)
        plt.axvline(pct16, alpha = 0.3, color='black' )
        plt.axvline(pct84, alpha = 0.3, color='black' )
        
        text = "$\mu=%1.2f$\n$\sigma_-=%1.2f$\n$\sigma_+=%1.2f$"%(median, median-pct16, pct84-median)
        plt.figtext(0.7,0.7, text)


        plt.title("Chief ray angle of incidence, " + self.conf_string)
        plt.xlabel("Angle [deg]")
        plt.ylabel("N")
        if show:
            plt.show()
        else:
            plt.savefig("ChiefRayAngleOfIncidence"+ self.conf_string + "_Hist.png", dpi=300)
            plt.close()


        



