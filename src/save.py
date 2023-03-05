import csv
import numpy as np
from properties import Property as prop

def save_csv(data_arr, path):
    dim = data_arr.ndim
    size = len(data_arr)
    if dim == 1:
        new_data_arr = np.zeros([size,1])
        new_data_arr[:,0] = data_arr
        data_arr = new_data_arr
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        for data_idx in range(size):
            data = data_arr[data_idx].tolist()
            writer.writerow(data)

def save_angle_arr(ang_arr, ds_type):
    path = prop.angle_path + ds_type + '.csv'
    save_csv(ang_arr, path)
    print(f'[INFO SAVE] User angle array of {ds_type} is saved in {path}')

def save_xy_arr(xy_arr, ds_type):
    path = prop.xy_path + ds_type + '.csv'
    save_csv(xy_arr, path)
    print(f'[INFO SAVE] User xy array of {ds_type} is saved in {path}')

def save_group_table(group_table, alg, ds_type):
    path = prop.group_path[alg] + '_' + alg + '_' + ds_type + '.csv'
    save_csv(group_table, path)
    print(f'[INFO SAVE] Group table of {ds_type} users with generating {alg} is saved in {path}')

def save_closest_user_arr(cls_usr_arr, ds_type):
    path = prop.cls_usr_path + ds_type + '.csv'
    save_csv(cls_usr_arr, path)
    print(f'[INOF SAVE] Closest user data of {ds_type} is saved in {path}')

def save_eval_arr(eval_arr, ds_type):
    path = prop.eval_path + ds_type + '.csv'
    save_csv(eval_arr, path)
    print(f'[INFO SAVE] Evaluation of each {ds_type} user group is saved in {path}')

# incomplete
def save_user_HAPS_angle(usr_ant_ang_arr, haps_shape, ds_type):
    path = prop.usr_ant_path[haps_shape] + haps_shape + '_' + ds_type + '.csv'
    save_csv(usr_ant_ang_arr, path)
    print(f'[INFO SAVE] Angles between users of {ds_type} and antenna elements of ' +
          f'{haps_shape} HAPS is saved in {path}')