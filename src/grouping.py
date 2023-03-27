from parameters import Parameter as param
import utils
import time
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
        ang_arr = self.eqpt.get_ang_all()
        az_arr = ang_arr[:,0]
        iter_arr = np.arange(self.usr_n, dtype=int)
        az_list = np.stack([iter_arr, az_arr])
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

    def print_group_info(self, start, end):
        print("[INFO GROUP] Grouping information is describe.")
        for group_idx in range(start, end+1):
            group = int(self.sorted_min_ad_list[0,group_idx])
            pair = self.min_ad_pair[group]
            usr1 = self.group_table[group, pair[0]]
            usr2 = self.group_table[group, pair[1]]
            min_ad = self.min_ad_arr[group]
            ang_dif = self.eqpt.get_ang_dif(usr1, usr2)
            print(f"[{group_idx}] group {group}: minAD={min_ad}, " + 
                  f"pair={[usr1, usr2]}, az={ang_dif[0]}, el={ang_dif[1]}")

    def print_group_info_all(self):
        start = 0
        end = self.usr_n-1
        self.print_group_info(start, end)

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
        if self.group_table.shape != group_table.shape:
            print("[INFO ERROR] Input group table has different shape.")
        else:
            self.group_table[:,:] = group_table[:,:]
    
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
        self.sorted_az_list = np.zeros([2, self.usr_n])
        self.last_idx_arr = np.zeros(self.group_n,dtype=int)-1
        self.g_head = 0
        self.u_head = 0
    
    def update_head(self, m):
        self.g_head = (self.g_head+m) % self.group_n
        self.u_head += m
    
    def calc_mrange_ad(self, group_idx, usr_idx):
        group = (self.g_head+group_idx) % self.group_n
        usr = int(self.sorted_az_list[0,self.u_head+usr_idx])
        g_usr_idx = self.last_idx_arr[group]
        g_usr = self.group_table[group, g_usr_idx]
        ad = self.calc_ad(usr, g_usr)
        return ad
    
    def get_optimal_matching(self, m):
        best_arr = np.zeros(m, dtype=int)
        min_ad = 0
        ptn_list = itertools.permutations(np.arange(m, dtype=int))
        for ptn in ptn_list:
            ptn_ad = 360
            for g_idx in range(len(ptn)):
                usr_idx = ptn[g_idx]
                ad = self.calc_mrange_ad(g_idx, usr_idx)
                if ptn_ad > ad:
                    ptn_ad = ad
            if min_ad < ptn_ad:
                best_arr = np.array(ptn)
                min_ad = ptn_ad
        best_arr += self.u_head
        return best_arr
    
    def print_area(self, m):
        usr_idx_arr = np.arange(m,dtype=int)
        surplus = (self.usr_n-self.group_n)%m
        for head in range(0, self.usr_n-self.group_n-surplus, m):
            usr_arr = self.sorted_az_list[0, usr_idx_arr+head].astype(int)
            usr2_arr = self.sorted_az_list[0, usr_idx_arr+head+self.group_n].astype(int)
            el_arr = self.eqpt.get_angs(usr_arr)[:,1]
            el2_arr = self.eqpt.get_angs(usr2_arr)[:,1]
            el_arr_int = ((el_arr+90)/5).astype(int)
            el2_arr_int = ((el2_arr+90)/5).astype(int)
            print(head, el_arr_int, el2_arr_int)
    
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
            usr = self.sorted_az_list[0,best_arr[idx]]
            group = group_arr[idx]
            last_idx = self.last_idx_arr[group]
            self.group_table[group, last_idx+1] = usr
            self.last_idx_arr[group] += 1
    
    def execute_MRangeAUS(self):
        self.set_sorted_az_list()
        self.init_group_table()
        print("[INFO MRUS] MRUS algorithm has been executed.")
        print("            Now calculating  [", end="")
        load_period = int(self.usr_n/self.M/10)
        load_ratio = load_period
        while self.u_head < self.usr_n:
            if self.u_head > load_ratio:
                print("=", end="")
                load_ratio += load_period
            m = min(self.usr_n-self.u_head, self.M)
            best_arr = self.get_optimal_matching(m)
            self.set_usrs_to_group_table(best_arr)
            self.update_head(m)
        print(">] 100 %")
    
    def print_group_info(self, start, end):
        self.set_min_ad_all()
        self.set_sorted_min_ad_list()
        super().print_group_info(start, end)
    
    def print_group_info_all(self):
        self.set_min_ad_all()
        self.set_sorted_min_ad_list()
        super().print_group_info_all()

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


