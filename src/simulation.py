import load
import save
import utils
import rand_uni as ru
import grouping
import fig
from haps import CyrindricalHAPS as chaps
from beamforming import BeamForming, ZeroForcing
from eval import SystemEvaluator as eval
from us_equipment import AUSEquipment
from properties import Property as prop
from parameters import Parameter as param
import numpy as np

def save_city_csv(city):
    xy_arr = load.load_mat(city)
    xyz_arr = utils.xy2xyz(xy_arr, 0-param.z)
    angr_arr = utils.xyz2angr(xyz_arr)
    ang_arr = utils.angr2ang(angr_arr)
    save.save_angle_arr(ang_arr, city)
    save.save_xy_arr(xy_arr, city)

def save_cities_csv():
    for city in prop.cities:
        save_city_csv(city)

def AUS_test(city):
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr, city)
    aus = grouping.AUS(eqpt)
    aus.execute_AUS()
    aus.print_group_info()
    group_table = aus.get_group_table()
    sorted_min_ad_arr = aus.get_sorted_min_ad_list()
    usr_ang_arr = eqpt.get_ang_all()
    print(usr_ang_arr)
    haps = chaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    ev = eval(group_table, sorted_min_ad_arr, usr_ant_angr)
    cap_list = ev.get_sum_cap_arr()
    print(cap_list)
    
    