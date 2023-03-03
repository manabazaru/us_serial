import matplotlib.pyplot as plt

def plt_all_users(xy_arr):
    fig = plt.figure()
    plt.scatter(xy_arr[:,0], xy_arr[:,1])
    plt.show()