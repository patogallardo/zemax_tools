'''Opens extreme ray angle cosines and produces 
average f numbers among the extreme rays

Author: Patricio Gallardo
03/17/2018'''
import numpy as np
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import GrasPy
import pandas as pd
import re

def FN(angle):
    return 0.5/np.tan(np.deg2rad(angle))

class extremeAngles():
    def __init__(self, fname):
        self.fname = fname
        self.title = fname.split(".txt")[0]
        self.conf_string = re.match("ExtremeAngles([0-9][0-9]).*", fname).groups(1)[0]
        df = pd.read_csv(fname, 
                         encoding = 'utf_16', 
                         delim_whitespace=True)
        df['angle0'] = 90 - np.rad2deg(
                          np.arccos(
                          np.sqrt(df['l']**2 + df['m']**2)/df['n'] ))
        df['angle1'] = 90 - np.rad2deg(
                          np.arccos(
                          np.sqrt(df['l.1']**2 + df['m.1']**2)/df['n.1'] ))
        df['angle2'] = 90 - np.rad2deg(
                          np.arccos(
                          np.sqrt(df['l.2']**2 + df['m.2']**2)/df['n.2'] ))
        df['angle3'] = 90 - np.rad2deg(
                          np.arccos(
                          np.sqrt(df['l.3']**2 + df['m.3']**2)/df['n.3'] ))
        df["FN0"] = FN(df['angle0'])
        df["FN1"] = FN(df['angle1'])
        df["FN2"] = FN(df['angle2'])
        df["FN3"] = FN(df['angle3'])
        df["FN_av"] = (df.FN0 + df.FN1 + df.FN2 + df.FN3)/4. 
        self.df = df

    def plotMap(self, show=False):
        '''Quick implementation, fix later'''
        plt.figure()
        df = self.df
        plt.hexbin(x=df.Hx.values, 
                   y=df.Hy.values, 
                   C=df["FN_av"],
                   gridsize=50,
                   cmap='inferno')
        plt.colorbar(label='$F/\#_{av}$')
        plt.title("$F/\#_{av}$ for Conf "+self.conf_string)
        if show:
            plt.show()
        else:
            plt.savefig("FNumber_av_Conf"
                        +self.conf_string + ".png", dpi=300)
            plt.close()
    def plotHist(self, show=False):

        df = self.df
        values = df['FN_av'].values

        pct16 = np.percentile(values, 16)
        pct84 = np.percentile(values, 84)
        median = np.median(values)

        plt.figure()
        plt.hist(values)
        plt.axvline(pct16, alpha = 0.3, color='black' )
        plt.axvline(pct84, alpha = 0.3, color='black' )
        plt.axvline(median, color='black')
        
        text = "$\mu=%1.2f$\n$\sigma_-=%1.2f$\n$\sigma_+=%1.2f$"%(median, median-pct16, pct84-median)
        plt.figtext(0.7,0.7, text)


        plt.title("$F/\#_{av}$ " + self.conf_string)
        plt.xlabel("$F/\#_{av}$")
        plt.ylabel("N")
        if show:
            plt.show()
        else:
            plt.savefig("FNumber_Config_"+ self.conf_string + "_Hist.png", dpi=300)
            plt.close()
