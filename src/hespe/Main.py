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
from matplotlib import colors
from matplotlib.colors import rgb2hex
import matplotlib.patches as patches

from astropy.io import fits
from MouseOverSystem import MouseOverSystem

# bokeh library
from bokeh.plotting import figure as bokeh_figure
from bokeh.plotting import gridplot as bokeh_gridplot
from bokeh.plotting import output_file as bokeh_output_file
from bokeh.plotting import show as bokeh_show
from bokeh.models import FixedTicker
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LogColorMapper,
)
from bokeh.models.tools import Inspection

# global variable

# Erster
__path = 'files/hsp_6120421_26454/coarse/'
__save_path = "files/generatedImages/6120421/"

# Zweiter
# __path = 'files/hsp_2031207_4934/coarse/'
# __save_path = "files/generatedImages/2031207/"

# Dritter
# __path = 'files/hsp_6120416_26448/coarse/'
# __save_path = "files/generatedImages/6120416/"

__save_is_valid = False
__do_mouse_over_system = False


# Main class

def main():
    filtered_list = __filter_fits_file()
    od_time = __sort_filtered_list_by_time(filtered_list)
    od_energy = __sort_od_time_by_energy(od_time)
    original_map_values, diff_map_values = __create_time_fits_value_maps(od_energy, od_time)

    # __plot_time_difference(original_map_values)
    # __plot_energy_difference(od_time)

    __plot_heat_image(original_map_values, "Original", "Original_Standard_deviation_heatmap", "std_fits_list")
    # __plot_heat_image(original_map_values, "Original", "Original_Mean_heatmap", "mean_fits_list")

    __plot_heat_image(diff_map_values, "Diff", "Diff_Standard_deviation_heatmap", "std_fits_list")
    # __plot_heat_image(diff_map_values, "Diff", "Diff_Mean_heatmap", "mean_fits_list")

    # __create_2D_chart(original_map_values, "Original")
    # __create_2D_chart(diff_map_values, "Diff")

    if not __save_is_valid:
        print "Speicherfunktion wurde deaktiviert!"


def __save_file(save_path, save_string, fig=None):
    if (__save_is_valid):
        if fig is None:
            plt.savefig(save_path + save_string)
        else:
            fig.savefig(save_path + save_string)


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


# move over system

# def __onpick(event):
#     ind = event.ind
#     print 'onpick3 scatter:', ind, np.take(x, ind), np.take(y, ind)

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


def __define_heat_map_values(min_val, max_val):
    # Source: http://stackoverflow.com/questions/15235630/matplotlib-pick-up-one-color-associated-to-one-value-in-a-colorbar?answertab=active#tab-top
    norm = matplotlib.colors.Normalize(min_val, max_val)  # the color maps work for [0, 1]

    my_cmap = cm.get_cmap('jet')  # or any other one

    # set the limits
    plt.xlim([0, 100])
    plt.ylim([0, 50])

    cmmapable = cm.ScalarMappable(norm, my_cmap)
    cmmapable.set_array(range(min_val, max_val))
    colorbar(cmmapable)
    return my_cmap, norm


