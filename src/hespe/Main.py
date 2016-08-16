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
__path = 'files/Erster_hsp_6120421_26454/coarse/'
# __path = 'files/Zweiter_hsp_2031207_4934/coarse/'
__save_path = "files/generatedImages/"
__save_is_valid = False


# Main class

def main():
    filtered_list = filter_FITS_file()
    od_time = sort_filtered_list_by_time(filtered_list)
    od_energy = sort_od_time_by_energy(od_time)
    map_time_FITS_values = create_time_FITS_values_map(od_energy, od_time)
    plot_time_difference(map_time_FITS_values)
    plot_energy_difference(od_time)


def save_file(save_path, save_string):
    if (__save_is_valid):
        plt.savefig(save_path + save_string)


# Source: http://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
# Sort items by string number value


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split('(\d+)', text)]


# Code for printing key and values of a map

def print_map(map):
    for key, value in map.iteritems():
        print str(key) + ", " + str(value)


def print_list(list):
    for value in list:
        print "Value: " + str(value)


# Filter coarse by 'bpmap_photon.fits'

def filter_FITS_file():
    temporary_list = []
    for filename in os.listdir(__path):
        if filename.endswith("bpmap_photon.fits"):
            temporary_list.append(filename)

    return temporary_list


# Sorting filteredList by time
# key = start time
# value = filename(s)


def sort_filtered_list_by_time(filteredList):
    flare_map_time = {}
    for currentfile in filteredList:
        key = fits.getval(__path + currentfile, "DATE_OBS")
        if key in flare_map_time:
            flare_map_time[key].append(currentfile)
            flare_map_time[key].sort(key=natural_keys)
        else:
            flare_map_time[key] = [currentfile]

    # Sort map by key
    return order_dict(flare_map_time)


def order_dict(map):
    return collections.OrderedDict(sorted(map.items()))


# Add filenames in filteredEnergyMap by energy

def sort_od_time_by_energy(odTime):
    filtered_energy_map = {}
    for starttime, filename_list in odTime.iteritems():
        for filename in filename_list:
            energy_l = int(filename.split("_")[0].split(".")[0])
            if energy_l in filtered_energy_map:
                filtered_energy_map[energy_l].append(filename)
            else:
                filtered_energy_map[energy_l] = [filename]

    # Sort map by key
    return order_dict(filtered_energy_map)


def get_difference_FITS(path, file_name_list, index):
    current_FITS = fits.getdata(path + file_name_list[index])
    next_FITS = fits.getdata(path + file_name_list[index + 1])
    difference_FITS = next_FITS - current_FITS
    return difference_FITS


def plot_time_difference(map_time_FITS_values):
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')
    for low_energy, values in map_time_FITS_values.iteritems():
        print "low_energy: " + str(low_energy)
        difference_FITS_list, map_position_list, std_FITS_list, mean_FITS_list = values

        # print "#=========================================================#"
        # print "# Creating images for time differences..."
        # print "#=========================================================#"
        #
        # print "=================================================================="
        # print "LowEnergy: " + str(low_energy) + ", proceeding..."
        #
        # for differenceFITS, map_position in zip(difference_FITS_list, map_position_list):
        #     plt.imshow(differenceFITS)
        #     save_file(__save_path, "timeDifference/" + str(low_energy) + "/" + str(map_position) + ".png")
        #     plt.clf()
        # plt.close()
        #
        # print "LowEnergy: " + str(low_energy) + ", finished."
        # print "==================================================================\n"



        # Source: http://stackoverflow.com/questions/15235630/matplotlib-pick-up-one-color-associated-to-one-value-in-a-colorbar?answertab=active#tab-top
        min_val = 0
        max_val = 50
        norm = matplotlib.colors.Normalize(min_val, max_val)  # the color maps work for [0, 1]

        my_cmap = cm.get_cmap('jet')  # or any other one

        # Plot rectangle
        for std_FITS, map_position in zip(std_FITS_list, map_position_list):
            color_i = my_cmap(norm(std_FITS))  # returns an rgba value
            rect = patches.Rectangle((map_position, low_energy), 2, 10, edgecolor=None,
                                     color=color_i)  # make your rectangle
            ax.add_patch(rect)

        # set the limits
        plt.xlim([0, 80])
        plt.ylim([0, 49])

    cmmapable = cm.ScalarMappable(norm, my_cmap)
    cmmapable.set_array(range(min_val, max_val))
    colorbar(cmmapable)
    plt.show()


def create_energy_difference_image(difference_FITS_list, date_list, energy_position_list):
    for difference_FITS, date, energy_position in zip(difference_FITS_list, date_list, energy_position_list):
        plt.imshow(difference_FITS)
        save_file(__save_path, "energyDifference/" + date + "/" + str(energy_position) + ".png")
        plt.clf()


def create_time_FITS_values_map(od_energy, od_time):
    map_time_FITS_values = {}
    map_position_list = []
    difference_FITS_list = []
    std_FITS_list = []
    mean_FITS_list = []
    for low_energy, file_name_list in od_energy.items():

        for index in range(len(file_name_list)):
            if not os.path.exists(__save_path + "timeDifference/" + str(low_energy)):
                os.makedirs(__save_path + "timeDifference/" + str(low_energy))

            if (index + 1) < len(file_name_list):
                start_time = fits.getval(__path + file_name_list[index], "DATE_OBS")
                map_position = od_time.keys().index(start_time)
                map_position_list.append(map_position)

                current_FITS = fits.getdata(__path + file_name_list[index])
                bscale_FITS = sci.bytescale(current_FITS)
                std_FITS_list.append(np.std(bscale_FITS))
                mean_FITS_list.append(np.mean(bscale_FITS))

                difference_FITS = get_difference_FITS(__path, file_name_list, index)
                difference_FITS_list.append(difference_FITS)

        map_time_FITS_values[low_energy] = [difference_FITS_list, map_position_list, std_FITS_list, mean_FITS_list]
        map_position_list = []
        difference_FITS_list = []

    return order_dict(map_time_FITS_values)


def plot_energy_difference(od_time):
    print "#=========================================================#"
    print "# Creating images for energy differences..."
    print "#=========================================================#"

    difference_FITS_list = []
    date_list = []
    energy_position_list = []
    for time, file_name_list in od_time.iteritems():
        energy_position = 0
        print "=================================================================="
        print "Time: " + str(time) + ", proceeding..."

        for index in range(len(file_name_list)):
            date = time.replace(":", "-").replace(".", "-")
            if not os.path.exists(__save_path + "energyDifference/" + date):
                os.makedirs(__save_path + "energyDifference/" + date)

            if (index + 1) < len(file_name_list):
                energy_position += 1
                energy_position_list.append(energy_position)

                date_list.append(date)

                difference_FITS = get_difference_FITS(__path, file_name_list, index)
                difference_FITS_list.append(difference_FITS)

        create_energy_difference_image(difference_FITS_list, date_list, energy_position_list)
        difference_FITS_list = []
        date_list = []
        energy_position_list = []
        print "Time: " + str(time) + ", finished."
        print "==================================================================\n"


if __name__ == '__main__':
    main()
