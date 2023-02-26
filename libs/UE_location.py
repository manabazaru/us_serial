import math
from parameters import *
from utils import *
import scipy.io as scio
import numpy as np
#  Loading User Distribution

def User_location(type,num_ues_for_uniform = 1000):
    user_location = np.zeros(((int(math.sqrt(num_ues_for_uniform))**2)*Parameter.N,2))
    # user_loation: ( x, y, antenna_idx)
    # for uniform distribution, antenna_idx is intialized by this function
    # for other distribution, antenna_idx should be initialized based on the received power.
    if type == 'uniform':
        for index_antenna in range(Parameter.N):
            #'''
            # Uniform Distribution
            Number_user_each_antenna = num_ues_for_uniform
            #'''
            # Uniform Distribution
            r = np.sqrt(np.linspace(0**2,Parameter.r**2,int(math.sqrt(Number_user_each_antenna))))
            deg = np.linspace(0,120,int(math.sqrt(Number_user_each_antenna)))+120*index_antenna
            R, Deg = np.meshgrid(r, deg)
            r = R.flatten()
            deg = Deg.flatten()
            R,Deg = r,deg
            X,Y = np.vectorize(lambda  r, d: pol2xy(r,d))(R,Deg)
            

            for index_user in range(X.shape[0]):
                # calculate x,y
                #print('X,Y check',X[index_user],Y[index_user])

                user_location[X.shape[0]*index_antenna+index_user,0] = X[index_user]#cosd(deg[index_user])*r[index_user]
                user_location[X.shape[0]*index_antenna+index_user,1] = Y[index_user]#sind(deg[index_user])*r[index_user]
                user_location[X.shape[0]*index_antenna+index_user,2] = index_antenna+1
    elif type=='tokyo':
        # tokyo 
        location_load = scio.loadmat('../UEs_Location/tokyo_20km_scale_0.0005_date_20210129.mat')['all_UE']
        user_location = np.zeros((location_load.shape[0],2))
        user_location[:,0] = location_load[:,0]
        user_location[:,1] = location_load[:,1]
        user_location /=1000
    elif type=='osaka':
        # osaka
        location_load = scio.loadmat('../UEs_Location/osaka_20km_scale_0.0005_date_20210129.mat')['all_UE']
        user_location = np.zeros((location_load.shape[0],2))
        user_location[:,0] = location_load[:,0]
        user_location[:,1] = location_load[:,1]
        user_location /=1000
    elif type=='sendai':
        # sentai
        location_load = scio.loadmat('../UEs_Location/sendai_20km_scale_0.005_date_20210129.mat')['all_UE']
        user_location = np.zeros((location_load.shape[0],2))
        user_location[:,0] = location_load[:,0]
        user_location[:,1] = location_load[:,1]
        user_location /=1000
    elif type=='nagoya':
        # nagoya
        location_load = scio.loadmat('../UEs_Location/nagoya_20km_scale_0.005_date_20210129.mat')['all_UE']
        user_location = np.zeros((location_load.shape[0],2))
        user_location[:,0] = location_load[:,0]
        user_location[:,1] = location_load[:,1]
        user_location /=1000
    elif type=='yagami':
        # yagami
        location_load = scio.loadmat('../UEs_Location/yagami_20km_scale_0.0005_date_20210129.mat')['all_UE']
        user_location = np.zeros((location_load.shape[0],2))
        user_location[:,0] = location_load[:,0]
        user_location[:,1] = location_load[:,1]
        user_location /=1000
    else:
        print('Input area is uncorrect')
    
    return user_location