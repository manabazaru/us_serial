import numpy as np
import csv
import scipy.io as scio
from properties import Property as prop

"""
mat, csv(angle, xy, group, eval, angle_dif)
"""

def load_csv(path, data_name):
    try:
        with open(path, 'r') as f:
            reader = csv.reader(f)
            load_list = [row for row in reader]
    except FileNotFoundError:
        print(f'[INFO ERROR] {data_name} could not be loaded from {path}')
        return
    data_arr = np.array(load_list)
    factor_n = data_arr.shape[1]
    if factor_n == 1:
        data_arr = data_arr[:,0]
    return data_arr

def load_mat(city):
    path = prop.mat_path[city]
    loc_load = scio.loadmat(path)['all_UE']
    usr_xy = np.zeros((loc_load.shape[0],2))
    usr_xy[:,0] = loc_load[:,0]
    usr_xy[:,1] = loc_load[:,1]
    usr_xy /= 1000
    print(f'[INFO LOAD] User xy data of {city} is loaded from {path}')
    return usr_xy

def load_angle(ds_type):
    d_name = f'User angle of {ds_type}'
    path = prop.angle_path + ds_type + '.csv'
    data_arr = load_csv(path, d_name)
    return data_arr

def load_xy(ds_type):
    d_name = f'User xy of {ds_type}'
    path = prop.xy_path + ds_type + '.csv'
    data_arr = load_csv(path, d_name)
    return data_arr

def load_group_table(ds_type, alg):
    d_name = f'Group table of {ds_type} with {alg}'
    path = prop.group_path[alg] + ds_type + '.csv'
    data_arr = load_csv(path, d_name)
    return data_arr

def load_eval(ds_type):
    d_name = f'Evaluation of {ds_type}'
    path = prop.eval_path + ds_type + '.csv'
    data_arr = load_csv(path, d_name)
    return data_arr