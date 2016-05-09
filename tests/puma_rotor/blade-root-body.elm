# BLADE_LAG + 0:  2.690000e-01 ->  2.890000e-01 m (0.036 -> 0.039 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_LAG + 0, CURR_ROTOR + CURR_BLADE + BLADE_LAG + 0,
         5.256000e-01, # kg; dL= 9.000000e-03 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_LAG,
                 1.550000e-02, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_LAG,
                sym,      0.000000e+00, 0.000000e+00, 0.000000e+00,
                                        3.547800e-06, 0.000000e+00,
                                                      3.547800e-06;

# BLADE_FLAP + 0:  2.890000e-01 ->  4.320000e-01 m (0.039 -> 0.058 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_FLAP + 0, CURR_ROTOR + CURR_BLADE + BLADE_FLAP + 0,
         8.351200e+00, # kg; dL= 1.430000e-01 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_FLAP,
                 7.150000e-02, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_FLAP,
                sym,      0.000000e+00, 0.000000e+00, 0.000000e+00,
                                        1.423114e-02, 0.000000e+00,
                                                      1.423114e-02;

