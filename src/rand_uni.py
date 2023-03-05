import numpy as np
from parameters import Parameter as param

def generate_random_uniform_usr_xy(size, com_r):
    com_r_arr = np.sqrt(np.random.random_sample(size)) * com_r
    az_rad = 2*np.pi*(np.random.random_sample(size) - 0.5*np.ones(size))
    x = com_r_arr*np.cos(az_rad)
    y = com_r_arr*np.sin(az_rad)
    xy_arr = np.array([x,y]).T
    return xy_arr