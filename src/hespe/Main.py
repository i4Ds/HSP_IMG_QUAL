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

import scipy.misc as sci
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab

from astropy.io import fits
from datetime import datetime
from mailcap import show
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

path = 'files/Erster_hsp_6120421_26454/coarse/'
pathA = 'files/Zweiter_hsp_2031207_4934/coarse/'
savePath = "files/generatedImages/"


# Main class

def main():
    filteredList = filterFITSFile()
    odTime = sortFilteredListByTime(filteredList)
    # printMap(odTime)
    odEnergy = sortOdTimeByEnergy(odTime)
    # printMap(odEnergy)
    # createImageTimeDifference(odEnergy, odTime)
    createImageEnergyDifference(odTime)


# Source: http://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
# Sort items by string number value


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split('(\d+)', text)]


# Code for printing key and values of a map

def printMap(map):
    for key, value in map.iteritems():
        print key + ", " + str(value)


def getDifferenceFITS(path, value, index):
    currentFITS = fits.getdata(path + value[index])
    nextFITS = fits.getdata(path + value[index + 1])
    differenceFITS = nextFITS - currentFITS
    return differenceFITS


# Filter coarse by 'bpmap_photon.fits'

def filterFITSFile():
    temporaryList = []
    for fileName in os.listdir(path):
        if fileName.endswith("bpmap_photon.fits"):
            temporaryList.append(fileName)

    return temporaryList


# Sorting filteredList by time
# key = start time 
# value = filename(s)


def sortFilteredListByTime(filteredList):
    flareMapTime = {}
    for currentFile in filteredList:
        key = fits.getval(path + currentFile, "DATE_OBS")
        if key in flareMapTime:
            flareMapTime[key].append(currentFile)
            flareMapTime[key].sort(key=natural_keys)
        else:
            flareMapTime[key] = [currentFile]

    # Sort map by key
    odTime = collections.OrderedDict(sorted(flareMapTime.items()))
    return odTime


# Add filenames in filteredEnergyMap by energy
# key = low energy value 
# value = filename(s)

def sortOdTimeByEnergy(odTime):
    filteredEnergyMap = {}
    for key, value in odTime.iteritems():
        for fileName in value:
            energyL = int(fileName.split("_")[0].split(".")[0])
            if energyL in filteredEnergyMap:
                filteredEnergyMap[energyL].append(fileName)
            else:
                filteredEnergyMap[energyL] = [fileName]

    # Sort map by key
    odEnergy = collections.OrderedDict(sorted(filteredEnergyMap.items()))
    return odEnergy


# Creating images by time differences of every FITS File


def createImageTimeDifference(odEnergy, odTime):
    print "#=========================================================#"
    print "# Creating images for time differences..."
    print "#=========================================================#"

    meanList = []
    mapPositionList = []
    for key, value in odEnergy.items():
        print "=================================================================="
        print "LowEnergy: " + str(key) + ", proceeding..."

        for index in range(len(value)):
            if not os.path.exists(savePath + "timeDifference/" + str(key)):
                os.makedirs(savePath + "timeDifference/" + str(key))

            if (index + 1) < len(value):
                startTime = fits.getval(path + value[index], "DATE_OBS")
                mapPosition = odTime.keys().index(startTime)
                mapPositionList.append(mapPosition)

                differenceFITS = getDifferenceFITS(path, value, index)
                plt.imshow(differenceFITS)
                plt.savefig(savePath + "timeDifference/" + str(key) + "/" + str(mapPosition) + ".png")
                plt.clf()

                # scaledFits = sci.bytescale(differenceFITS)
                muFits = np.mean(differenceFITS)
                meanList.append(muFits)

            else:
                # Create mu-Position Chart of every Energy
                plt.plot(mapPositionList, meanList, label="Energy: " + str(key))
                plt.xlabel('Zeit')
                plt.ylabel(r'$\mu$')
                plt.title(r'$\mu$-Position Chart')
                plt.legend()
                plt.savefig(savePath + "timeDifference/" + str(key) + "/muPosition_Chart.png")
                plt.clf()
                mapPositionList = []
                meanList = []

                print "LowEnergy: " + str(key) + ", finished."
                print "==================================================================\n"


# Creating images by energy differences of every FITS File
def createImageEnergyDifference(odTime):
    print "#=========================================================#"
    print "# Creating images for energy differences..."
    print "#=========================================================#"

    sigmaList = []
    timePositionList = []
    energyPositionList = []
    for key, value in odTime.iteritems():
        energyPosition = 0
        print "=================================================================="
        print "Time: " + str(key) + ", proceeding..."
        for index in range(len(value)):
            date = key.replace(":", "-").replace(".", "-")
            if not os.path.exists(savePath + "energyDifference/" + date):
                os.makedirs(savePath + "energyDifference/" + date)

            if (index + 1) < len(value):
                energyPosition += 1
                differenceFITS = getDifferenceFITS(path, value, index)

                mapPosition = odTime.keys().index(key)
                sigmaFits = np.std(differenceFITS)

                if not mapPosition in timePositionList:
                    timePositionList.append(mapPosition)
                sigmaList.append(sigmaFits)
                energyPositionList.append(energyPosition)

                plt.imshow(differenceFITS)
                plt.savefig(savePath + "energyDifference/" + date + "/" + str(energyPosition) + ".png")
                plt.clf()

            else:
                #
                # Abfrage voruebergehend!
                #
                if timePositionList and sigmaList and energyPositionList:
                    fig = plt.figure()
                    ax = fig.gca(projection='3d')
                    X = 31
                    Y = energyPositionList
                    X, Y = np.meshgrid(X, Y)
                    R = np.sqrt(X ** 2 + Y ** 2)
                    Z = sigmaList
                    Z = sigmaList
                    surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm)

                    print "sigmaList: " + str(sigmaList)
                    print "timePositionList: " + str(timePositionList)
                    print "energyPositionList: " + str(energyPositionList)

                    # plt.show()
                    plt.savefig(savePath + "energyDifference/" + date + "/3D_Chart.png")
                    plt.clf()

                sigmaList = []
                timePositionList = []
                energyPositionList = []

                print "Time: " + str(key) + ", finished."
                print "==================================================================\n"


if __name__ == '__main__':
    main()
