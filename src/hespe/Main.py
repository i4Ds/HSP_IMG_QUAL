'''
Created on 11.08.2016

@author: Kushtrim Sylejmani
'''

import os
import collections
import re
import matplotlib

# important: install pillow package, otherwise import of 'scipy.misc' won't work!
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
__save_is_valid = True


# Main class

def main():
    filtered_list = filter_fits_file()
    od_time = sort_filtered_list_by_time(filtered_list)
    od_energy = sort_od_time_by_energy(od_time)
    original_map_values, diff_map_values = create_time_fits_value_maps(od_energy, od_time)

    # plot_time_difference(map_time_fits_values)
    # plot_energy_difference(od_time)

    plot_heat_image(original_map_values, "Normal_Standard_deviation_heatmap", "std_fits_list")
    plot_heat_image(original_map_values, "Normal_Mean_heatmap", "mean_fits_list")

    plot_heat_image(diff_map_values, "Diff_Standard_deviation_heatmap", "std_fits_list")
    plot_heat_image(diff_map_values, "Diff_Mean_heatmap", "mean_fits_list")

    if not __save_is_valid:
        print "Speicherfunktion wurde deaktiviert!"


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


# Code for printing values of a list

def print_list(list):
    for value in list:
        print "Value: " + str(value)


# Filter coarse by 'bpmap_photon.fits'

def filter_fits_file():
    temporary_list = []
    for filename in os.listdir(__path):
        if filename.endswith("bpmap_photon.fits"):
            temporary_list.append(filename)

    return temporary_list


# Sorting filteredList by time
# key = start time
# value = filename(s)

def sort_filtered_list_by_time(filtered_list):
    flare_map_time = {}
    for current_file in filtered_list:
        start_time = fits.getval(__path + current_file, "DATE_OBS")
        if start_time in flare_map_time:
            flare_map_time[start_time].append(current_file)
            flare_map_time[start_time].sort(key=natural_keys)
        else:
            flare_map_time[start_time] = [current_file]

    # Sort map by key
    return order_dict(flare_map_time)


def order_dict(map):
    return collections.OrderedDict(sorted(map.items()))


# Sorting odTime by low_energy
# key = low_energy
# value = filename(s)

def sort_od_time_by_energy(od_time):
    filtered_energy_map = {}
    for start_time, filename_list in od_time.iteritems():
        for filename in filename_list:
            low_energy = int(filename.split("_")[0].split(".")[0])
            if low_energy in filtered_energy_map:
                filtered_energy_map[low_energy].append(filename)
            else:
                filtered_energy_map[low_energy] = [filename]

    # Sort map by key
    return order_dict(filtered_energy_map)


def get_diff_fits(path, file_name_list, index):
    current_fits = fits.getdata(path + file_name_list[index])
    next_fits = fits.getdata(path + file_name_list[index + 1])
    diff_fits = next_fits - current_fits
    return diff_fits


def define_heat_map_values():
    # Source: http://stackoverflow.com/questions/15235630/matplotlib-pick-up-one-color-associated-to-one-value-in-a-colorbar?answertab=active#tab-top
    min_val = 0
    max_val = 255
    norm = matplotlib.colors.Normalize(min_val, max_val)  # the color maps work for [0, 1]

    my_cmap = cm.get_cmap('jet')  # or any other one

    # set the limits
    plt.xlim([0, 80])
    plt.ylim([0, 50])

    cmmapable = cm.ScalarMappable(norm, my_cmap)
    cmmapable.set_array(range(min_val, max_val))
    colorbar(cmmapable)
    return my_cmap, norm


def plot_heat_image(map_time_fits_values, title, list_name):
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')

    my_cmap, norm = define_heat_map_values()

    for low_energy, values in map_time_fits_values.iteritems():
        high_energy, difference_fits_list, map_position_list, std_fits_list, mean_fits_list = values

        # Plot rectangle
        for current_fits, map_position in zip(locals()[list_name], map_position_list):
            color_i = my_cmap(norm(current_fits))  # returns an rgba value
            rect = patches.Rectangle((map_position, low_energy), 1, high_energy - low_energy, edgecolor=None,
                                     color=color_i)  # make your rectangle
            ax.add_patch(rect)

    plt.title(title)
    save_file(__save_path, title + ".png")
    plt.clf()


