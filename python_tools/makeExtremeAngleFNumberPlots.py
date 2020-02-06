import extremeAnglesFNumbs as exAF
import glob
import os
import datetime
import concurrent.futures
import pptx2pdf

wd = os.getcwd()
DesignName = wd.split("\\")[-2]

fnames = glob.glob("*.txt")

def makePlots(fname):
    ea = exAF.extremeAngles(fname)
    ea.plotMap(show=False)
    ea.plotHist(show=False)
    ea.df.to_csv("F_av_" + fname.split(".")[0]+".csv")

map(makePlots, fnames)

import slidesFromPlots as sl

imgTemplate = [ "FNumber_av_Conf??.png",
                'FNumber_Config_??_Hist.png']

now = datetime.datetime.now()
signature = 'PAG%02i%02i%02i_' % (now.year, now.month, now.day)

fnameOut = signature + 'Design_%s_FNumbers.pptx'%DesignName
slides = sl.compileSlides(imgStrings = imgTemplate, fnameOut=fnameOut)

pptx2pdf.pptx2pdf(fnameOut)

