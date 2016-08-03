'''
Created on 26.07.2016

@author: Kushtrim Sylejmani
'''

import astropy
import os
import sys
import collections
import re
import matplotlib

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from astropy import wcs
from astropy.io import fits

from astropy.io.fits import getval
from astropy.io.fits import getdata
from datetime import datetime
from matplotlib.pyplot import savefig
from mailcap import show




#=================================================================================================================
# Source: http://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
#=================================================================================================================

def atoi(text):
    return int(text) if text.isdigit() else text
    
def natural_keys(text):
    return [atoi(c) for c in re.split('(\d+)', text) ]



#===============================================================================
# Filter coarse by 'bpmap_photon.fits'
#===============================================================================

filteredList = []
path = 'files/Erster_hsp_6120421_26454/coarse/'
pathA = 'files/Zweiter_hsp_2031207_4934/coarse/'
savePath = "files/generatedImages/"

for fileName in os.listdir(path):
    if fileName.endswith("bpmap_photon.fits"):
        filteredList.append(fileName)

flareMapTime = {}
for currentFile in filteredList:
    hdulist = fits.open(path + currentFile)
    print repr(hdulist[1].header)
    #===========================================================================
    # cols = hdulist[0].columns
    # print cols
    #===========================================================================
    print "\n"
    
    key = getval(path + currentFile, "DATE_OBS")
    
    if key in flareMapTime:
        flareMapTime[key].append(currentFile)
        flareMapTime[key].sort(key=natural_keys)
    else:
        flareMapTime[key] = [currentFile]
    

odTime = collections.OrderedDict(sorted(flareMapTime.items()))

#===============================================================================
# for key, value in odTime.iteritems():
#     print key + ", " + str(value)
#  
# print "\n"
#===============================================================================


filteredEnergyMap = {}
for key, value in odTime.iteritems():
    for fileName in value:
        energyL = int(fileName.split("_")[0].split(".")[0])
        if energyL in filteredEnergyMap:
            filteredEnergyMap[energyL].append(fileName)
        else:
            filteredEnergyMap[energyL] = [fileName]
    

odEnergy = collections.OrderedDict(sorted(filteredEnergyMap.items()))

#===============================================================================
# for key, value in odEnergy.iteritems():
#     print str(key) + ", " + str(value)
# 
# print "\n"
#===============================================================================

#===============================================================================
# number = 0
#  
# print "Creating images for time differences..."
# for key, value in odEnergy.items():
#     print "LowEngery: " + str(key) +", proceeding..."
#     for index in range(len(value)):
#         if not os.path.exists(savePath + "timeDifference/" + str(key)):
#             os.makedirs(savePath + "timeDifference/" + str(key))
#                  
#         nextIndex = index + 1
#         if nextIndex < len(value):
#             number = number + 1
#             currentFITS = getdata(path + value[index])
#             nextFITS = getdata(path + value[nextIndex])
#             differenceFITS = nextFITS - currentFITS
#             plt.imshow(differenceFITS)            
#             plt.savefig(savePath + "timeDifference/" + str(key) +"/" + "foo" + str(number) +".png")
#               
#         else:
#             print "LowEngery: " + str(key) +", finshed.\n"    
#===============================================================================


#===============================================================================
# print "odTime: \n"
# for key, value in odTime.items():
#     print str(key) + ", " + str(value)
#===============================================================================

#===============================================================================
# print "Creating images for spectrum differences..."
# spectrumFITS = fits.open(path + "hsi_spectrum.fits")
# print repr(spectrumFITS[1].header)
# a = getdata(path + "hsi_spectrum.fits")
# 
# hdulist = fits.open(path + "hsi_spectrum.fits")
# cols = hdulist[1].columns
# print cols
#===============================================================================
        
        
        
#===============================================================================
#         date = key.replace(":", "-").replace(".", "-")
#         if not os.path.exists(savePath + "spectrumDifference/" + date):
#             os.makedirs(savePath + "spectrumDifference/" + date)
#             
#         nextIndex = index + 1
#         if nextIndex < len(value):
#             number = number + 1
#             currentFITS = getdata(path + value[index])
#             nextFITS = getdata(path + value[nextIndex])
#             differenceFITS = nextFITS - currentFITS
#             print "Sum: " + str(np.sum(differenceFITS)) 
#             print "Mean: " + str(np.mean(differenceFITS))            
#             print "Deviation / Sigma: " + str(np.std(differenceFITS))
#             plt.hist(differenceFITS)
#             #===================================================================
#             # plt.show()
#             #===================================================================
#             plt.imshow(differenceFITS)            
#             plt.savefig(savePath + "spectrumDifference/" + date + "/" + "foo" + str(number) + ".png")
# 
#         else:
#             print "Time: " + str(key) + ", finshed."
#             print "==================================================================\n"       
#===============================================================================
            
#=====================================================================
#   dateEndFits = getval(path + value[index], "DATE_END")      
#   date = dateEndFits.split("T")[0]
#   time = dateEndFits.split("T")[-1]
#   dateEnd = datetime.strptime(date + time, '%Y-%m-%d%H:%M:%S.%f')
# 
#   dateStartFits = getval(path + value[nextIndex], "DATE_OBS")
#   dateA = dateStartFits.split("T")[0]
#   timeA = dateStartFits.split("T")[-1]
#   dateStart = datetime.strptime(dateA + timeA, '%Y-%m-%d%H:%M:%S.%f')
#     
#   print "#=============================================================================================="
#   print "# FITS-File B: " + value[index] + ", dateEnd: " + str(dateEnd)
#   print "# FITS-File A: " + value[nextIndex] + ", dateStart: " + str(dateStart)
#   print "#"
#   timeDifference = dateStart - dateEnd
#   print "# timeDifference: " + str(timeDifference)
#   print "#=============================================================================================="
#   print "\n"
#=====================================================================

print "Process succeeded"            
            
