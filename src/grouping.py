from parameters import Parameter as param
import utils
import numpy as np
import itertools
from us_equipment import AUSEquipment

class Grouping():
    def __init__(self, eqpt: AUSEquipment):
        self.alg_name = ''
        self.eqpt = eqpt
        # int(3): number of each parameter
        self.usr_n = eqpt.get_usr_n()
        self.usrs_per_group = eqpt.get_users_per_group()
        self.group_n = int(self.usr_n/self.usrs_per_group)
        # ndarray(1): group table (output)
        self.group_table = np.zeros([self.group_n, self.usrs_per_group],
                                    dtype=int) - 1
        # ndarray(3): for calculate minAD of groups
        self.min_ad_arr = np.zeros(self.group_n) - 1
        self.min_ad_pair = np.zeros([self.group_n, 2],dtype=int) - 1
        self.sorted_min_ad_list = np.zeros([2, self.group_n], dtype=int) - 1
        self.sorted_az_list = np.zeros([2, self.usr_n])

    def calc_ad(self, usr1, usr2):
        ad = self.eqpt.get_ad(usr1, usr2)
        return ad
    
    def calc_min_ad(self, group):
        min_ad = 360
        pair = np.zeros(2,dtype=int)-1
        for usr1_idx in range(self.usrs_per_group):
            usr1 = self.group_table[group, usr1_idx]
            for usr2_idx in range(usr1_idx+1, self.usrs_per_group):
                usr2 = self.group_table[group, usr2_idx]
                ad = self.calc_ad(usr1, usr2)
                if ad < min_ad:
                    min_ad = ad
                    pair[0] = usr1_idx
                    pair[1] = usr2_idx
        return min_ad, pair
    
    def set_min_ad(self, group, min_ad, pair):
        self.min_ad_arr[group] = min_ad
        self.min_ad_pair[group] = pair
    
    def set_min_ad_all(self):
        self.raise_before_assignment_group_table_error()
        for group in range(self.group_n):
            min_ad, pair = self.calc_min_ad(group)
            self.set_min_ad(group, min_ad, pair)
    
    def set_sorted_min_ad_list(self):
        min_ad_list = np.stack([np.arange(self.group_n, dtype=int),
                               self.min_ad_arr])
        self.sorted_min_ad_list = min_ad_list[:,np.argsort(min_ad_list[1])]

    def set_sorted_az_list(self):
        az_arr = self.ang_arr[:,0]
        az_list = np.stack([np.arange(self.usr_n, dtype=int),
                            az_arr])
        self.sorted_az_list = az_list[:,np.argsort(az_list[1])]
    
    def get_group_table(self):
        return self.group_table
    
    def get_min_ad_arr(self):
        return self.min_ad_arr
    
    def get_sorted_min_ad_list(self):
        return self.sorted_min_ad_list
    
    def raise_before_assignment_group_table_error(self):
        if -1 in self.group_table:
            raise AttributeError('[INFO ERROR] calc_min_ad method is called '+
                                 'before initialization of group table')    

    def print_group_info(self):
        print("[INFO GROUP] Grouping information is describe.")
        for group_idx in range(self.group_n):
            group = int(self.sorted_min_ad_list[0,group_idx])
            pair = self.min_ad_pair[group]
            usr1 = self.group_table[group, pair[0]]
            usr2 = self.group_table[group, pair[1]]
            usr1_ang = self.eqpt.get_angs(usr1)
            usr2_ang = self.eqpt.get_angs(usr2)
            min_ad = self.min_ad_arr[group]
            ang_dif = self.eqpt.get_ang_dif(usr1, usr2)
            print(f"[{group_idx}] group {group}: minAD={min_ad}, " + 
                  f"pair={[usr1, usr2]}, az={ang_dif[0]}, el={ang_dif[1]}")

class AUS(Grouping):
    def __init__(self, eqpt: AUSEquipment, *args):
        super().__init__(eqpt)
        self.alg_name = 'AUS'
        # ndarray(1): AD table. row_idx < col_idx blocks are unusable.
        self.dif_table = np.zeros([self.usr_n, self.usr_n]) - 1
        self.swap_cnt = 0
        self.init_group_table(args)
    
    def swap(self, group1, group2, usr1_idx, usr2_idx):
        usr1 = self.group_table[group1, usr1_idx]
        usr2 = self.group_table[group2, usr2_idx]
        self.group_table[group1, usr1_idx] = usr2
        self.group_table[group2, usr2_idx] = usr1
    
    def try_swap(self, group1, group2):
        swapped = False
        usr1_idx = self.min_ad_pair[group1, 0]
        usr2_idx = self.min_ad_pair[group2, 0]
        min_ad_prev = min(self.min_ad_arr[group1], self.min_ad_arr[group2])
        self.swap(group1, group2, usr1_idx, usr2_idx)
        ad1, pair1 = self.calc_min_ad(group1)
        ad2, pair2 = self.calc_min_ad(group2)
        min_ad = min(ad1, ad2)
        if min_ad > min_ad_prev:
            self.set_min_ad(group1, ad1, pair1)
            self.set_min_ad(group2, ad2, pair2)
            swapped = True
            self.swap_cnt += 1
        else:
            self.swap(group1, group2, usr1_idx, usr2_idx)
        return swapped
    
    def init_group_table(self, args):
        if len(args) == 0:
            aranged_arr = np.arange(self.usr_n, dtype=int)
            np.random.shuffle(aranged_arr)
            self.group_table = aranged_arr.reshape([self.group_n,
                                                    self.usrs_per_group])
            return
        group_table = args[0]
        if self.group_table.shape != group_table:
            print("[INFO ERROR] Input group table has different shape.")
        else:
            self.group_table = group_table
    
    def execute_AUS(self):
        self.raise_before_assignment_group_table_error()
        print("[INFO GROUP] AUS grouping has been started.")
        self.set_min_ad_all()
        self.set_sorted_min_ad_list()
        swapped = False
        print("             Start swapping.")
        while True:
            group_worst = int(self.sorted_min_ad_list[0,0])
            for group_idx in range(1, self.group_n):
                group_k = int(self.sorted_min_ad_list[0, group_idx])
                swapped = self.try_swap(group_worst, group_k)
                if swapped:
                    break
            if swapped:
                self.set_sorted_min_ad_list()
                swapped = False
            else:
                break


