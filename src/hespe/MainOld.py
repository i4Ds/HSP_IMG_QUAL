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
from matplotlib.backends.backend_pdf import PdfPages

from astropy.io import fits
from datetime import datetime
from mailcap import show
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

path = 'files/Erster_hsp_6120421_26454/coarse/'
pathA = 'files/Zweiter_hsp_2031207_4934/coarse/'
savePath = "files/generatedImages/"
saveIsValid = True


# Main class

def main():
    filteredList = filterFITSFile()
    odTime = sortFilteredListByTime(filteredList)
    # printMap(odTime)
    odEnergy = sortOdTimeByEnergy(odTime)
    # printMap(odEnergy)
    createImageTimeDifference(odEnergy, odTime)
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
        print str(key) + ", " + str(value)


def printList(list):
    for value in list:
        print "Value: " + str(value)


def getDifferenceFITS(path, fileNameList, index):
    currentFITS = fits.getdata(path + fileNameList[index])
    nextFITS = fits.getdata(path + fileNameList[index + 1])
    differenceFITS = nextFITS - currentFITS
    return differenceFITS


def saveFile(savePath, saveString):
    if (saveIsValid):
        plt.savefig(savePath + saveString)


def createDifferenceImage(lowEnergy, differenceFITSList, mapPositionList, mseFITSList, normalizedMseList):
    # Create images
    # pdf = PdfPages(savePath + "timeDifference/" + str(lowEnergy) + "/AllDifferences.pdf")
    for differenceFITS, mapPosition, mseFITS, normMSE in zip(differenceFITSList, mapPositionList, mseFITSList, normalizedMseList):
        # line_up, = plt.plot(mseFITS, label='mseFITS')
        # line_down, = plt.plot(normMSE, label='normMSE')
        # line_bla, = plt.plot()

        plt.imshow(differenceFITS)
        # plt.imshow(differenceFITS, cmap=plt.get_cmap("Greys"), vmin=np.amin(differenceFITSList),
        #            vmax=np.amax(differenceFITSList))
        # fig = plt.figure()
        saveFile(savePath, "timeDifference/" + str(lowEnergy) + "/" + str(mapPosition) + ".png")
        # pdf.savefig(fig)
        plt.clf()
        # pdf.close()


# Create mu-Position Chart of every Energy
def create2DChart(lowEnergy, mapPositionList, normalizedMseList):
    plt.plot(mapPositionList, normalizedMseList, label="Energy: " + str(lowEnergy))
    plt.grid()
    plt.xlabel('Zeit')
    plt.ylabel(r'MSE')
    plt.title(r'MSE-Position Chart: TimeDifference')
    plt.legend()
    saveFile(savePath, "timeDifference/" + str(lowEnergy) + "/muPosition_Chart_TimeDifference.png")
    # plt.show()
    plt.clf()


def calculateMSE(differenceFITS):
    return (differenceFITS ** 2).mean(axis=None)


def calculateNormalizedMSE(path, fileNameList, index, mseFits):
    currentFITS = fits.getdata(path + fileNameList[index])
    nextFITS = fits.getdata(path + fileNameList[index + 1])

    normalizedMSE = (((nextFITS + currentFITS) / 2) ** 2).mean(axis=None)
    return mseFits / normalizedMSE


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

def sortOdTimeByEnergy(odTime):
    filteredEnergyMap = {}
    for startTime, filenameList in odTime.iteritems():
        for fileName in filenameList:
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

    mseFITSList = []
    normalizedMseList = []
    mapPositionList = []
    differenceFITSList = []
    for lowEnergy, fileNameList in odEnergy.items():
        print "=================================================================="
        print "LowEnergy: " + str(lowEnergy) + ", proceeding..."

        for index in range(len(fileNameList)):
            if not os.path.exists(savePath + "timeDifference/" + str(lowEnergy)):
                os.makedirs(savePath + "timeDifference/" + str(lowEnergy))

            if (index + 1) < len(fileNameList):
                startTime = fits.getval(path + fileNameList[index], "DATE_OBS")
                mapPosition = odTime.keys().index(startTime)
                mapPositionList.append(mapPosition)

                differenceFITS = getDifferenceFITS(path, fileNameList, index)
                differenceFITSList.append(differenceFITS)
                mseFits = calculateMSE(differenceFITS)
                mseFITSList.append(mseFits)
                normalizedMseList.append(calculateNormalizedMSE(path, fileNameList, index, mseFits))
                # scaledFits = sci.bytescale(differenceFITS)

        createDifferenceImage(lowEnergy, differenceFITSList, mapPositionList, mseFITSList, normalizedMseList)
        create2DChart(lowEnergy, mapPositionList, normalizedMseList)
        mapPositionList = []
        normalizedMseList = []
        differenceFITSList = []
        print "LowEnergy: " + str(lowEnergy) + ", finished."
        print "==================================================================\n"


# Creating images by energy differences of every FITS File
def createImageEnergyDifference(odTime):
    print "#=========================================================#"
    print "# Creating images for energy differences..."
    print "#=========================================================#"

    sigmaList = []
    timePositionList = []
    energyPositionList = []
    for time, value in odTime.iteritems():
        energyPosition = 0
        print "=================================================================="
        print "Time: " + str(time) + ", proceeding..."
        for index in range(len(value)):
            date = time.replace(":", "-").replace(".", "-")
            if not os.path.exists(savePath + "energyDifference/" + date):
                os.makedirs(savePath + "energyDifference/" + date)

            if (index + 1) < len(value):
                energyPosition += 1
                differenceFITS = getDifferenceFITS(path, value, index)
                mapPosition = odTime.keys().index(time)
                sigmaFits = np.std(differenceFITS)

                if not mapPosition in timePositionList:
                    timePositionList.append(mapPosition)
                sigmaList.append(sigmaFits)
                energyPositionList.append(energyPosition)

                plt.imshow(differenceFITS)
                saveFile(savePath, "energyDifference/" + date + "/" + str(energyPosition) + ".png")
                plt.clf()

            else:
                #
                # Abfrage voruebergehend!
                #
                if timePositionList and sigmaList and energyPositionList:
                    fig = plt.figure()
                    ax = fig.gca(projection='3d')
                    X = timePositionList
                    Y = energyPositionList
                    X, Y = np.meshgrid(X, Y)
                    R = np.sqrt(X ** 2 + Y ** 2)
                    Z = sigmaList
                    surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm)

                    print "sigmaList: " + str(sigmaList)
                    print "timePositionList: " + str(timePositionList)
                    print "energyPositionList: " + str(energyPositionList)

                    # plt.show()
                    saveFile(savePath, "energyDifference/" + date + "/3D_Chart.png")
                    plt.clf()
                    fig.clf()

                sigmaList = []
                timePositionList = []
                energyPositionList = []

                print "Time: " + str(time) + ", finished."
                print "==================================================================\n"


# if __name__ == '__main__':
#     main()