def __plot_heat_image(map, method, title, list_name):
    print "=================================================================="
    print " Plotting heat image..."
    print "=================================================================="

    # matplotlib only used for saving file!
    fig = plt.figure()
    ax = fig.add_subplot(111)

    TOOLS = "pan,wheel_zoom,box_zoom,reset,hover,save"
    bokeh_plot = bokeh_figure(width=1400, height=1000, tools=TOOLS)

    min_val = 0
    max_val = 255

    my_cmap, norm = __define_heat_map_values(min_val=min_val, max_val=max_val)
    num_slabs = 255  # number of color steps
    jet_100 = [colors.rgb2hex(m) for m in my_cmap(np.arange(0, my_cmap.N, my_cmap.N / (num_slabs - 1)))]
    for low_energy, values in map.iteritems():
        high_energy, start_time_list, end_time_list, current_fits_list, map_position_list, std_fits_list, mean_fits_list = values

        # Plot rectangle
        # Source: http://matthiaseisen.com/pp/patterns/p0203/
        for i, (current_fits, map_position) in enumerate(zip(locals()[list_name], map_position_list)):
            color_i = my_cmap(norm(current_fits))  # returns a rgba value
            rect = patches.Rectangle(  # make your rectangle
                (map_position, low_energy),  # (x,y)
                1,  # width
                high_energy - low_energy,  # height
                edgecolor=None,
                color=color_i)

            ax.add_patch(rect)

            if method == "Original":
                source = ColumnDataSource(data=dict(
                    file=[map_position],
                    start_time=[start_time_list[i]],
                    end_time=[end_time_list[i]],
                ))
            else:
                source = ColumnDataSource(data=dict(
                    file=[map_position],
                    start_time_first=[start_time_list[i]],
                    end_time_first=[end_time_list[i]],
                    start_time_second=[start_time_list[i + 1]],
                    end_time_second=[end_time_list[i + 1]]

                ))

            bokeh_plot.rect(x=map_position + 0.5, y=low_energy + (high_energy - low_energy) / 2, width=1,
                            height=high_energy - low_energy,
                            color=rgb2hex(color_i),
                            source=source)
            # width_units="screen", height_units="screen")

    plt.title(title)

    hover = bokeh_plot.select_one(HoverTool)
    hover.point_policy = "follow_mouse"
    if method == "Original":
        hover.tooltips = [
            ("File", "@file"),
            ("Start time:", "@start_time"),
            ("End time:", "@end_time")
        ]
    else:
        hover.tooltips = [
            ("File", "@file"),
            ("Start time first:", "@start_time_first"),
            ("End time first:", "@end_time_first"),
            ("Start time second:", "@start_time_second"),
            ("End time second:", "@end_time_second")
        ]

    pcb = bokeh_figure(plot_width=80, plot_height=1000, x_range=[0, 1], y_range=[0, max_val], min_border_right=10)
    pcb.image(image=[np.linspace(min_val, max_val, 100).reshape(100, 1)], x=[0], y=[0], dw=[1], dh=[max_val - min_val],
              palette=jet_100)
    pcb.xaxis.major_label_text_color = None
    pcb.xaxis.major_tick_line_color = None
    pcb.xaxis.minor_tick_line_color = None
    pgrid = bokeh_gridplot([[bokeh_plot, pcb]])  # this places the colorbar next to the image

    bokeh_output_file(__save_path + title + ".html", title=title)

    bokeh_show(pgrid)
    __save_file(__save_path, title + ".png", fig=fig)

    plt.clf()
    plt.close()
    print "=================================================================="
    print " Plotting heat image, done!"
    print "=================================================================="


def position_of_list():
    print ""


def __create_2D_chart(map, map_name):
    print "=================================================================="
    print " Plotting 2D chart..."
    print "=================================================================="

    if not os.path.exists(__save_path + "plot2DCharts/" + map_name):
        os.makedirs(__save_path + "plot2DCharts/" + map_name)

    for low_energy, values in map.iteritems():
        high_energy, start_time_list, end_time_list, current_fits_list, map_position_list, std_fits_list, mean_fits_list = values

        fig = plt.figure()
        ax = fig.add_subplot(111)
        mos = MouseOverSystem(fig, ax)

        x = map_position_list

        y = std_fits_list
        title = map_name + "_Standard_deviation_low_energy_" + str(low_energy)
        plt.title(title)
        plt.xlim([0, 100])
        plt.plot(x, y)
        fig = plt.gcf()

        __save_file(__save_path, "plot2DCharts/" + map_name + "/" + title + ".png", fig=fig)
        if __do_mouse_over_system:
            mos.do_mouse_over_system(map_position_list, std_fits_list, start_time_list, end_time_list, map_name)
        plt.clf()
        plt.close()

        fig = plt.figure()
        ax = fig.add_subplot(111)
        mos = MouseOverSystem(fig, ax)

        y = mean_fits_list
        title = map_name + "_Mean_low_energy_" + str(low_energy)
        plt.title(title)
        plt.xlim([0, 100])
        plt.plot(x, y)
        fig = plt.gcf()

        __save_file(__save_path, "plot2DCharts/" + map_name + "/" + title + ".png", fig=fig)
        if __do_mouse_over_system:
            mos.do_mouse_over_system(map_position_list, mean_fits_list, start_time_list, end_time_list, map_name)
        plt.clf()
        plt.close()

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
        start_time_list = []
        end_time_list = []

        original_fits_list = []
        original_map_position_list = []
        original_std_fits_list = []
        original_mean_fits_list = []

        diff_fits_list = []
        diff_map_position_list = []
        diff_std_fits_list = []
        diff_mean_fits_list = []

        for index in range(len(file_name_list)):
            # if low_energy == 5:
            #     fits_file = fits.open(__path + file_name_list[index])
            #     print "fits_file[0].header:"
            #     print repr(fits_file[0].header)
            #     print "\n"
            #     print "test"

            start_time = fits.getval(__path + file_name_list[index], "DATE_OBS")
            start_time_list.append(start_time)

            end_time = fits.getval(__path + file_name_list[index], "DATE_END")
            end_time_list.append(end_time)

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

        original_map_values[low_energy] = [high_energy, start_time_list, end_time_list, original_fits_list,
                                           original_map_position_list,
                                           original_std_fits_list,
                                           original_mean_fits_list]

        diff_map_values[low_energy] = [high_energy, start_time_list, end_time_list, diff_fits_list,
                                       diff_map_position_list,
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
        high_energy, start_time_list, end_time_list, difference_fits_list, map_position_list, std_fits_list, mean_fits_list = values

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
