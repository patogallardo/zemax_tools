import chiefRays
import glob
import os
import datetime
import concurrent.futures
import pptx2pdf

wd = os.getcwd()
DesignName = wd.split("\\")[-2]

fnames = glob.glob("*.txt")

def makePlots(fname):
    cr = chiefRays.chiefRays(fname)
    cr.plotMap(show=False)
    cr.plotHist(show=False)

map(makePlots, fnames)

import slidesFromPlots as sl

imgTemplate = [ "ChiefRayAngleOfIncidence_Conf??.png",
                'ChiefRayAngleOfIncidenceConf??_Hist.png']

now = datetime.datetime.now()
signature = 'PAG%02i%02i%02i_' % (now.year, now.month, now.day)

fnameOut = signature + 'Design_%s_ChiefRayAngles.pptx'%DesignName
slides = sl.compileSlides(imgStrings = imgTemplate, fnameOut=fnameOut)

pptx2pdf.pptx2pdf(fnameOut)

