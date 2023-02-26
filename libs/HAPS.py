from parameters import *
from utils import * 
import numpy as np




####### Antenna ########

class Antenna:
    def __init__(
            self,
            x,
            y,
            h,
            yaw,
            ttilt,
            ptilt,
            t3db,
            p3db,
            min_ttilt,
            max_ttilt,
            min_ptilt,
            max_ptilt,
            min_t3db,
            max_t3db,
            min_p3db,
            max_p3db
    ):

        self.x = x
        self.y = y
        self.h = h
        self.yaw = yaw

        self.ptilt = ptilt
        self.p_init = ptilt
        self.min_ptilt = min_ptilt
        self.max_ptilt = max_ptilt

        self.ttilt = ttilt
        self.t_init = ttilt
        self.min_ttilt = min_ttilt
        self.max_ttilt = max_ttilt

        self.p3db = p3db
        self.p3db_init = p3db
        self.min_p3db = min_p3db
        self.max_p3db = max_p3db

        self.t3db = t3db
        self.t3db_init = t3db
        self.min_t3db = min_t3db
        self.max_t3db = max_t3db
        self.gp = self.Gp()


    def G(self, deg, db):
        # print('db input',db)
        deg1 = db * (-Parameter.ln / 3) ** 0.5
        deg2 = 3.745 * db
        x = Parameter.ln + Parameter.a * math.log10(deg2)
        deg3 = 10 ** ((x - Parameter.lf) / 10)

        deg = abs(deg)
        if 0 <= deg <= deg1:
            return -3 * (deg / db) ** 2
        elif deg1 <= deg <= deg2:
            return Parameter.ln
        elif deg2 <= deg <= deg3:
            return x - Parameter.a * math.log10(deg)
        elif deg >= deg3:
            return Parameter.lf

    def Gp(self):
        return 10 * math.log10(80 ** 2 / (self.t3db * self.p3db))

    def Gain(self, theta, phi):
        out = self.G(theta, self.t3db) + self.G(phi, self.p3db)
        if out > Parameter.lf:
            return out + self.gp
        else:
            return Parameter.lf + self.gp

    def Signal(self, user_x,user_y):
        ttilt = self.ttilt
        ptilt = self.ptilt + self.yaw
        ta = theta_a(self.ttilt,
                     ptilt, self.h,
                     (user_x - self.x),
                     (user_y - self.y))
        pa = phi_a(ttilt,
                   ptilt,
                   self.h,
                   (user_x - self.x),
                   (user_y - self.y))
        t = ta * cosd(pa)
        p = ta * sind(pa)
        r = math.sqrt((user_x - self.x) ** 2
                      + (user_y - self.y) ** 2
                      + self.h ** 2)
        l = 300000 / Parameter.f
        los = 20 * math.log10(4 * math.pi * r / l)
        return Parameter.power + self.Gain(t, p) - los # dB



    def adjust(self):
        if self.min_ptilt >= self.ptilt:
            self.ptilt = self.min_ptilt
        elif self.max_ptilt <= self.ptilt:
            self.ptilt = self.max_ptilt
        if self.min_ttilt >= self.ttilt:
            self.ttilt = self.min_ttilt
        elif self.max_ttilt <= self.ttilt:
            self.ttilt = self.max_ttilt
        if self.min_p3db >= self.p3db:
            self.p3db = self.min_p3db
        elif self.max_p3db <= self.p3db:
            self.p3db = self.max_p3db
        if self.min_t3db >= self.t3db:
            self.t3db = self.min_t3db
        elif self.max_t3db <= self.t3db:
            self.t3db = self.max_t3db
    def KPI(self):
        x = np.zeros(self.user_this_antenna.size)
        y = np.zeros(self.user_this_antenna.size)
        for i in range(self.user_this_antenna.size):
            x[i] = self.user_this_antenna[i].x
            y[i] = self.user_this_antenna[i].y
        signal = np.vectorize(lambda ux,uy: self.Signal(ux,uy))(x,y)
        return np.count_nonzero(signal > Parameter.power_threshold) / signal.size
#     def KPI(self):
#         signal = np.vectorize(lambda u: self.Signal(u))(self.users)
#         return np.count_nonzero(signal > Parameter.power_threshold) / signal.size

    def Initialize(self):
        self.ptilt = self.p_init
        self.ttilt = self.t_init
        self.p3db = self.p3db_init
        self.t3db = self.t3db_init