def create_energy_diff_image(diff_fits_list, date_list, energy_position_list):
    for diff_fits, date, energy_position in zip(diff_fits_list, date_list, energy_position_list):
        plt.imshow(diff_fits)
        save_file(__save_path, "energyDifference/" + date + "/" + str(energy_position) + ".png")
        plt.clf()


# map: original_map_values
# key = low_energy
# values = high_energy, original_fits_list, original_map_position_list, original_std_fits_list, original_mean_fits_list
#
# map: diff_map_values
# key = low_energy
# values = high_energy, diff_fits_list, diff_map_position_list, diff_std_fits_list, diff_mean_fits_list

def create_time_fits_value_maps(od_energy, od_time):
    original_map_values = {}
    diff_map_values = {}

    for low_energy, file_name_list in od_energy.items():
        original_fits_list = []
        original_map_position_list = []
        original_std_fits_list = []
        original_mean_fits_list = []

        diff_fits_list = []
        diff_map_position_list = []
        diff_std_fits_list = []
        diff_mean_fits_list = []

        for index in range(len(file_name_list)):
            if not os.path.exists(__save_path + "timeDifference/" + str(low_energy)):
                os.makedirs(__save_path + "timeDifference/" + str(low_energy))

            start_time = fits.getval(__path + file_name_list[index], "DATE_OBS")
            map_position = od_time.keys().index(start_time)
            original_map_position_list.append(map_position)

            current_fits = fits.getdata(__path + file_name_list[index])
            original_fits_list.append(current_fits)

            bscale_fits = sci.bytescale(current_fits, cmin=0, cmax=255)
            original_std_fits_list.append(np.std(bscale_fits))
            original_mean_fits_list.append(np.mean(bscale_fits))

            if (index + 1) < len(file_name_list):

                diff_map_position_list.append(map_position)
                diff_fits = get_diff_fits(__path, file_name_list, index)
                diff_fits_list.append(diff_fits)

                bscale_fits = sci.bytescale(diff_fits, cmin=0, cmax=255)
                diff_std_fits_list.append(np.std(bscale_fits))
                diff_mean_fits_list.append(np.mean(bscale_fits))

            high_energy = fits.getval(__path + file_name_list[index], "ENERGY_H")

        original_map_values[low_energy] = [high_energy, original_fits_list, original_map_position_list,
                                           original_std_fits_list,
                                           original_mean_fits_list]

        diff_map_values[low_energy] = [high_energy, diff_fits_list, diff_map_position_list,
                                       diff_std_fits_list,
                                       diff_mean_fits_list]

    return order_dict(original_map_values), order_dict(diff_map_values)


def plot_time_difference(map_time_fits_values):
    for low_energy, values in map_time_fits_values.iteritems():
        print "low_energy: " + str(low_energy)
        high_energy, difference_fits_list, map_position_list, std_fits_list, mean_fits_list = values

        print "#=========================================================#"
        print "# Creating images for time differences..."
        print "#=========================================================#"

        print "=================================================================="
        print "LowEnergy: " + str(low_energy) + ", proceeding..."

        # difference plot

        for difference_fits, map_position in zip(difference_fits_list, map_position_list):
            plt.imshow(difference_fits)
            save_file(__save_path, "timeDifference/" + str(low_energy) + "/" + str(map_position) + ".png")
            plt.clf()
        plt.close()

        print "LowEnergy: " + str(low_energy) + ", finished."
        print "==================================================================\n"


def plot_energy_difference(od_time):
    print "#=========================================================#"
    print "# Creating images for energy differences..."
    print "#=========================================================#"

    for time, file_name_list in od_time.iteritems():
        diff_fits_list = []
        date_list = []
        energy_position_list = []
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

                diff_fits = get_diff_fits(__path, file_name_list, index)
                diff_fits_list.append(diff_fits)

        create_energy_diff_image(diff_fits_list, date_list, energy_position_list)

        print "Time: " + str(time) + ", finished."
        print "==================================================================\n"


if __name__ == '__main__':
    main()
