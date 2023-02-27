import numpy as np
import load
from parameters import Parameter as param
import tqdm

class AngleDif():
    def __init__(self, ang_arr, *args):
        # Removed user array to adjust number of users for grouping.
        self.rm_usr_arr = self.get_removed_user_arr(ang_arr)
        # Angle array without removed users.
        self.ang_arr = self.get_cut_usr_arr(ang_arr)
        self.usr_n = len(self.ang_arr)
        # closest user information
        self.cls_usr_arr = np.zeros(self.usr_n)
        self.cls_usr_ad = np.zeros(self.usr_n)
        self.cls_ang_dif_arr = np.zeros([self.usr_n,2])
        # User information for saving (before removing users).
        self.ang_arr_prev = ang_arr
        self.cls_usr_arr_prev = np.zeros(len(ang_arr))
        self.set_closest_user_prev(args)
        # Set all variable
        self.set_all()
    
    def get_removed_user_arr(self, ang_arr):
        usrs_per_group = param.users_per_group
        usr_n = len(ang_arr)
        rm_usr_n = usr_n % usrs_per_group
        if rm_usr_n == 0:
            return np.array([])
        group_size = int(usr_n/usrs_per_group)
        rm_usr_arr = np.array([i for i in range(0,usr_n,group_size)])
        return rm_usr_arr
    
    def get_cut_usr_arr(self, ang_arr):
        new_ang_arr = np.delete(ang_arr, self.rm_usr_arr, 0)
        return new_ang_arr
    
    def set_closest_user_prev(self, args):
        if len(args) == 0 or args[0] is None:
            pass
        else:
            self.cls_usr_arr_prev = args[0]

    def set_all(self):
        pass