class RUS(Grouping):
    def __init__(self, eqpt: AUSEquipment):
        super().__init__(eqpt)
        self.alg_name = 'RUS'

    def execute_RUS(self):
        aranged_arr = np.arange(self.usr_n, dtype=int)
        np.random.shuffle(aranged_arr)
        self.group_table = aranged_arr.reshape([self.group_n,
                                                self.usrs_per_group])
        self.set_min_ad_all()
        self.set_sorted_min_ad_list()


class MRangeAUS(Grouping):
    def __init__(self, eqpt: AUSEquipment):
        super().__init__(eqpt)
        self.M = param.M
        self.ang_arr = eqpt.get_ang_all()
        self.sorted_az_list = np.zeros([2, self.usr_n])
        self.last_idx_arr = np.zeros(self.group_n,dtype=int)-1
        self.g_head = 0
        self.u_head = 0
    
    def update_head(self, m):
        self.g_head = (self.g_head+m) % self.group_n
        self.u_head += m
    
    def calc_mrange_ad(self, group_idx, usr_idx):
        group = (self.g_head+group_idx) % self.group_n
        usr = self.u_head + usr_idx
        g_usr_idx = self.last_idx_arr[group]
        g_usr = self.group_table[group, g_usr_idx]
        ad = self.calc_ad(usr, g_usr)
        return ad
    
    def get_optimal_matching(self, m):
        best_arr = np.zeros(m, dtype=int)
        min_ad = 360
        ptn_list = itertools.permutations(np.arange(m, dtype=int))
        for ptn in ptn_list:
            ptn_ad = 360
            for g_idx in range(len(ptn)):
                usr_idx = ptn[g_idx]
                ad = self.calc_mrange_ad(g_idx, usr_idx)
                if ptn_ad > ad:
                    ptn_ad = ad
            if min_ad > ptn_ad:
                best_arr = np.array(ptn)
                min_ad = ptn_ad
        best_arr += self.u_head
        return best_arr
    
    def init_group_table(self):
        usr_idx = 0
        for group in range(self.group_n):
            usr = self.sorted_az_list[0,usr_idx]
            self.group_table[group, 0] = usr
            self.last_idx_arr[group] = 0
            usr_idx += 1
        self.u_head += self.group_n
    
    def set_usrs_to_group_table(self, best_arr):
        usr_n = len(best_arr)
        group_arr = np.arange(self.g_head, self.g_head+usr_n, dtype=int)
        group_arr = group_arr % self.group_n
        for idx in range(usr_n):
            usr = best_arr[idx]
            group = group_arr[idx]
            last_idx = self.last_idx_arr[group]
            self.group_table[group, last_idx] = usr
            self.last_idx_arr[group] += 1
    
    def execute_MRangeAUS(self):
        self.set_sorted_az_list()
        self.init_group_table()
        while self.u_head < self.usr_n:
            m = min(self.usr_n-self.u_head, self.M)
            best_arr = self.get_optimal_matching(m)
            self.set_usrs_to_group_table(best_arr)
            self.update_head(m)

class AzimuthUS(Grouping):
    def __init__(self, eqpt: AUSEquipment):
        super().__init__(eqpt)
    
    def set_group_table(self):
        group_idx = 0
        set_idx = 0
        for usr_idx in range(self.usr_n):
            usr = self.sorted_az_list[0,usr_idx]
            self.group_table[group_idx, set_idx] = usr
            group_idx += 1
            if group_idx >= self.group_n:
                group_idx -= self.group_n
                set_idx += 1
    
    def execute(self):
        self.set_sorted_az_list()
        self.set_group_table()

class SerialAUS(Grouping):
    def __init__(self, eqpt: AUSEquipment):
        super().__init__(eqpt)
        self.reset_usr_list = [[] for i in range(self.usrs_per_group)]
        self.reset_group_list = [[] for i in range(self.usrs_per_group)]
        self.th_el = param.threshold_elevation
        self.th_ad = param.threshold_ad
        self.is_ad = True if param.threshold == 'ad' else False
    
    def calc_el_dif(self, usr1, usr2):
        ang_dif = self.eqpt.get_ang_dif(usr1, usr2)
        return abs(ang_dif[1])
    
    def init_group_table(self):
        group_idx = 0
        set_idx = 0
        for usr_idx in range(self.usr_n):
            usr = self.sorted_az_list[0,usr_idx]
            self.group_table[group_idx, set_idx] = usr
            group_idx += 1
            if group_idx >= self.group_n:
                group_idx -= self.group_n
                set_idx += 1
    
    def is_under_threshold(self, group, usr1_idx, usr2_idx):
        usr1 = self.group_table[group, usr1_idx]
        usr2 = self.group_table[group, usr2_idx]
        if self.is_ad:
            ad = self.calc_ad(usr1, usr2)
            is_under = True if ad < self.th_ad else False
        else:
            el = self.calc_el_dif(usr1, usr2)
            is_under = True if el < self.th_el else False
        return is_under
    
    def remove_usrs(self):
        self.