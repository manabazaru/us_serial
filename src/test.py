import load
import save
import utils
import rand_uni as ru
import grouping
import fig
import path
from haps import CyrindricalHAPS as chaps
from beamforming import BeamForming, ZeroForcing
from eval import SystemEvaluator as eval
from us_equipment import AUSEquipment
from properties import Property as prop
from parameters import Parameter as param
import numpy as np

path.set_cur_dir()
np.set_printoptions(threshold=np.inf)

class TestUSEquipment():
    def test_calc_ad(self, ang_arr, usr1, usr2):
        usr1_ang = ang_arr[usr1]
        usr2_ang = ang_arr[usr2]
        dif_ang = abs(usr1_ang - usr2_ang)
        if dif_ang[0] > 180:
            dif_ang[0] = 360 - dif_ang[0]
        ad = np.sqrt(sum(dif_ang**2))
        return ad
    
    def test_get_angs(self, ang_arr, usrs):
        angs = ang_arr[usrs]
        return angs

    def test(self, ds_type, usrs):
        # ds_type = {'tokyo', 'rand1', 'osaka', 'rand2'}
        print("test USEquipment")
        cls_flg = False
        if ds_type == 'tokyo':
            ang_arr = load.load_angle('tokyo')
            cls_usr_arr = load.load_closest_user('tokyo')
            cls_flg = True
        elif ds_type == 'rand1':
            xy_arr = ru.generate_random_uniform_usr_xy(1200)
            xyz_arr = utils.xy2xyz(xy_arr, -param.z)
            angr_arr = utils.xyz2angr(xyz_arr)
            ang_arr = utils.angr2ang(angr_arr)
        elif ds_type == 'osaka':
            ang_arr = load.load_angle('osaka')
            cls_usr_arr = load.load_closest_user('osaka')
            cls_flg = True
        elif ds_type == 'rand2':
            xy_arr = ru.generate_random_uniform_usr_xy(1201)
            xyz_arr = utils.xy2xyz(xy_arr, -param.z)
            angr_arr = utils.xyz2angr(xyz_arr)
            ang_arr = utils.angr2ang(angr_arr)
        if cls_flg:
            eqpt = AUSEquipment(ang_arr, cls_usr_arr)
        else:
            eqpt = AUSEquipment(ang_arr)
        # print(eqpt.usr_n, eqpt.get_usr_n(), eqpt.rm_usr_n)
        # print(eqpt.rm_usr_arr, int(eqpt.usr_n/eqpt.usrs_per_group))
        # print(eqpt.usr_orig_iter)
        # new_ang_arr = eqpt.get_ang_all()
        # fig.hist_usr_angles(new_ang_arr, ds_type)
        usr_pair = np.array([0, 1])
        orig_usr_pair = usrs
        ang1 = eqpt.get_angs(usr_pair)
        ang2 = self.test_get_angs(ang_arr, orig_usr_pair)
        ad = eqpt.calc_ad(usr_pair[0], usr_pair[1])
        ans_ad = self.test_calc_ad(ang_arr, orig_usr_pair[0], orig_usr_pair[1])
        print(ang1, ang2)
        print(ad, ans_ad)
        return eqpt

class TestAUSGrouping():
    def test(self, eqpt):
        aus = grouping.AUS(eqpt)
        aus.execute_AUS()
        return aus.get_group_table()

def test_eqpt_aus():
    testeq = TestUSEquipment()
    testaus = TestAUSGrouping()
    test_type = ['tokyo','osaka']
    orig_usr_arr = np.array([[0,1],[0,1],[1,2],[1,2]])
    for ds_type_iter in range(len(test_type)):
        ds_type = test_type[ds_type_iter]
        eqpt = testeq.test(ds_type, orig_usr_arr[ds_type_iter])
        group_table = testaus.test(eqpt)
        save.save_group_table(group_table, 'AUS', ds_type)

def get_test_eqpt(city):
    ang_arr = np.zeros([12,2])
    ang_arr[0] = np.array([0,-90])
    ang_arr[1] = np.array([0, -45])
    ang = -180
    dif = 360/10
    for i in range(2, 12):
        ang_arr[i] = np.array([ang, -45])
        ang += dif
    eqpt = AUSEquipment(ang_arr)
    return eqpt

def get_test_random_eqpt(city):
    ang_arr = np.zeros([12,2])
    ang_arr[:,0] = np.random.random_sample(12)*360-180
    ang_arr[:,1] = np.random.random_sample(12)*-45
    eqpt = AUSEquipment(ang_arr)
    return eqpt

def test_haps():
    city = 'tokyo'
    eqpt = get_test_eqpt(city)
    haps = chaps()
    usr_ant_ang_arr = haps.get_user_antenna_angle_r_arr(eqpt)
    save.save_user_HAPS_angle(usr_ant_ang_arr, 'cylindrical', city)
    print(usr_ant_ang_arr.shape)
    input()

def test_beamforming():
    eqpt = get_test_random_eqpt('tokyo')
    haps = chaps()
    usr_ant_ang_arr = haps.get_user_antenna_angle_r_arr(eqpt)
    bf = ZeroForcing(usr_ant_ang_arr)
    hw = np.dot(bf.h, bf.w)

def test_AUS():
    xy_arr = ru.generate_random_uniform_usr_xy(1200, 100)
    xyz_arr = utils.xy2xyz(xy_arr, -param.z)
    angr_arr = utils.xyz2angr(xyz_arr)
    ang_arr = utils.angr2ang(angr_arr)
    eqpt = AUSEquipment(ang_arr)
    aus = grouping.AUS(eqpt)
    aus.execute_AUS()
    aus.print_group_info()
    group_table = aus.get_group_table()
    sorted_min_ad_arr = aus.get_sorted_min_ad_list()
    haps = chaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    save.save_user_HAPS_angle(usr_ant_angr, 'cylindrical', 'random')
    ev = eval(group_table, sorted_min_ad_arr, usr_ant_angr)
    cap_list = ev.get_sum_cap_arr()
    print(cap_list)
    save.save_eval_arr(cap_list, 'random_100')

def test_RUS():
    xy_arr = ru.generate_random_uniform_usr_xy(1200, 100)
    xyz_arr = utils.xy2xyz(xy_arr, -param.z)
    angr_arr = utils.xyz2angr(xyz_arr)
    ang_arr = utils.angr2ang(angr_arr)
    eqpt = AUSEquipment(ang_arr)
    rus = grouping.RUS(eqpt)
    rus.execute_RUS()
    rus.print_group_info()
    group_table = rus.get_group_table()
    sorted_min_ad_arr = rus.get_sorted_min_ad_list()
    haps = chaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    save.save_user_HAPS_angle(usr_ant_angr, 'cylindrical', 'random')
    ev = eval(group_table, sorted_min_ad_arr, usr_ant_angr)
    cap_list = ev.get_sum_cap_arr()
    print(cap_list)
    save.save_eval_arr(cap_list, 'random_100')

def test_utils():
    ang_arr = np.array([[0,-90],[90,-45]])
    angr_arr = utils.ang2angr_with_z(ang_arr, -20)
    print(angr_arr)

test_AUS()
print(1j)