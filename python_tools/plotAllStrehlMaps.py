# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 14:47:41 2017

Generates strehl ratio plots for all the txt files in this folder.

Core library is strehlMaps.py which contains all the handling routines.

@author: pag227
"""

import strehlMaps
import glob
import os
import datetime
import pptx2pdf

wd = os.getcwd()
DesignName = wd.split("\\")[-2]
fnames = glob.glob('*.txt')

for fname in fnames:
    s = strehlMaps.strehlMap(fname, degToMM=135.2/0.65)
    #s.strehlGreaterThan(show=False, limit=0.7)
    #s.strehlAndLayout(limit=0.7, show=False)
    
#    s.strehlGreaterThan(show=False, limit=0.8)
    s.strehlAndLayout(limit=0.8, show=False, shortTitle=True)
    #s.plotHist_maskedRegion()

    
#import slidesFromPlots as sl

#imgTemplate = ["imgQual_imgQualConf_0??_wavelength_1100_FocalPlaneLayout_limit_0p8.png",
#               "imgQual_imgQualConf_0??_wavelength_750_FocalPlaneLayout_limit_0p8.png",
#               "imgQual_imgQualConf_0??_wavelength_2000_FocalPlaneLayout_limit_0p8.png",
#               "imgQual_imgQualConf_0??_wavelength_3000_FocalPlaneLayout_limit_0p8.png",
#               "imgQual_imgQualConf_0??_wavelength_350_FocalPlaneLayout_limit_0p8.png"]
#now = datetime.datetime.now()
#signature = 'PAG%02i%02i%02i_' % (now.year, now.month, now.day)
#
#fnameOut = signature + 'Design_%s_Image_Quality.pptx'%DesignName
#slides = sl.compileSlides(imgStrings = imgTemplate, fnameOut=fnameOut)

#pptx2pdf.pptx2pdf(fnameOut)
