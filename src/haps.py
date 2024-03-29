import numpy as np
import tqdm
import utils
from parameters import Parameter as param
from us_equipment import AUSEquipment

class HAPS():
    def __init__(self):
        self.wv_len = param.c/param.carrier_freq
        self.altitude = param.z
    
    def rot_usr_xyz(self, xyz, yaw, pitch):
        xyz2 = utils.rotate_with_yaw(xyz, yaw)
        xyz3 = utils.rotate_with_pitch(xyz2, pitch)
        return xyz3

class PlanarHAPS(HAPS):
    def __init__(self):
        self.sd_n = param.planar_antenna_size_of_side
        self.ant_n = self.sd_n ** 2
        self.xyz_arr = np.zeros([self.sd_n, self.sd_n, 3])
        # parameter
        self.ant_dis = self.wv_len * 0.6
    
    # def set_antenna_xyz(self):


class CyrindricalHAPS(HAPS):
    def __init__(self):
        super().__init__()
        # number of each antenna element
        self.sd_h_n = param.side_horizonal_antenna
        self.sd_v_n = param.side_vertical_antenna
        self.sd_n = self.sd_h_n * self.sd_v_n
        self.btm_n = param.bottom_antenna
        self.ant_n = self.sd_n + self.btm_n
        # side antenna element
        self.sd_xyz_arr = np.zeros([self.sd_v_n, self.sd_h_n, 3])
        self.sd_vec_dir = np.zeros([self.sd_v_n, self.sd_h_n])
        # bottom antenna element
        self.btm_xyz_arr = np.zeros([self.btm_n, 3])
        self.btm_rot_yaw = np.zeros([self.btm_n])
        # length
        self.h_r = 0.6 * self.wv_len * (self.sd_h_n / (2*np.pi))
        self.b_r = 0.5 * self.h_r
        self.dv = 0.6 * self.wv_len
        self.ant_height = param.antenna_height
        self.set_all()

    def set_side_antenna_vector_direction(self):
        vec_ang_dif = 360/self.sd_h_n
        dir_arr = np.arange(self.sd_h_n)*vec_ang_dif - 180
        for v in range(self.sd_v_n):
            self.sd_vec_dir[v,:] = dir_arr[:]

    def set_bottom_rot_yaw(self):
        rot_ang_dif = 360/self.btm_n
        rot_ang_arr = np.arange(self.btm_n)*rot_ang_dif - 180
        self.btm_rot_yaw = rot_ang_arr

    def set_antenna_xyz_arr(self):
        z = (self.sd_v_n-1) * self.dv / 2
        # set side antenna
        for v in range(self.sd_v_n):
            dir_rad = np.deg2rad(self.sd_vec_dir[v])
            x = self.h_r * np.cos(dir_rad)
            y = self.h_r * np.sin(dir_rad)
            self.sd_xyz_arr[v,:,0] = x
            self.sd_xyz_arr[v,:,1] = y
            self.sd_xyz_arr[v,:,2] = z
            z -= self.dv
        # set bottom antenna
        dir_rad = np.deg2rad(self.btm_rot_yaw)
        x = self.b_r * np.cos(dir_rad)
        y = self.b_r * np.sin(dir_rad)
        self.btm_xyz_arr[:,0] = x
        self.btm_xyz_arr[:,1] = y
        self.btm_xyz_arr[:,2] = -1*self.ant_height/2
    
    def set_all(self):
        print("[INFO HAPS] Initialization of HAPS has been started.")
        self.set_side_antenna_vector_direction()
        self.set_bottom_rot_yaw()
        self.set_antenna_xyz_arr()
 
    def get_user_antenna_angle_r_arr(self, eqpt: AUSEquipment):
        print("[INFO HAPS] Calculation of user angle from each antenna "+
              "element has been started.")
        ang_arr = eqpt.get_ang_all()
        usr_n = eqpt.get_usr_n()
        usr_angr_arr = utils.ang2angr_with_z(ang_arr, -self.altitude)
        usr_xyz_arr = utils.angr2xyz(usr_angr_arr)
        usr_sd_angr = np.zeros([usr_n, self.sd_n, 3])
        usr_btm_angr = np.zeros([usr_n, self.btm_n, 3])
        usr_ant_angr = np.zeros([usr_n, self.ant_n, 3])
        flt_sd_xyz_arr = self.sd_xyz_arr.reshape(self.sd_n,3)
        flt_sd_vec_dir = self.sd_vec_dir.reshape(self.sd_n)
        for usr in tqdm.tqdm(range(usr_n)):
            usr_xyz = usr_xyz_arr[usr]
            for sd_ant in range(self.sd_n):
                sd_xyz = flt_sd_xyz_arr[sd_ant]
                shift_usr_xyz = usr_xyz - sd_xyz
                shift_usr_angr = utils.xyz2angr(shift_usr_xyz)
                shift_usr_angr[0] = utils.calc_az_dif(shift_usr_angr[0],
                                                      flt_sd_vec_dir[sd_ant])
                usr_sd_angr[usr, sd_ant] = shift_usr_angr
            for btm_ant in range(self.btm_n):
                btm_xyz = self.btm_xyz_arr[btm_ant]
                shift_usr_xyz = usr_xyz - btm_xyz
                yaw = -1*self.btm_rot_yaw[btm_ant]
                rot_xyz = self.rot_usr_xyz(shift_usr_xyz, yaw, -90)
                rot_angr = utils.xyz2angr(rot_xyz)
                usr_btm_angr[usr, btm_ant] = rot_angr
        usr_ant_angr = np.concatenate([usr_sd_angr, usr_btm_angr],1)
        return usr_ant_angr