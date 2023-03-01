class Parameter:
    users_per_group = 12
    z = 20
    c = 299792.458   # light speed [km/s]
    com_range = 20   # communication range [km]
    # for haps
    side_horizonal_antenna = 31
    side_vertical_antenna = 6
    bottom_antenna = 10
    carrier_freq = 2.5 * 10**9
    antenna_height = 4.4 * 10**-4
    # for beamforming
    three_bandwidth_angle = 65
    max_attenuation = 30
    side_lobe_attenuation = 30
    trans_gain = 8
    rcv_gain = -3
    # for eval
    noise_figure = 5
    bandwidth = 1.8 * 10**7
    trans_pwr = 120
    noise_power_density = -174