class AzimuthAUS(Grouping):
    def __init__(self, eqpt: AUSEquipment):
        super().__init__(eqpt)
        self.azimuth = AzimuthUS(eqpt)
        self.aus = None
    
    def set_azimuth_US(self):
        self.azimuth.execute()
    
    def execute(self):
        self.set_azimuth_US()
        group_table = self.azimuth.get_group_table()
        self.aus = AUS(self.eqpt, group_table)
        self.aus.set_min_ad_all()
        self.aus.set_sorted_min_ad_list()
        self.aus.execute_AUS()
        self.group_table = self.aus.get_group_table()
            
    def get_group_table(self):
        return self.group_table

class SerialSlideAUS(Grouping):
    def __init__(self, eqpt: AUSEquipment, th):
        super().__init__(eqpt)
        self.th_ad_list = th
        self.under_th_group = [i for i in range(self.group_n)]
    
    def init_group_table(self):
        self.set_sorted_az_list()
        group_idx = 0
        set_idx = 0
        for usr_idx in range(self.usr_n):
            usr = self.sorted_az_list[0,usr_idx]
            self.group_table[group_idx, set_idx] = usr
            group_idx += 1
            if group_idx >= self.group_n:
                group_idx -= self.group_n
                set_idx += 1
    
    def update_under_threshold_group(self):
        new_list = []
        low = self.th_ad_list[0]
        high = self.th_ad_list[1]
        for group in self.under_th_group:
            min_ad, pair = self.calc_min_ad(group)
            self.set_min_ad(group, min_ad, pair)
            if min_ad < low or high < min_ad:
                new_list.append(group)
        self.under_th_group = new_list
        
    def slide_users(self, pair_idx):
        group1 = self.under_th_group[0]
        usr1_idx = self.min_ad_pair[group1, pair_idx]
        usr1 = self.group_table[group1, usr1_idx]
        for grp_idx in range(len(self.under_th_group)-1):
            group2 = self.under_th_group[grp_idx+1]
            usr2_idx = self.min_ad_pair[group2, pair_idx]
            usr2 = self.group_table[group2, usr2_idx]
            self.group_table[group2, usr2_idx] = usr1
            usr1 = usr2
        group2 = self.under_th_group[0]
        usr2_idx = self.min_ad_pair[group2, pair_idx]
        self.group_table[group2, usr2_idx] = usr1
    
    def execute(self):
        self.init_group_table()
        cnt = 0
        under_th_n = self.group_n
        while True:
            print(under_th_n)
            self.update_under_threshold_group()
            if under_th_n == len(self.under_th_group):
                print('no change')
                cnt += 1
            elif under_th_n == 0:
                print('finish')
                break
            else:
                cnt = 0
            if cnt > 200:
                print('over 1000')
                break
            pair_idx = np.random.randint(0,2)
            self.slide_users(pair_idx)
            under_th_n = len(self.under_th_group)
            
            

