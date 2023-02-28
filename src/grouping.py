from parameters import Parameter as param
import utils
import numpy as np
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
        self.sorted_min_ad_list = np.zeros([2, self.group_n],dtype=int) - 1
    
    def calc_ad(self, usr1, usr2):
        return self.eqpt.get_ad(usr1, usr2)
    
    def calc_min_ad(self, group):
        min_ad = 360
        pair = np.zeros(2,dtype=int)-1
        for usr1_idx in range(self.usrs_per_group):
            usr1 = self.group_table[group, usr1_idx]
            for usr2_idx in range(self.usrs_per_group):
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
        if -1 in self.group_table:
            raise AttributeError('[INFO ERROR] calc_min_ad method is called '+
                                 'before initialization of group table')
        for group in range(self.group_n):
            min_ad, pair = self.calc_min_ad(group)
            self.set_min_ad(group, min_ad, pair)
    
    def set_sorted_min_ad_list(self):
        min_ad_list = np.stack(
                               np.arange(self.group_n, dtype=int),
                               self.min_ad_arr
                              )
        self.sorted_min_ad_list = min_ad_list[:,np.argsort(min_ad_list[1])]
    
    def get_group_table(self):
        return self.group_table
    

class AUS(Grouping):
    def __init__(self, eqpt: AUSEquipment):
        super().__init__(eqpt)
        self.alg_name = 'AUS'
        # ndarray(1): AD table. row_idx < col_idx blocks are unusable.
        self.dif_table = np.zeros([self.usr_n, self.usr_n]) - 1
        