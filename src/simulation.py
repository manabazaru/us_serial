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

def test_hist():
    for city in prop.cities:
        ang_arr = load.load_angle(city)
        fig.hist_usr_angles(ang_arr, city)


    
    