class SerialAUS(Grouping):
    def __init__(self, eqpt: AUSEquipment):
        super().__init__(eqpt)
        self.th_el = param.threshold_elevation
        self.area_n = param.area_n
        self.max_area_dis = param.area_distance
        self.rst_queues = [[[] for i in range(self.area_n)] for j in range(self.usrs_per_group)]
        self.usr_list = [[] for i in range(self.usrs_per_group)]
        self.group_rank_arr = np.zeros([self.usrs_per_group, self.area_n],dtype=int)
        self.usr_rank_arr = np.zeros([self.usrs_per_group, self.area_n],dtype=int)

    def calc_el_dif(self, usr1, usr2):
        ang_dif = self.eqpt.get_ang_dif(usr1, usr2)
        return abs(ang_dif[1])
    
    def get_elevation_range(self):
        el_arr = self.eqpt.get_ang_all()[:,1]
        max_el = max(el_arr)
        min_el = min(el_arr)
        return (min_el, max_el)

    def input_to_usr_list(self, idx, usr, area):
        self.usr_list[idx].append([usr, area])
    
    def remove_from_usr_list(self, idx, list_idx):
        self.usr_list[idx][list_idx] = [-1,-1]

    def init_group_table(self):
        self.set_sorted_az_list()
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
        el = self.calc_el_dif(usr1, usr2)
        is_under = True if el < self.th_el else False
        return is_under
    
    def get_area(self, usr):
        el_range = self.get_elevation_range()
        unit = (el_range[1] - el_range[0]) / self.area_n
        lim = el_range[0] + unit
        el = self.eqpt.get_angs(usr)[1]
        area_idx = 0
        while el > lim:
            area_idx += 1
            lim += unit
        return area_idx

    def remove_usr(self, group, idx):
        if idx == 0:
            return 
        last = idx-1
        is_under = self.is_under_threshold(group, last, idx)
        if not is_under:
            return
        usr = self.group_table[group, idx]
        usr_area = self.get_area(usr)
        self.input_to_usr_list(idx, usr, usr_area)
        usr_iter = len(self.usr_list[idx])
        last_usr = self.group_table[group, last]
        last_usr_area = self.get_area(last_usr)
        self.rst_queues[idx][last_usr_area].append([group, usr_iter])

    def remove_usrs(self, idx):
        for group in range(self.group_n):
            self.remove_usr(group, idx)
    
    def seek_target_usr(self, idx, usr_idx, group_area, distance):
        target_idx = usr_idx
        dif = 1
        head = 0
        tail = len(self.usr_list[idx])-1
        flg = False
        while True:
            target_idx += dif
            dif = -1*(abs(dif)+1)*np.sign(dif)
            if (target_idx < head) or (tail < target_idx):
                if flg:
                    return None
                flg = True
                continue
            flg = False
            area = self.usr_list[idx][target_idx][1]
            if area == -1:
                continue
            if abs(area-group_area) > distance:
                return target_idx
    
    def seek_worst_usr(self, idx, usr_idx, group_area):
        target_idx = -1
        head = 0
        tail = len(self.usr_list[idx])
        for usr_idx in range(head, tail):
            usr_area = self.usr_list[idx][target_idx][1]
            if usr_area == group_area:
                target_idx = usr_idx
        if target_idx == -1:
            raise ValueError('could not be found the target in seek_worst_usr')
        return target_idx
    
    def redistribute_usrs_with_input_distance(self, idx, distance):
        dec_arr = np.zeros([self.area_n, self.area_n],dtype=int)
        target_arr = np.zeros(self.area_n, dtype=int)
        # set arr and list
        for i in range(len(dec_arr)):
            for j in range(len(dec_arr[i])):
                if abs(i-j) > distance:
                    dec_arr[i,j] -= 1
                    target_arr[i] += self.usr_rank_arr[idx, j]
        while True:
            min_area = -1
            min_dif = self.usr_n
            for area in range(len(self.group_rank_arr[idx])):
                if self.group_rank_arr[idx,area] == 0:
                    continue
                dif = target_arr[area] - self.group_rank_arr[idx,area]
                if dif < min_dif:
                    min_area = area
                    min_dif = dif
            if min_dif < 0:
                return False
            elif min_dif == self.usr_n:
                return True
            group, usr_idx = self.rst_queues[idx][min_area].pop(0)
            target_idx = self.seek_target_usr(idx, usr_idx, min_area, distance)
            if target_idx is None:
                raise ValueError()
            target_usr, usr_area = self.usr_list[idx][target_idx]
            self.group_table[group, idx] = target_usr
            self.remove_from_usr_list(idx, target_idx)
            self.usr_rank_arr[idx, usr_area] -= 1
            target_arr += dec_arr[usr_area]
            self.group_rank_arr[idx, min_area] -= 1
    
    def redistribute_worst_usr(self, idx):
        target_arr = np.zeros(self.area_n,dtype=int)
        for i in range(self.area_n):
            for j in range(self.area_n):
                if abs(i-j) != 0:
                    target_arr[i] += self.usr_rank_arr[idx, j]
        min_dif = self.usr_n
        min_area = -1
        for area in range(self.area_n):
            dif = target_arr[area] - self.group_rank_arr[idx, area]
            if dif < min_dif:
                min_dif = dif
                min_area = area
        if min_dif != -1:
            raise ValueError('It is not the worst situation.')
        group, usr_idx = self.rst_queues[idx][min_area].pop(0)
        target_idx = self.seek_worst_usr(idx, usr_idx)
        target_usr, usr_area = self.usr_list[idx][target_idx]
        self.group_table[group, idx] = target_usr
        self.remove_from_usr_list(idx, target_idx)
        self.usr_rank_arr[idx, usr_area] -= 1
        self.group_rank_arr[idx, min_area] -= 1
            
    def redistribute_usrs(self, idx):
        for area in range(self.area_n):
            group_n = len(self.rst_queues[idx][area])
            self.group_rank_arr[idx, area] += group_n
        for usr_idx in range(len(self.usr_list[idx])):
            usr_area = self.usr_list[idx][usr_idx][1]
            self.usr_rank_arr[idx, usr_area] += 1
        while True:
            max_dis = self.max_area_dis
            for dis in range(max_dis, -1, -1):
                is_complete = self.redistribute_usrs_with_input_distance(idx, dis)
                if is_complete:
                    break
            if is_complete:
                break
            else:
                self.redistribute_worst_usr(idx)
    
    def execute(self):
        for idx in range(1, self.usrs_per_group):
            self.remove_usrs(idx)
            self.redistribute_usrs(idx)
    
    
        
            

