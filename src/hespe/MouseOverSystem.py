'''
Created on 07.09.2016

@author: Kushtrim Sylejmani
'''

# Source: http://stackoverflow.com/questions/11537374/matplotlib-basemap-popup-box/11556140#11556140
import matplotlib.pyplot as plt


class MouseOverSystem():
    def __init__(self, fig, ax):
        self.__fig = fig
        self.__ax = ax
        self.__points_with_annotation = []

    def add_rectangle(self, rect):
        self.__points_with_annotation.append(rect)

    def do_mouse_over_system(self, x_list, y_list, start_time_list, end_time_list, map_name):
        for i, (x, y) in enumerate(zip(x_list, y_list)):
            point, = plt.plot(x, y, 'o', markersize=5)

            if (map_name == "Original"):
                current_start_time = "start_time: " + start_time_list[i] + "\nend_time: " + end_time_list[i]
            else:
                current_start_time = "start_time: " + start_time_list[i] + "\nend_time: " + end_time_list[i] + ",\n\n"
                current_start_time += "start_time: " + start_time_list[i + 1] + "\nend_time: " + end_time_list[i + 1]

            annotation = self.__ax.annotate("%s image: %s.png,\n%s" % (map_name, x, current_start_time),
                                            xy=(x, y), xycoords='data',
                                            xytext=(x + 0.5, y), textcoords='data',
                                            horizontalalignment="left",
                                            bbox=dict(boxstyle="round", facecolor="w",
                                                      edgecolor="0.5", alpha=0.9)
                                            )
            # by default, disable the annotation visibility
            annotation.set_visible(False)

            self.__points_with_annotation.append([point, annotation])

        on_move_id = self.__fig.canvas.mpl_connect('motion_notify_event', self.__on_move)
        plt.show()

    def __on_move(self, event):
        visibility_changed = False
        for point, annotation in self.__points_with_annotation:
            should_be_visible = (point.contains(event)[0] == True)

            if should_be_visible != annotation.get_visible():
                visibility_changed = True
                annotation.set_visible(should_be_visible)

        if visibility_changed:
            plt.draw()
