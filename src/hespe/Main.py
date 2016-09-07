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
    filtered_list = __filter_fits_file()
    od_time = __sort_filtered_list_by_time(filtered_list)
    od_energy = __sort_od_time_by_energy(od_time)
    original_map_values, diff_map_values = __create_time_fits_value_maps(od_energy, od_time)

    __plot_time_difference(original_map_values)
    __plot_energy_difference(od_time)

    __plot_heat_image(original_map_values, "Normal_Standard_deviation_heatmap", "std_fits_list")
    __plot_heat_image(original_map_values, "Normal_Mean_heatmap", "mean_fits_list")

    __plot_heat_image(diff_map_values, "Diff_Standard_deviation_heatmap", "std_fits_list")
    __plot_heat_image(diff_map_values, "Diff_Mean_heatmap", "mean_fits_list")

    __plot_2D_chart(original_map_values, "Original")
    __plot_2D_chart(diff_map_values, "Diff")

    if not __save_is_valid:
        print "Speicherfunktion wurde deaktiviert!"


def __save_file(save_path, save_string):
    if (__save_is_valid):
        plt.savefig(save_path + save_string)


# Source: http://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
# Sort items by string number value


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split('(\d+)', text)]


# Code for printing key and values of a map

def __print_map(map):
    for key, value in map.iteritems():
        print str(key) + ", " + str(value)


# Code for printing values of a list

def __print_list(list):
    for value in list:
        print "Value: " + str(value)
    print "\n"


# Filter coarse by 'bpmap_photon.fits'

def __filter_fits_file():
    print "=================================================================="
    print " Filtering list..."
    print "=================================================================="
    temporary_list = []
    for filename in os.listdir(__path):
        if filename.endswith("bpmap_photon.fits"):
            temporary_list.append(filename)
    print "=================================================================="
    print " Filtering list, done!"
    print "=================================================================="

    return temporary_list


# Sorting filteredList by time
# key = start time
# value = filename(s)

def __sort_filtered_list_by_time(filtered_list):
    print "=================================================================="
    print " Sorting map by time..."
    print "=================================================================="
    od_time = {}
    for current_file in filtered_list:
        start_time = fits.getval(__path + current_file, "DATE_OBS")
        if start_time in od_time:
            od_time[start_time].append(current_file)
            od_time[start_time].sort(key=natural_keys)
        else:
            od_time[start_time] = [current_file]

    print "=================================================================="
    print " Sorting map by time, done!"
    print "=================================================================="

    # Sort map by key
    return order_dict(od_time)


def order_dict(map):
    return collections.OrderedDict(sorted(map.items()))


# Sorting odTime by low_energy
# key = low_energy
# value = filename(s)

def __sort_od_time_by_energy(od_time):
    print "=================================================================="
    print " Sorting map by energy..."
    print "=================================================================="

    od_energy = {}
    for start_time, filename_list in od_time.iteritems():
        for filename in filename_list:
            low_energy = int(filename.split("_")[0].split(".")[0])
            if low_energy in od_energy:
                od_energy[low_energy].append(filename)
            else:
                od_energy[low_energy] = [filename]
    print "=================================================================="
    print " Sorting map by energy, done!"
    print "=================================================================="

    # Sort map by key
    return order_dict(od_energy)


def __get_diff_fits(path, file_name_list, index):
    current_fits = fits.getdata(path + file_name_list[index])
    next_fits = fits.getdata(path + file_name_list[index + 1])
    diff_fits = next_fits - current_fits
    return diff_fits


def __define_heat_map_values():
    # Source: http://stackoverflow.com/questions/15235630/matplotlib-pick-up-one-color-associated-to-one-value-in-a-colorbar?answertab=active#tab-top
    min_val = 0
    max_val = 255
    norm = matplotlib.colors.Normalize(min_val, max_val)  # the color maps work for [0, 1]

    my_cmap = cm.get_cmap('jet')  # or any other one

    # set the limits
    plt.xlim([0, 100])
    plt.ylim([0, 50])

    cmmapable = cm.ScalarMappable(norm, my_cmap)
    cmmapable.set_array(range(min_val, max_val))
    colorbar(cmmapable)
    return my_cmap, norm


