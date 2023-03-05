import matplotlib.pyplot as plt
import utils
from fig_properties import FigProperty as fp
from properties import Property as prop

def plt_all_users(xy_arr):
    fig = plt.figure()
    plt.scatter(xy_arr[:,0], xy_arr[:,1])
    plt.show()

def hist_usr_angle(ang_arr, ds_type, ang_type):
    fig = plt.figure(figsize=fp.hist_size)
    plt.ylim(fp.ang_ylim[ds_type])
    if ang_type == 0:
        plt.xlim(fp.az_xlim)
        plt.xlabel('azimuth [°]', fontsize=30)
        figname = 'azimuth'
    else:
        plt.xlim(fp.el_xlim)
        plt.xlabel('elevation [°]', fontsize=30)
        figname = 'elevation'
    plt.ylabel('user num', fontsize=30)
    plt.grid(True)
    plt.tick_params(labelsize=12)
    plt.hist(ang_arr, alpha=0.5, color='b')
    plt.show()
    path = prop.fig_path + 'hist_' + ds_type + '_' + figname + '.png'

def hist_usr_angles(ang_arr, ds_type):
    data = utils.turn_el(ang_arr)
    for i in range(2):
        hist_usr_angle(data[:,i], ds_type, i)
