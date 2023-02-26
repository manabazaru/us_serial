import numpy as np

# args = xyz_arr, angr_arr, xyz, angr, x-y-z or az-el-r
def get_data_from_args(args):
    if len(args) == 1:
        if args[0].ndim == 1:
            d = args[0]
            d1 = d[0]
            d2 = d[1]
            d3 = d[2]
        else:
            d = args[0]
            d1 = d[:,0]
            d2 = d[:,1]
            d3 = d[:,2]
    else:
        d1 = args[0]
        d2 = args[1]
        d3 = args[2]
    return d1, d2, d3

def get_init_arr(arr):
    if arr.ndim == 1:
        new_arr = np.zeros(len(arr))
    else:
        arr_size = len(arr)
        arr_factor_n = len(arr[0])
        new_arr = np.zeros([arr_size, arr_factor_n])
        return new_arr

def get_data_in_arr(arr, d1, d2, d3):
    if arr.ndim == 1:
        arr[0] = d1
        arr[1] = d2
        arr[2] = d3
    else:
        arr[:,0] = d1
        arr[:,1] = d2
        arr[:,2] = d3
    return arr

def ints2arr(*args):
    size = len(args)
    arr = np.zeros(size)
    for arg_idx in range(size):
        arr[arg_idx] = args[arg_idx]
    return arr

def calc_x(*args):
    az, el, r = get_data_from_args(args)
    az_rad = np.deg2rad(az)
    el_rad = np.deg2rad(el)
    x = r*np.cos(el_rad) * np.cos(az_rad)
    return x

def calc_y(*args):
    az, el, r = get_data_from_args(args)
    az_rad = np.deg2rad(az)
    el_rad = np.deg2rad(el)
    y = r*np.cos(el_rad) * np.sin(az_rad)
    return y

def calc_z(*args):
    az, el, r = get_data_from_args(args)
    el_rad = np.deg2rad(el)
    z = r*np.sin(el_rad)
    return z

def calc_az(*args):
    x, y, z = get_data_from_args(args)
    az_rad = np.arctan2(y,x)
    az = np.rad2deg(az_rad)
    return az_rad

def calc_el(*args):
    x, y, z = get_data_from_args(args)
    r = np.sqrt(x**2+y**2+z**2)
    el_rad = np.arcsin(z/r)
    el = np.deg2rad(el_rad)
    return el

def calc_r(*args):
    x, y, z = get_data_from_args(args)
    r = np.sqrt(x**2+y**2+z**2)
    return r

def xyz2angr(xyz_arr):
    angr_arr = get_init_arr(xyz_arr)
    az = calc_az(xyz_arr)
    el = calc_el(xyz_arr)
    r = calc_r(xyz_arr)
    angr_arr = get_data_in_arr(angr_arr, az, el, r)
    return angr_arr

def angr2xyz(angr_arr):
    xyz_arr = get_init_arr(angr_arr)
    x = calc_x(angr_arr)
    y = calc_y(angr_arr)
    z = calc_z(angr_arr)
    xyz_arr = get_data_in_arr(xyz_arr, x, y, z)
    return xyz_arr

def cut_last_factor(arr):
    if arr.ndim == 1:
        return arr[:len(arr)-1]
    else:
        return arr[:,:len(arr[0])-1]

def add_factor(arr, factor):
    if arr.ndim == 1:
        new_arr = np.zeros(3)
        new_arr[:2] = arr
        new_arr[2] = factor
    else:
        size = len(arr)
        new_arr = np.zeros([size,3])
        new_arr[:,:2] = arr
        new_arr[:,2] += factor
    return new_arr

def xyz2xy(xyz_arr):
    xy_arr = cut_last_factor(xyz_arr)
    return xy_arr

def angr2ang(angr_arr):
    ang_arr = cut_last_factor(angr_arr)
    return ang_arr

def xy2xyz(xy_arr, z):
    return add_factor(xy_arr, z)

def ang2angr(ang_arr, r):
    return add_factor(ang_arr, r)

def rotate_with_yaw(xyz_arr, angle):
    pass