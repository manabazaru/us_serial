import numpy as np
class Parameter:
    N = 3                   # number of antenna arrays
    r = 20                  # radius of the HAPS's coverage
    ln = -20                # for antenna gain
    lf = -30                # for antenna gain
    a = 20                  # for antenna gain
    power = 43              # transmit power at each antenna array
    f = 2*10**9             # frequence        
    B = 20*10**6            # bandwidth
    noise = 4               # noise power
    actions = np.array(["ptilt", "ttilt", "p3db", "t3db"])
    kpi_state_num = 8
    states = np.array(["kpi"])
    d_ptilt = 5 # (-70,70)
    d_ttilt = 1 # (-10,12)
    d_p3db = 1 # (10,15)
    d_t3db = 1 # (10,19)
    power_threshold = -77