def __plot_heat_image(map, title, list_name):
    print "=================================================================="
    print " Plotting heat image..."
    print "=================================================================="

    fig = plt.figure()
    ax = fig.add_subplot(111)

    my_cmap, norm = __define_heat_map_values()

    for low_energy, values in map.iteritems():
        high_energy, current_fits_list, map_position_list, std_fits_list, mean_fits_list = values

        # Plot rectangle
        for current_fits, map_position in zip(locals()[list_name], map_position_list):
            color_i = my_cmap(norm(current_fits))  # returns an rgba value
            rect = patches.Rectangle((map_position, low_energy), 1, high_energy - low_energy, edgecolor=None,
                                     color=color_i)  # make your rectangle
            ax.add_patch(rect)

    plt.title(title)
    __save_file(__save_path, title + ".png")
    plt.clf()
    print "=================================================================="
    print " Plotting heat image, done!"
    print "=================================================================="


def __plot_2D_chart(map, map_name):
    print "=================================================================="
    print " Plotting 2D chart..."
    print "=================================================================="
    for low_energy, values in map.iteritems():
        high_energy, current_fits_list, map_position_list, std_fits_list, mean_fits_list = values

        if not os.path.exists(__save_path + "plotCharts/"):
            os.makedirs(__save_path + "plotCharts/")

        x = map_position_list

        y = std_fits_list
        title = map_name + "_Standard_deviation_histogram_low_energy_" + str(low_energy)
        plt.title(title)
        plt.xlim([0, 100])
        plt.plot(x, y)
        __save_file(__save_path, "plotCharts/" + title + ".png")
        plt.clf()

        y = mean_fits_list
        title = map_name + "_Mean_histogram_low_energy_" + str(low_energy)
        plt.title(title)
        plt.xlim([0, 100])
        plt.plot(x, y)
        __save_file(__save_path, "plotCharts/" + title + ".png")
        plt.clf()

    print "=================================================================="
    print " Plotting 2D chart, done!"
    print "=================================================================="


def __create_energy_diff_image(diff_fits_list, date_list, energy_position_list):
    for diff_fits, date, energy_position in zip(diff_fits_list, date_list, energy_position_list):
        plt.imshow(diff_fits)
        __save_file(__save_path, "energyDifference/" + date + "/" + str(energy_position) + ".png")
        plt.clf()


# map: original_map_values
# key = low_energy
# values = high_energy, original_fits_list, original_map_position_list, original_std_fits_list, original_mean_fits_list
#
# map: diff_map_values
# key = low_energy
# values = high_energy, diff_fits_list, diff_map_position_list, diff_std_fits_list, diff_mean_fits_list

def __create_time_fits_value_maps(od_energy, od_time):
    print "=================================================================="
    print " Creating original and diff maps..."
    print "=================================================================="

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
                diff_fits = __get_diff_fits(__path, file_name_list, index)
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
    print "=================================================================="
    print " Creating original and diff maps, done!"
    print "=================================================================="
    return order_dict(original_map_values), order_dict(diff_map_values)


def __plot_time_difference(map_time_fits_values):
    print "#================================================================#"
    print "# Creating images for time differences..."
    print "#================================================================#"

    for low_energy, values in map_time_fits_values.iteritems():
        high_energy, difference_fits_list, map_position_list, std_fits_list, mean_fits_list = values

        if not os.path.exists(__save_path + "timeDifference/" + str(low_energy)):
            os.makedirs(__save_path + "timeDifference/" + str(low_energy))

        print "=================================================================="
        print "LowEnergy: " + str(low_energy) + ", proceeding..."

        # difference plot

        for difference_fits, map_position in zip(difference_fits_list, map_position_list):
            plt.imshow(difference_fits)
            __save_file(__save_path, "timeDifference/" + str(low_energy) + "/" + str(map_position) + ".png")
            plt.clf()
        plt.close()

        print "LowEnergy: " + str(low_energy) + ", finished."
        print "==================================================================\n"


def __plot_energy_difference(od_time):
    print "#================================================================#"
    print "# Creating images for energy differences..."
    print "#================================================================#"

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

                diff_fits = __get_diff_fits(__path, file_name_list, index)
                diff_fits_list.append(diff_fits)

        __create_energy_diff_image(diff_fits_list, date_list, energy_position_list)

        print "Time: " + str(time) + ", finished."
        print "==================================================================\n"


if __name__ == '__main__':
    main()
