'''
Created on 11.08.2016

@author: Kushtrim Sylejmani
'''

import os
import collections
import re
import matplotlib

# important: install pillow package, otherwise scipy.misc won't work!
import scipy.misc as sci

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pylab import colorbar
import matplotlib.cm as cm
import matplotlib.patches as patches

from astropy.io import fits

# global variable
path = 'files/Erster_hsp_6120421_26454/coarse/'
# path = 'files/Zweiter_hsp_2031207_4934/coarse/'
savePath = "files/generatedImages/"
saveIsValid = False


# Main class

def main():
    filteredList = filterFITSFile()
    odTime = sortFilteredListByTime(filteredList)
    odEnergy = sortOdTimeByEnergy(odTime)
    mapTimeFITSValues = createTimeFITSValuesMap(odEnergy, odTime)
    plotTimeDifference(mapTimeFITSValues)
    plotEnergyDifference(odTime)


def saveFile(savePath, saveString):
    if (saveIsValid):
        plt.savefig(savePath + saveString)


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
    return orderDict(flareMapTime)


def orderDict(map):
    return collections.OrderedDict(sorted(map.items()))


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
    return orderDict(filteredEnergyMap)


def getDifferenceFITS(path, fileNameList, index):
    currentFITS = fits.getdata(path + fileNameList[index])
    nextFITS = fits.getdata(path + fileNameList[index + 1])
    differenceFITS = nextFITS - currentFITS
    return differenceFITS


def plotTimeDifference(mapTimeFITSValues):
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')
    for lowEnergy, values in mapTimeFITSValues.iteritems():
        print "lowEnergy: " + lowEnergy
        differenceFITSList, mapPositionList, stdFITSList, meanFITSList = values

        # print "#=========================================================#"
        # print "# Creating images for time differences..."
        # print "#=========================================================#"
        #
        # print "=================================================================="
        # print "LowEnergy: " + str(lowEnergy) + ", proceeding..."
        #
        # for differenceFITS, mapPosition in zip(differenceFITSList, mapPositionList):
        #     plt.imshow(differenceFITS)
        #     saveFile(savePath, "timeDifference/" + str(lowEnergy) + "/" + str(mapPosition) + ".png")
        #     plt.clf()
        # plt.close()
        #
        # print "LowEnergy: " + str(lowEnergy) + ", finished."
        # print "==================================================================\n"



        # Source: http://stackoverflow.com/questions/15235630/matplotlib-pick-up-one-color-associated-to-one-value-in-a-colorbar?answertab=active#tab-top
        min_val = 0
        max_val = 50
        norm = matplotlib.colors.Normalize(min_val, max_val)  # the color maps work for [0, 1]

        my_cmap = cm.get_cmap('jet')  # or any other one

        # Plot rectangle
        for stdFITS, mapPosition in zip(stdFITSList, mapPositionList):
            color_i = my_cmap(norm(stdFITS))  # returns an rgba value
            rect = patches.Rectangle((mapPosition, lowEnergy), 2, 10, edgecolor=None,
                                     color=color_i)  # make your rectangle
            ax.add_patch(rect)

        # set the limits
        plt.xlim([0, 80])
        plt.ylim([0, 49])

    cmmapable = cm.ScalarMappable(norm, my_cmap)
    cmmapable.set_array(range(min_val, max_val))
    colorbar(cmmapable)
    plt.show()


def createEnergyDifferenceImage(differenceFITSList, dateList, energyPositionList):
    for differenceFITS, date, energyPosition in zip(differenceFITSList, dateList, energyPositionList):
        plt.imshow(differenceFITS)
        saveFile(savePath, "energyDifference/" + date + "/" + str(energyPosition) + ".png")
        plt.clf()


def createTimeFITSValuesMap(odEnergy, odTime):
    mapTimeFITSValues = {}
    mapPositionList = []
    differenceFITSList = []
    stdFITSList = []
    meanFITSList = []
    for lowEnergy, fileNameList in odEnergy.items():

        for index in range(len(fileNameList)):
            if not os.path.exists(savePath + "timeDifference/" + str(lowEnergy)):
                os.makedirs(savePath + "timeDifference/" + str(lowEnergy))

            if (index + 1) < len(fileNameList):
                startTime = fits.getval(path + fileNameList[index], "DATE_OBS")
                mapPosition = odTime.keys().index(startTime)
                mapPositionList.append(mapPosition)

                currentFITS = fits.getdata(path + fileNameList[index])
                bscaleFITS = sci.bytescale(currentFITS)
                stdFITSList.append(np.std(bscaleFITS))
                meanFITSList.append(np.mean(bscaleFITS))

                differenceFITS = getDifferenceFITS(path, fileNameList, index)
                differenceFITSList.append(differenceFITS)

        mapTimeFITSValues[lowEnergy] = [differenceFITSList, mapPositionList, stdFITSList, meanFITSList]
        mapPositionList = []
        differenceFITSList = []

    return orderDict(mapTimeFITSValues)


def plotEnergyDifference(odTime):
    print "#=========================================================#"
    print "# Creating images for energy differences..."
    print "#=========================================================#"

    differenceFITSList = []
    dateList = []
    energyPositionList = []
    for time, fileNameList in odTime.iteritems():
        energyPosition = 0
        print "=================================================================="
        print "Time: " + str(time) + ", proceeding..."

        for index in range(len(fileNameList)):
            date = time.replace(":", "-").replace(".", "-")
            if not os.path.exists(savePath + "energyDifference/" + date):
                os.makedirs(savePath + "energyDifference/" + date)

            if (index + 1) < len(fileNameList):
                energyPosition += 1
                energyPositionList.append(energyPosition)

                dateList.append(date)

                differenceFITS = getDifferenceFITS(path, fileNameList, index)
                differenceFITSList.append(differenceFITS)

        createEnergyDifferenceImage(differenceFITSList, dateList, energyPositionList)
        differenceFITSList = []
        dateList = []
        energyPositionList = []
        print "Time: " + str(time) + ", finished."
        print "==================================================================\n"


if __name__ == '__main__':
    main()
