from numpy import int32
from UE_location import *
from HAPS import *
from style import *
from user import *
import os
class Environment_Initial:
    def __init__(self,method_name,distribution_type = 'uniform',movement_type='shift',num_ues_for_uniform = 1000,episodes = 100, steps = 100):
        
        self.distribution_type = distribution_type
        self.movement_type = movement_type
        self.num_ues_for_uniform = num_ues_for_uniform
        self.style = Style()
        self.user_location = User_location(self.distribution_type,self.num_ues_for_uniform)
        self.user_distribution_idx = np.zeros(self.user_location.shape[0],dtype=int32)
        self.method_name = method_name
        self.episodes = episodes
        self.steps = steps

        if self.movement_type == 'shift':
            self.h1 = Haps(-5,0,20,0)
            
        elif self.movement_type == 'rotate':
            self.h1 = Haps(0,0,20,30)

        elif self.movement_type == 'none':
            self.h1 = Haps(0,0,20,0)
        self.users = np.vectorize(lambda x,y: User(x,y))(self.user_location[:,0],self.user_location[:,1])
        self.user_antenna_idx_distribution()
        self.haps = np.array([],dtype=Haps)
        self.haps = np.append(self.haps,self.h1)

        for i in range(1,3):
            x = 2*Parameter.r * i
            y = 0
            for j in range(1, 7):
                step_x = 2 * Parameter.r * cosd(60 + 60 * j)
                step_y = 2 * Parameter.r * sind(60 + 60 * j)
                for k in range(1, i + 1):
                    h_all = Haps(x, y, 20, 0)
                    x = x + step_x
                    y = y + step_y
                    self.haps = np.append(self.haps,h_all)
        
        self.throughput_before = self.Throughput()
        self.throughput_after = np.zeros_like(self.throughput_before)

    def folder_check(self,name):
        if not os.path.exists(name):
            os.makedirs(name)

    def Sinr(self,users_x,user_y):
        signal = np.zeros((users_x.shape[0],Parameter.N*self.haps.size))
        haps_idx =0
        for hap in self.haps:
            SINR_3_db = hap.Received_Power(users_x,user_y)
            signal[:,(0+Parameter.N*haps_idx):(Parameter.N+Parameter.N*haps_idx)] = SINR_3_db
            haps_idx +=1
        signal = np.vectorize(lambda x: db2pow(x))(signal)
        s = np.max(signal,1)
        i = np.sum(signal,1)-s
        sinr = s/i
        Sinr = np.vectorize(lambda x: pow2db(x))(sinr)
        return Sinr-Parameter.noise
    
    def user_antenna_idx_distribution(self):
        X = self.user_location[:,0]
        Y = self.user_location[:,1] 

        signal = self.h1.Received_Power(X,Y)
        Antenna_distribution = np.argmax(signal,1)
        Antenna_distribution = np.squeeze(Antenna_distribution)
        for antenna_idx in range(Parameter.N):
            antenna_users_idx = np.argwhere(Antenna_distribution == antenna_idx)
            antenna_users_idx = np.squeeze(antenna_users_idx)
            self.user_distribution_idx[antenna_users_idx] = antenna_idx
            if antenna_users_idx.size == 0:
                self.h1.antennas[antenna_idx].user_this_antenna = np.array([],dtype = User)
                #self.h1.antennas[antenna_idx].throughput_users_this_antenna = np.array([])
            elif antenna_users_idx.size == 1:
                self.h1.antennas[antenna_idx].user_this_antenna = np.array([],dtype = User)

                self.h1.antennas[antenna_idx].user_this_antenna = np.append(self.h1.antennas[antenna_idx].user_this_antenna ,self.users[antenna_users_idx])
            else:
                self.h1.antennas[antenna_idx].user_this_antenna = self.users[antenna_users_idx]
    
    def Plot_sinr(self,Learning_state,folder_name,ue_plot_switch = False,save_switch = False):
        path_name = './'+ self.method_name+'/'+folder_name+'/'+str(self.episodes)+'/'
        file_name = self.movement_type +'_'+self.distribution_type+'_'+Learning_state+'.pdf'
        self.folder_check(path_name)
        fig, ax = self.style.Fig()
        ax.grid()
        x = np.arange(-25, 25.2, 0.5)
        y = np.arange(-25, 25.2, 0.5)
        X, Y = np.meshgrid(x, y)
        X = X.flatten()
        Y = Y.flatten()
        Z = self.Sinr(X,Y)
        Z = np.reshape(Z,(x.shape[0],y.shape[0]))
        X = np.reshape(X,(x.shape[0],y.shape[0]))
        Y = np.reshape(Y,(x.shape[0],y.shape[0]))
        ax.contourf(X, Y, Z, levels=20, cmap=self.style.Colormap(Z))
        colorbar = fig.colorbar(self.style.Mappable(Z), ax=ax)
        colorbar.set_label('SINR [dB]', size=20)
        ax.set_xlabel("km", fontsize=18)
        ax.set_ylabel("km", fontsize=18)
        #Kmeans_estimator = KMeans(n_clusters=3, random_state=10)
        #y_pred = Kmeans_estimator.fit_predict(self.user_location[:,0:2])
        #print('y_pred check', np.max(y_pred))
        #plt.scatter(self.user_location[:,0],self.user_location[:,1], s=1,c=y_pred)
        if ue_plot_switch:
            color_point = ['c','m','tab:brown']
            #if self.Learned == 0:
            colors = np.array([])
            for idx in range(self.user_distribution_idx.size):
                color_idx = int(self.user_distribution_idx[idx])
                colors = np.append(colors,color_point[color_idx])
            plt.scatter(self.user_location[:,0],self.user_location[:,1],s=1,color=colors)  
            plt.tight_layout()
        if save_switch:
            plt.savefig(path_name+file_name)
        plt.show()
    def Throughput(self):
        user_in_order = np.zeros_like(self.users)
        num_user = 0
        b = np.zeros(3)
        for i in range(3):
            if len(self.h1.antennas[i].user_this_antenna) == 0:
                b[i] = 0
                print('[Error]: UEs number is 0 !!!!!')
            else:
                b[i] = Parameter.B/len(self.h1.antennas[i].user_this_antenna)
        
        bandwidth = np.zeros(len(self.users))

        for antenna_idx in range(Parameter.N):
            users_antenna = self.h1.antennas[antenna_idx].user_this_antenna
            users_num_antenna = len(users_antenna)
            user_in_order[num_user:num_user+users_num_antenna] = users_antenna
            bandwidth[num_user:num_user+users_num_antenna] = b[antenna_idx]
            num_user += users_num_antenna
        
        user_location_in_order = np.zeros_like(self.user_location)
        idx = 0 
        for ue in user_in_order:
            user_location_in_order[idx,0] = ue.x
            user_location_in_order[idx,1] = ue.y
            idx +=1

        X = user_location_in_order[:,0]
        Y = user_location_in_order[:,1]
        sinr = self.Sinr(X,Y)
        sinr = np.vectorize(lambda s: db2pow(s))(sinr)
        
  
        return np.vectorize(lambda b, s: throughput(b, s))(bandwidth, sinr).flatten()
    def Plot_SINR_CDF(self,throughput_before,throughput_after,folder_name,epoch_idx = 0,save_switch = False,plot_switch = False):
        path_name = './'+ self.method_name+'/'+folder_name+'/'+str(self.episodes)+'/'
        SNR_file_name = 'SINR_'+self.movement_type +'_'+self.distribution_type+'_'+'after_'+str(epoch_idx)+'.pdf'
        CDF_file_name = 'CDF_'+self.movement_type+'_'+self.distribution_type+'_'+str(epoch_idx)+'.npy'
        self.folder_check(path_name)
        fig, axs = plt.subplots(1,2,figsize = (13,5))
        axs[0].grid()
        axs[0].set_title('SINR distribution')
        x = np.arange(-25, 25.2, 0.5)
        y = np.arange(-25, 25.2, 0.5)
        X, Y = np.meshgrid(x, y)
        X = X.flatten()
        Y = Y.flatten()
        Z = self.Sinr(X,Y)
        Z = np.reshape(Z,(x.shape[0],y.shape[0]))
        X = np.reshape(X,(x.shape[0],y.shape[0]))
        Y = np.reshape(Y,(x.shape[0],y.shape[0]))
        axs[0].contourf(X, Y, Z, levels=20, cmap=self.style.Colormap(Z))
        colorbar = fig.colorbar(self.style.Mappable(Z), ax=axs[0])
        colorbar.set_label('SINR [dB]', size=20)
        axs[0].set_xlabel("km", fontsize=18)
        axs[0].set_ylabel("km", fontsize=18)

        axs[1].set_title('CDF of throughput')
        axs[1].grid()
        before = np.sort(throughput_before / (10 ** 3))
        after = np.sort(throughput_after / (10 ** 3))
        cdf_y = 1. * np.arange(len(before)) / (len(before) - 1)
        axs[1].plot(before, cdf_y, color="black", label="Before Learning", linewidth=1.0)
        axs[1].plot(after, cdf_y, color="red", label="After "+ self.method_name, linewidth=1.0)
        # グラフの範囲を決める
        throughput_max = round(16, 1)
        throughput_min = round(np.min(before), 1)

        axs[1].set_xlim([throughput_min, throughput_max])
        axs[1].set_xlabel("Throughput (kbps)", fontsize=18)
        axs[1].set_ylabel("CDF of throughput", fontsize=18)

        if save_switch:
            plt.savefig(path_name+SNR_file_name)
            np.save(path_name+'before_'+CDF_file_name,before)
            np.save(path_name+'after_'+CDF_file_name,after)
        if plot_switch:
            plt.show()
        
        plt.close()

    
    def PlotThroughputCDF(self,throughput_before,throughput_after,folder_name,save_switch = False):
        path_name = './'+ self.method_name+'/'+folder_name+'/'+str(self.episodes)+'/'
        file_name = self.movement_type+'_'+self.distribution_type+'.npy'
        self.folder_check(path_name)
        fig, ax = self.style.Fig()
        before = np.sort(throughput_before / (10 ** 3))
        after = np.sort(throughput_after / (10 ** 3))
        cdf_y = 1. * np.arange(len(before)) / (len(before) - 1)
        ax.plot(before, cdf_y, color="black", label="Before Learning", linewidth=1.0)
        ax.plot(after, cdf_y, color="red", label="After "+ self.method_name, linewidth=1.0)
        ax.grid(True)
        if save_switch:
            np.save(path_name+'before_'+file_name,before)
            np.save(path_name+'after_'+file_name,after)
        # グラフの範囲を決める
        throughput_max = round(16, 1)
        throughput_min = round(np.min(before), 1)

        ax.set_xlim([throughput_min, throughput_max])

        ax.set_xlabel("Throughput [kbps]", fontsize=20)
        ax.set_ylabel("CDF of Users", fontsize=20)
        ax.legend(fontsize=15)
        plt.tight_layout()
        plt.show()