####### HAPS ########

class Haps:
    def __init__(self,x,y,h,yaw,num_antenna = 3):
        self.x = x
        self.y = y
        self.h = h
        self.yaw = yaw
        self.antennas = np.array([],dtype = Antenna)
        if num_antenna == 3:
            for antenna_idx in range(1,Parameter.N+1):
                t3db = 10
                p3db = 10
                ptilt = 120*(antenna_idx-1) + 60
                ttilt = atand(1/2)
                min_t3db = 10
                max_t3db = 15
                min_p3db = 10
                max_p3db = 19
                min_ttilt = ttilt - 10
                max_ttilt = ttilt + 12
                min_ptilt = ptilt - 70
                max_ptilt = ptilt + 70
                self.antennas=np.append(self.antennas,Antenna(
                    self.x,
                    self.y,
                    self.h,
                    self.yaw,
                    ttilt,
                    ptilt,
                    t3db,
                    p3db,
                    min_ttilt,
                    max_ttilt,
                    min_ptilt,
                    max_ptilt,
                    min_t3db,
                    max_t3db,
                    min_p3db,
                    max_p3db
                ))
        elif num_antenna == 1 :
            t3db = 15
            p3db = 15
            ptilt = 0
            ttilt = 0
            min_t3db = 10
            max_t3db = 15
            min_p3db = 10
            max_p3db = 19
            min_ttilt = ttilt - 10
            max_ttilt = ttilt + 12
            min_ptilt = ptilt - 70
            max_ptilt = ptilt + 70
            self.antennas=np.append(self.antennas,Antenna(
                self.x,
                self.y,
                self.h,
                self.yaw,
                ttilt,
                ptilt,
                t3db,
                p3db,
                min_ttilt,
                max_ttilt,
                min_ptilt,
                max_ptilt,
                min_t3db,
                max_t3db,
                min_p3db,
                max_p3db
            ))
    def Received_Power(self,x,y):
        user_x = x
        user_y = y
       #print('Received_power, x.shape',user_x.shape[0])
        received_signal = np.zeros((user_x.shape[0],Parameter.N))
        for antenna_idx in range(Parameter.N):
            signal_power = np.vectorize(lambda x,y: self.antennas[antenna_idx].Signal(x,y))(user_x,user_y)
            #signal_power = np.expand_dims(signal_power,1)
            
            received_signal[:,antenna_idx] = signal_power
        
        return received_signal
    def Received_Power_1(self, x, y):
        user_x = x
        user_y = y
       #print('Received_power, x.shape',user_x.shape[0])
        signal_power = np.vectorize(lambda x,y: self.antennas[0].Signal(x,y))(user_x,user_y)
        signal_power = np.expand_dims(signal_power,1)
            
        
        return signal_power
# class Agent:
#     def __init__(self, x, y, h, yaw):
#         self.antennas = Haps(x, y, h, yaw)
#     def Signal(self, antenna, user):
#         return db2pow(antenna.Signal(user))

#     def Throughput(self, users):
#         user_num = users.shape[0]
#         users = np.tile(self.users.reshape(1, -1, 1), (1, 1, Parameter.N)).reshape(-1, Parameter.N)
#         antennas = np.tile(self.antennas.reshape(1, -1), (user_num * Parameter.N, 1))
#         i = np.tile(np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]]), (1, user_num)).reshape(-1, Parameter.N)
#         signals = np.vectorize(lambda a, u: self.Signal(a, u))(antennas, users)
#         interference = np.sum(signals * i, axis=1).reshape(-1, user_num * Parameter.N)
#         s = np.sum(signals, axis=1).reshape(-1, user_num * Parameter.N) - interference
#         sinr = np.vectorize(lambda s: pow2db(s))(s / interference).reshape(-1, user_num) - Parameter.noise
#         sinr = np.vectorize(lambda s: db2pow(s))(sinr)
#         b = Parameter.B * Parameter.N / sinr.size
#         bandwidth = np.full_like(sinr, b)
#         return np.vectorize(lambda b, s: throughput(b, s))(bandwidth, sinr).flatten()


