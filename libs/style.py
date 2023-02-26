from matplotlib import pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable, get_cmap


class Style:
    colors = ["red", "blue", "g", "c", "m"]
    fuzzy_labels = [r'$M_1$',r'$M_2$',r'$M_3$',r'$M_4$',r'$M_5$']
    kpi_labels = [r'$KPI_1$', r'$KPI_2$', r'$KPI_3$']

    def Fig(self):
        # plt.rc('text', usetex=True)
        fig, ax = plt.subplots(figsize=(5,5))
        ax.grid()
        return fig, ax

    def Mappable(self,data):
        norm = Normalize(vmin=data.min(), vmax=data.max())
        #norm = Normalize(vmin=-20, vmax=20)
        cmap = get_cmap('jet')
        mappable = ScalarMappable(cmap=cmap, norm=norm)
        
        mappable._A = []
        return mappable

    def Colormap(self,data):
        cmap = get_cmap('jet')
        return cmap
    def PointColormap(self,data):
        color_point = ['y','g','purple']
        cmap = color_point
        return cmap