# This is the MBDyn model of the AS330 Puma described in Bousman 1996

# BLADE_PITCH + 0:  4.320000e-01 ->  6.450758e-01 m (0.058 -> 0.086 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 0, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 0,
        condense, 4,
         9.811200e+00, # kg; dL= 1.680000e-01 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 8.400000e-02, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      0.000000e+00, 0.000000e+00, 0.000000e+00,
                                        2.307594e-02, 0.000000e+00,
                                                      2.307594e-02,
         2.336000e-01, # kg; dL= 4.000000e-03 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.700000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      0.000000e+00, 0.000000e+00, 0.000000e+00,
                                        3.114667e-07, 0.000000e+00,
                                                      3.114667e-07,
         3.504000e-01, # kg; dL= 6.000000e-03 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.750000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.152000e-03, 0.000000e+00, 0.000000e+00,
                                        1.051200e-06, 0.000000e+00,
                                                      1.153051e-03,
         1.753792e+00, # kg; dL= 3.507584e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.955379e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      5.824207e-03, 0.000000e+00, 0.000000e+00,
                                        1.798097e-04, 0.000000e+00,
                                                      6.004016e-03;

# BLADE_PITCH + 1:  6.450758e-01 ->  1.227210e+00 m (0.086 -> 0.164 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 1, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 1,
        condense, 19,
         3.996208e+00, # kg; dL= 7.992416e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 2.530379e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.380725e-02, 0.000000e+00, 0.000000e+00,
                                        2.127272e-03, 0.000000e+00,
                                                      1.593452e-02,
         2.500000e-01, # kg; dL= 5.000000e-03 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 2.955000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      8.885417e-04, 0.000000e+00, 0.000000e+00,
                                        5.208333e-07, 0.000000e+00,
                                                      8.890625e-04,
         3.882000e-01, # kg; dL= 2.400000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 3.100000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.952000e-03, 0.000000e+00, 0.000000e+00,
                                        1.863360e-05, 0.000000e+00,
                                                      2.970634e-03,
         3.199980e-01, # kg; dL= 6.000000e-03 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 3.250000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.595000e-03, 0.000000e+00, 0.000000e+00,
                                        9.599940e-07, 0.000000e+00,
                                                      2.595960e-03,
         9.979600e-01, # kg; dL= 4.000000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 3.480000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      8.900000e-03, 0.000000e+00, 0.000000e+00,
                                        1.330613e-04, 0.000000e+00,
                                                      9.033061e-03,
         3.310000e-01, # kg; dL= 1.000000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 3.730000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      3.236944e-03, 0.000000e+00, 0.000000e+00,
                                        2.758333e-06, 0.000000e+00,
                                                      3.239703e-03,
         3.310000e-01, # kg; dL= 1.000000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 3.830000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      3.350833e-03, 0.000000e+00, 0.000000e+00,
                                        2.758333e-06, 0.000000e+00,
                                                      3.353592e-03,
         2.648000e-01, # kg; dL= 8.000000e-03 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 3.920000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.762667e-03, 0.000000e+00, 0.000000e+00,
                                        1.412267e-06, 0.000000e+00,
                                                      2.764079e-03,
         2.648000e-01, # kg; dL= 8.000000e-03 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 4.000000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.835556e-03, 0.000000e+00, 0.000000e+00,
                                        1.412267e-06, 0.000000e+00,
                                                      2.836968e-03,
         3.310000e-02, # kg; dL= 1.000000e-03 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 4.045000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.395000e-04, 0.000000e+00, 0.000000e+00,
                                        2.758333e-09, 0.000000e+00,
                                                      2.395028e-04,
         9.930000e-02, # kg; dL= 3.000000e-03 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 4.065000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      3.615000e-04, 0.000000e+00, 0.000000e+00,
                                        7.447500e-08, 0.000000e+00,
                                                      3.615745e-04,
         7.392000e-01, # kg; dL= 3.300000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 4.245000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.825975e-03, 0.000000e+00, 0.000000e+00,
                                        6.708240e-05, 0.000000e+00,
                                                      2.893057e-03,
         2.060800e+00, # kg; dL= 9.200000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 4.870000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      9.145424e-03, 0.000000e+00, 0.000000e+00,
                                        1.453551e-03, 0.000000e+00,
                                                      1.059897e-02,
         1.164800e+00, # kg; dL= 5.200000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 5.590000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      5.994102e-03, 0.000000e+00, 0.000000e+00,
                                        2.624683e-04, 0.000000e+00,
                                                      6.256570e-03,
         5.152000e-01, # kg; dL= 2.300000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 5.965000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.518500e-03, 0.000000e+00, 0.000000e+00,
                                        2.271173e-05, 0.000000e+00,
                                                      2.541212e-03,
         7.699500e-01, # kg; dL= 4.500000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 6.305000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.587500e-03, 0.000000e+00, 0.000000e+00,
                                        1.299291e-04, 0.000000e+00,
                                                      2.717429e-03,
         4.277500e-01, # kg; dL= 2.500000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 6.655000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.000000e-03, 0.000000e+00, 0.000000e+00,
                                        2.227865e-05, 0.000000e+00,
                                                      1.022279e-03,
         1.122500e-02, # kg; dL= 1.000000e-03 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 6.785000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.600000e-05, 0.000000e+00, 0.000000e+00,
                                        9.354167e-10, 0.000000e+00,
                                                      2.600094e-05,
         1.304456e+00, # kg; dL= 1.162099e-01 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 7.371049e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      3.021457e-03, 0.000000e+00, 0.000000e+00,
                                        1.468027e-03, 0.000000e+00,
                                                      4.489484e-03;

# BLADE_PITCH + 2:  1.227210e+00 ->  1.653362e+00 m (0.164 -> 0.221 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 2, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 2,
        condense, 4,
         1.435692e-01, # kg; dL= 1.279013e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 8.016049e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      3.325433e-04, 0.000000e+00, 0.000000e+00,
                                        1.957176e-06, 0.000000e+00,
                                                      3.345005e-04,
         1.122500e-01, # kg; dL= 1.000000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 8.130000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.600000e-04, 0.000000e+00, 0.000000e+00,
                                        9.354167e-07, 0.000000e+00,
                                                      2.609354e-04,
         1.122500e-01, # kg; dL= 1.000000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 8.230000e-01, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.600000e-04, 0.000000e+00, 0.000000e+00,
                                        9.354167e-07, 0.000000e+00,
                                                      2.609354e-04,
         2.812535e+00, # kg; dL= 3.933616e-01 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.024681e+00, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      9.721133e-03, 0.000000e+00, 0.000000e+00,
                                        3.626607e-02, 0.000000e+00,
                                                      4.598721e-02;

# BLADE_PITCH + 3:  1.653362e+00 ->  2.235496e+00 m (0.221 -> 0.298 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 3, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 3,
        condense, 8,
         3.120149e-01, # kg; dL= 4.363844e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.243181e+00, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.452357e-03, 0.000000e+00, 0.000000e+00,
                                        4.951452e-05, 0.000000e+00,
                                                      1.501872e-03,
         4.290000e-01, # kg; dL= 6.000000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.295000e+00, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.118824e-03, 0.000000e+00, 0.000000e+00,
                                        1.287000e-04, 0.000000e+00,
                                                      2.247524e-03,
         9.295000e-02, # kg; dL= 1.300000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.331500e+00, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      4.776863e-04, 0.000000e+00, 0.000000e+00,
                                        1.309047e-06, 2.167672e-08,
                                                      4.789953e-04,
         8.784910e-01, # kg; dL= 1.100000e-01 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.393000e+00, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.070761e-02, 0.000000e+00, 0.000000e+00,
                                        8.858142e-04, 5.083217e-06,
                                                      1.159342e-02,
         6.213047e-02, # kg; dL= 7.000000e-03 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.451500e+00, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      7.583932e-04, 0.000000e+00, 0.000000e+00,
                                        2.542909e-07, 6.697644e-07,
                                                      7.586463e-04,
         1.071480e+00, # kg; dL= 1.200000e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.515000e+00,-5.369995e-03, 7.123036e-06,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.304910e-02, 0.000000e+00, 0.000000e+00,
                                        1.285799e-03, 1.730896e-05,
                                                      1.433485e-02,
         1.080409e+00, # kg; dL= 1.210000e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.635500e+00,-5.369982e-03, 1.390865e-05,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.315784e-02, 0.000000e+00, 0.000000e+00,
                                        1.318277e-03, 3.407957e-05,
                                                      1.447595e-02,
         9.598281e-01, # kg; dL= 1.074956e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.749748e+00,-5.369953e-03, 2.247483e-05,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.168934e-02, 0.000000e+00, 0.000000e+00,
                                        9.244633e-04, 4.892246e-05,
                                                      1.261339e-02;

# BLADE_PITCH + 4:  2.235496e+00 ->  2.661647e+00 m (0.298 -> 0.355 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 4, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 4,
        condense, 4,
         1.920129e-01, # kg; dL= 2.150441e-02 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.814248e+00,-5.369931e-03, 2.731094e-05,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.338444e-03, 0.000000e+00, 0.000000e+00,
                                        7.460021e-06, 1.189279e-05,
                                                      2.345783e-03,
         1.875090e-01, # kg; dL= 2.100000e-02 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.835500e+00,-5.369920e-03, 2.936495e-05,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.283593e-03, 0.000000e+00, 0.000000e+00,
                                        6.959241e-06, 1.248726e-05,
                                                      2.290415e-03,
         2.044741e+00, # kg; dL= 2.290000e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 1.960500e+00,-5.369818e-03, 4.421988e-05,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.490204e-02, 0.000000e+00, 0.000000e+00,
                                        8.937377e-03, 2.050517e-04,
                                                      3.383604e-02,
         1.380845e+00, # kg; dL= 1.546473e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 2.152324e+00,-5.369564e-03, 6.843571e-05,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.681673e-02, 0.000000e+00, 0.000000e+00,
                                        2.754731e-03, 2.142964e-04,
                                                      1.956600e-02;

# BLADE_PITCH + 5:  2.661647e+00 ->  3.243781e+00 m (0.355 -> 0.433 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 5, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 5,
        condense, 3,
         8.514045e-01, # kg; dL= 9.535273e-02 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 2.277324e+00,-5.369318e-03, 8.558547e-05,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.036890e-02, 0.000000e+00, 0.000000e+00,
                                        6.477248e-04, 1.652354e-04,
                                                      1.101135e-02,
         2.232250e+00, # kg; dL= 2.500000e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 2.450000e+00,-5.368950e-03, 1.061826e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.718563e-02, 0.000000e+00, 0.000000e+00,
                                        1.163693e-02, 5.374443e-04,
                                                      3.880130e-02,
         2.114220e+00, # kg; dL= 2.367813e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 2.693391e+00,-5.368320e-03, 1.343039e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.574819e-02, 0.000000e+00, 0.000000e+00,
                                        9.893986e-03, 6.437620e-04,
                                                      3.560997e-02;

# BLADE_PITCH + 6:  3.243781e+00 ->  3.669933e+00 m (0.433 -> 0.490 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 6, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 6,
        condense, 3,
         1.180298e-01, # kg; dL= 1.321870e-02 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 2.818391e+00,-5.367928e-03, 1.491540e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.437435e-03, 0.000000e+00, 0.000000e+00,
                                        2.827595e-06, 3.990996e-05,
                                                      1.438044e-03,
         2.232250e+00, # kg; dL= 2.500000e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 2.950000e+00,-5.367542e-03, 1.624461e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.718563e-02, 0.000000e+00, 0.000000e+00,
                                        1.165118e-02, 8.220070e-04,
                                                      3.878705e-02,
         1.454829e+00, # kg; dL= 1.629330e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 3.156466e+00,-5.366878e-03, 1.830910e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.771774e-02, 0.000000e+00, 0.000000e+00,
                                        3.239060e-03, 6.037381e-04,
                                                      2.091561e-02;

# BLADE_PITCH + 7:  3.669933e+00 ->  4.252067e+00 m (0.490 -> 0.568 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 7, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 7,
         5.197875e+00, # kg; dL= 5.821340e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 3.529000e+00,-5.365479e-03, 2.203035e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      6.330272e-02, 0.000000e+00, 0.000000e+00,
                                        1.468945e-01, 2.594799e-03,
                                                      2.099842e-01;

# BLADE_PITCH + 8:  4.252067e+00 ->  4.678219e+00 m (0.568 -> 0.625 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 8, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 8,
         3.805108e+00, # kg; dL= 4.261517e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 4.033143e+00,-5.363175e-03, 2.706453e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      4.634081e-02, 0.000000e+00, 0.000000e+00,
                                        5.770335e-02, 2.332586e-03,
                                                      1.038087e-01;

# BLADE_PITCH + 9:  4.678219e+00 ->  5.260353e+00 m (0.625 -> 0.702 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 9, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 9,
        condense, 2,
         5.105435e+00, # kg; dL= 5.717813e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 4.532109e+00,-5.360430e-03, 3.204468e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      6.217694e-02, 0.000000e+00, 0.000000e+00,
                                        1.393164e-01, 3.703705e-03,
                                                      2.010505e-01,
         9.243951e-02, # kg; dL= 1.035273e-02 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 4.823176e+00,-5.358615e-03, 3.494855e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.125782e-03, 0.000000e+00, 0.000000e+00,
                                        5.593935e-06, 7.311178e-05,
                                                      1.121839e-03;

# BLADE_PITCH + 10:  5.260353e+00 ->  5.686504e+00 m (0.702 -> 0.759 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 10, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 10,
         3.805108e+00, # kg; dL= 4.261517e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 5.041429e+00,-5.357151e-03, 3.712530e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      4.634081e-02, 0.000000e+00, 0.000000e+00,
                                        5.780713e-02, 3.196090e-03,
                                                      1.037050e-01;

# BLADE_PITCH + 11:  5.686504e+00 ->  6.268638e+00 m (0.759 -> 0.837 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 11, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 11,
        condense, 4,
         1.013402e+00, # kg; dL= 1.134956e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 5.311252e+00,-5.355219e-03, 3.981556e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.234180e-02, 0.000000e+00, 0.000000e+00,
                                        1.155671e-03, 9.125566e-04,
                                                      1.336177e-02,
         2.767990e+00, # kg; dL= 3.100000e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 5.523000e+00,-5.353608e-03, 4.192607e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      3.371018e-02, 0.000000e+00, 0.000000e+00,
                                        2.237247e-02, 2.623876e-03,
                                                      5.567168e-02,
         1.312563e+00, # kg; dL= 1.470000e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 5.751500e+00,-5.351776e-03, 4.420282e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.598515e-02, 0.000000e+00, 0.000000e+00,
                                        2.471908e-03, 1.311342e-03,
                                                      1.824044e-02,
         1.039197e-01, # kg; dL= 1.163844e-02 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 5.830819e+00,-5.351118e-03, 4.499305e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.265594e-03, 0.000000e+00, 0.000000e+00,
                                        1.005760e-05, 1.056661e-04,
                                                      1.257882e-03;

# BLADE_PITCH + 12:  6.268638e+00 ->  6.694790e+00 m (0.837 -> 0.894 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 12, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 12,
         3.805108e+00, # kg; dL= 4.261517e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 6.049714e+00,-5.349237e-03, 4.717631e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      4.634081e-02, 0.000000e+00, 0.000000e+00,
                                        5.794330e-02, 4.055373e-03,
                                                      1.035688e-01;

# BLADE_PITCH + 13:  6.694790e+00 ->  7.276924e+00 m (0.894 -> 0.972 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 13, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 13,
        condense, 3,
         3.350249e+00, # kg; dL= 3.752099e-01 m; ycg=-5.370000e-03 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 6.450395e+00,-5.345564e-03, 5.117063e-04,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      4.080127e-02, 0.000000e+00, 0.000000e+00,
                                        3.967517e-02, 3.870253e-03,
                                                      7.973547e-02,
         2.180934e+00, # kg; dL= 1.710000e-01 m; ycg= 1.611000e-02 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 6.723500e+00, 1.602867e-02,-1.616747e-03,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.610998e-02, 0.000000e+00, 0.000000e+00,
                                        5.577357e-03, 2.607083e-03,
                                                      3.116140e-02,
         4.581767e-01, # kg; dL= 3.592416e-02 m; ycg= 1.611000e-02 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 6.826962e+00, 1.602552e-02,-1.647659e-03,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      5.485257e-03, 0.000000e+00, 0.000000e+00,
                                        1.066522e-04, 5.580658e-04,
                                                      5.477154e-03;

# BLADE_PITCH + 14:  7.276924e+00 ->  7.490000e+00 m (0.972 -> 1.000 R)
body: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 14, CURR_ROTOR + CURR_BLADE + BLADE_BODY + 14,
        condense, 8,
         2.943093e-01, # kg; dL= 2.307584e-02 m; ycg= 1.611000e-02 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 6.856462e+00, 1.602461e-02,-1.656472e-03,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      3.523449e-03, 0.000000e+00, 0.000000e+00,
                                        5.031146e-05, 3.603699e-04,
                                                      3.499257e-03,
         1.275400e-01, # kg; dL= 1.000000e-02 m; ycg= 1.611000e-02 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 6.873000e+00, 1.602410e-02,-1.661413e-03,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.526899e-03, 0.000000e+00, 0.000000e+00,
                                        1.730239e-05, 1.566284e-04,
                                                      1.511723e-03,
         5.101600e-01, # kg; dL= 4.000000e-02 m; ycg= 1.611000e-02 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 6.898000e+00, 1.602332e-02,-1.668881e-03,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      6.107597e-03, 0.000000e+00, 0.000000e+00,
                                        1.335649e-04, 6.292992e-04,
                                                      6.110075e-03,
         4.081280e-01, # kg; dL= 3.200000e-02 m; ycg= 1.611000e-02 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 6.934000e+00, 1.602220e-02,-1.679634e-03,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      4.886078e-03, 0.000000e+00, 0.000000e+00,
                                        8.793964e-05, 5.066477e-04,
                                                      4.867792e-03,
         1.020320e-01, # kg; dL= 8.000000e-03 m; ycg= 1.611000e-02 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 6.954000e+00, 1.602157e-02,-1.685608e-03,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      1.221519e-03, 0.000000e+00, 0.000000e+00,
                                        1.391697e-05, 1.271074e-04,
                                                      1.208691e-03,
         4.152000e-01, # kg; dL= 1.200000e-02 m; ycg= 7.893900e-02 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 6.964000e+00, 7.850417e-02,-8.274112e-03,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,     -1.632630e-04, 0.000000e+00, 0.000000e+00,
                                        3.188710e-06,-1.701840e-05,
                                                     -1.564870e-04,
         2.217600e-01, # kg; dL= 3.200000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 6.986000e+00, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      2.144000e-03, 0.000000e+00, 0.000000e+00,
                                        4.266226e-05, 2.243487e-04,
                                                      2.139185e-03,
         3.880800e-01, # kg; dL= 5.600000e-02 m; ycg= 0.000000e+00 m
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                 7.030000e+00, 0.000000e+00, 0.000000e+00,
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                sym,      6.608000e-03, 0.000000e+00, 0.000000e+00,
                                        1.757219e-04, 6.967620e-04,
                                                      6.635115e-03;

# BLADE_PITCH + 0:  4.320000e-01 ->  1.440286e+00 m (0.058 -> 0.192 R)
#     x1= 6.450758e-01 xm= 9.361429e-01 x2= 1.227210e+00 (0.086 -> 0.125 -> 0.164 R
beam: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 0,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 0,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 1,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 2,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        # point 1
        # twist=0.000 deg
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                1,  1.000000e+00, 0.000000e+00, 0.000000e+00,
                2,  0.000000e+00, 1.000000e+00, 0.000000e+00,
        # EA= 5.690000e+08 N EJf= 1.370000e+06 Nm^2 EJl= 1.370000e+06 Nm^2 GJ= 8.400000e+05 Nm^2
        linear viscoelastic generic,
                sym,     5.690000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,-0.000000e+00,
                                       5.690000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                     5.690000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                                   8.400000e+05, 0.000000e+00, 0.000000e+00,
                                                                                 1.370000e+06, 0.000000e+00,
                                                                                               1.370000e+06,
                proportional, blade_damp,
        # point 2
        # twist=0.000 deg
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                1,  1.000000e+00, 0.000000e+00, 0.000000e+00,
                2,  0.000000e+00, 1.000000e+00, 0.000000e+00,
        # EA= 3.740000e+08 N EJf= 4.100000e+05 Nm^2 EJl= 1.780000e+06 Nm^2 GJ= 8.500000e+04 Nm^2
        linear viscoelastic generic,
                sym,     3.740000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,-0.000000e+00,
                                       3.740000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                     3.740000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                                   8.500000e+04, 0.000000e+00, 0.000000e+00,
                                                                                 4.100000e+05,-0.000000e+00,
                                                                                               1.780000e+06,
                proportional, blade_damp;

# BLADE_PITCH + 1:  1.440286e+00 ->  2.448571e+00 m (0.192 -> 0.327 R)
#     x1= 1.653362e+00 xm= 1.944429e+00 x2= 2.235496e+00 (0.221 -> 0.260 -> 0.298 R
beam: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 1,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 2,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 3,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 4,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        # point 1
        # twist=0.000 deg
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                1,  1.000000e+00, 0.000000e+00, 0.000000e+00,
                2,  0.000000e+00, 1.000000e+00, 0.000000e+00,
        # EA= 1.690000e+08 N EJf= 8.100000e+04 Nm^2 EJl= 1.523350e+06 Nm^2 GJ= 8.500000e+04 Nm^2
        linear viscoelastic generic,
                sym,     1.690000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,-0.000000e+00,
                                       1.690000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                     1.690000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                                   8.500000e+04, 0.000000e+00, 0.000000e+00,
                                                                                 8.100000e+04,-0.000000e+00,
                                                                                               1.523350e+06,
                proportional, blade_damp,
        # point 2
        # twist=-0.300 deg
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                1,  1.000000e+00, 0.000000e+00, 0.000000e+00,
                2,  0.000000e+00, 9.999863e-01,-5.235964e-03,
        # EA= 1.536600e+08 N EJf= 8.100000e+04 Nm^2 EJl= 1.515020e+06 Nm^2 GJ= 8.500000e+04 Nm^2
        linear viscoelastic generic,
                sym,     1.536600e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,-0.000000e+00,
                                       1.536600e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                     1.536600e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                                   8.500000e+04, 0.000000e+00, 0.000000e+00,
                                                                                 8.100000e+04,-0.000000e+00,
                                                                                               1.515020e+06,
                proportional, blade_damp;

# BLADE_PITCH + 2:  2.448571e+00 ->  3.456857e+00 m (0.327 -> 0.462 R)
#     x1= 2.661647e+00 xm= 2.952714e+00 x2= 3.243781e+00 (0.355 -> 0.394 -> 0.433 R
beam: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 2,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 4,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 5,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 6,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        # point 1
        # twist=-0.983 deg
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                1,  1.000000e+00, 0.000000e+00, 0.000000e+00,
                2,  0.000000e+00, 9.998528e-01,-1.715574e-02,
        # EA= 1.500330e+08 N EJf= 8.100000e+04 Nm^2 EJl= 1.507582e+06 Nm^2 GJ= 8.500000e+04 Nm^2
        linear viscoelastic generic,
                sym,     1.500330e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,-0.000000e+00,
                                       1.500330e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                     1.500330e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                                   8.500000e+04, 0.000000e+00, 0.000000e+00,
                                                                                 8.100000e+04,-0.000000e+00,
                                                                                               1.507582e+06,
                proportional, blade_damp,
        # point 2
        # twist=-1.600 deg
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                1,  1.000000e+00, 0.000000e+00, 0.000000e+00,
                2,  0.000000e+00, 9.996101e-01,-2.792164e-02,
        # EA= 1.490236e+08 N EJf= 8.100000e+04 Nm^2 EJl= 1.500144e+06 Nm^2 GJ= 8.500000e+04 Nm^2
        linear viscoelastic generic,
                sym,     1.490236e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,-0.000000e+00,
                                       1.490236e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                     1.490236e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                                   8.500000e+04, 0.000000e+00, 0.000000e+00,
                                                                                 8.100000e+04,-0.000000e+00,
                                                                                               1.500144e+06,
                proportional, blade_damp;

# BLADE_PITCH + 3:  3.456857e+00 ->  4.465143e+00 m (0.462 -> 0.596 R)
#     x1= 3.669933e+00 xm= 3.961000e+00 x2= 4.252067e+00 (0.490 -> 0.529 -> 0.568 R
beam: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 3,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 6,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 7,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 8,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        # point 1
        # twist=-3.726 deg
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                1,  1.000000e+00, 0.000000e+00, 0.000000e+00,
                2,  0.000000e+00, 9.978862e-01,-6.498495e-02,
        # EA= 1.450000e+08 N EJf= 8.100000e+04 Nm^2 EJl= 1.470496e+06 Nm^2 GJ= 8.500000e+04 Nm^2
        linear viscoelastic generic,
                sym,     1.450000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,-0.000000e+00,
                                       1.450000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                     1.450000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                                   8.500000e+04, 0.000000e+00, 0.000000e+00,
                                                                                 8.100000e+04,-0.000000e+00,
                                                                                               1.470496e+06,
                proportional, blade_damp,
        # point 2
        # twist=-3.726 deg
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                1,  1.000000e+00, 0.000000e+00, 0.000000e+00,
                2,  0.000000e+00, 9.978862e-01,-6.498495e-02,
        # EA= 1.450000e+08 N EJf= 8.100000e+04 Nm^2 EJl= 1.470496e+06 Nm^2 GJ= 8.500000e+04 Nm^2
        linear viscoelastic generic,
                sym,     1.450000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,-0.000000e+00,
                                       1.450000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                     1.450000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                                   8.500000e+04, 0.000000e+00, 0.000000e+00,
                                                                                 8.100000e+04,-0.000000e+00,
                                                                                               1.470496e+06,
                proportional, blade_damp;

# BLADE_PITCH + 4:  4.465143e+00 ->  5.473429e+00 m (0.596 -> 0.731 R)
#     x1= 4.678219e+00 xm= 4.969286e+00 x2= 5.260353e+00 (0.625 -> 0.663 -> 0.702 R
beam: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 4,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 8,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 9,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 10,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        # point 1
        # twist=-3.726 deg
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                1,  1.000000e+00, 0.000000e+00, 0.000000e+00,
                2,  0.000000e+00, 9.978862e-01,-6.498495e-02,
        # EA= 1.450000e+08 N EJf= 8.100000e+04 Nm^2 EJl= 1.470496e+06 Nm^2 GJ= 8.500000e+04 Nm^2
        linear viscoelastic generic,
                sym,     1.450000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,-0.000000e+00,
                                       1.450000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                     1.450000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                                   8.500000e+04, 0.000000e+00, 0.000000e+00,
                                                                                 8.100000e+04,-0.000000e+00,
                                                                                               1.470496e+06,
                proportional, blade_damp,
        # point 2
        # twist=-4.313 deg
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                1,  1.000000e+00, 0.000000e+00, 0.000000e+00,
                2,  0.000000e+00, 9.971686e-01,-7.519782e-02,
        # EA= 1.440000e+08 N EJf= 8.100000e+04 Nm^2 EJl= 1.462314e+06 Nm^2 GJ= 8.500000e+04 Nm^2
        linear viscoelastic generic,
                sym,     1.440000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,-0.000000e+00,
                                       1.440000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                     1.440000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                                   8.500000e+04, 0.000000e+00, 0.000000e+00,
                                                                                 8.100000e+04,-0.000000e+00,
                                                                                               1.462314e+06,
                proportional, blade_damp;

# BLADE_PITCH + 5:  5.473429e+00 ->  6.481714e+00 m (0.731 -> 0.865 R)
#     x1= 5.686504e+00 xm= 5.977571e+00 x2= 6.268638e+00 (0.759 -> 0.798 -> 0.837 R
beam: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 5,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 10,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 11,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 12,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        # point 1
        # twist=-4.313 deg
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                1,  1.000000e+00, 0.000000e+00, 0.000000e+00,
                2,  0.000000e+00, 9.971686e-01,-7.519782e-02,
        # EA= 1.440000e+08 N EJf= 8.100000e+04 Nm^2 EJl= 1.462314e+06 Nm^2 GJ= 8.500000e+04 Nm^2
        linear viscoelastic generic,
                sym,     1.440000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,-0.000000e+00,
                                       1.440000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                     1.440000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                                   8.500000e+04, 0.000000e+00, 0.000000e+00,
                                                                                 8.100000e+04,-0.000000e+00,
                                                                                               1.462314e+06,
                proportional, blade_damp,
        # point 2
        # twist=-5.668 deg
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                1,  1.000000e+00, 0.000000e+00, 0.000000e+00,
                2,  0.000000e+00, 9.951102e-01,-9.877071e-02,
        # EA= 1.430000e+08 N EJf= 8.100000e+04 Nm^2 EJl= 1.443421e+06 Nm^2 GJ= 8.500000e+04 Nm^2
        linear viscoelastic generic,
                sym,     1.430000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,-0.000000e+00,
                                       1.430000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                     1.430000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                                   8.500000e+04, 0.000000e+00, 0.000000e+00,
                                                                                 8.100000e+04,-0.000000e+00,
                                                                                               1.443421e+06,
                proportional, blade_damp;

# BLADE_PITCH + 6:  6.481714e+00 ->  7.490000e+00 m (0.865 -> 1.000 R)
#     x1= 6.694790e+00 xm= 6.985857e+00 x2= 7.276924e+00 (0.894 -> 0.933 -> 0.972 R
beam: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 6,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 12,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 13,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        CURR_ROTOR + CURR_BLADE + BLADE_BODY + 14,
        reference, node,
                 0.000000e+00, 0.000000e+00, 0.000000e+00,
        # point 1
        # twist=-5.668 deg
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                1,  1.000000e+00, 0.000000e+00, 0.000000e+00,
                2,  0.000000e+00, 9.951102e-01,-9.877071e-02,
        # EA= 1.430000e+08 N EJf= 8.100000e+04 Nm^2 EJl= 1.443421e+06 Nm^2 GJ= 8.500000e+04 Nm^2
        linear viscoelastic generic,
                sym,     1.430000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,-0.000000e+00,
                                       1.430000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                     1.430000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                                   8.500000e+04, 0.000000e+00, 0.000000e+00,
                                                                                 8.100000e+04,-0.000000e+00,
                                                                                               1.443421e+06,
                proportional, blade_damp,
        # point 2
        # twist=-5.914 deg
        reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
                1,  1.000000e+00, 0.000000e+00, 0.000000e+00,
                2,  0.000000e+00, 9.946776e-01,-1.030366e-01,
        # EA= 1.430000e+08 N EJf= 8.100000e+04 Nm^2 EJl= 1.440000e+06 Nm^2 GJ= 8.700000e+04 Nm^2
        linear viscoelastic generic,
                sym,     1.430000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,-0.000000e+00,
                                       1.430000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                     1.430000e+08, 0.000000e+00, 0.000000e+00, 0.000000e+00,
                                                                   8.700000e+04, 0.000000e+00, 0.000000e+00,
                                                                                 8.100000e+04,-0.000000e+00,
                                                                                               1.440000e+06,
                proportional, blade_damp;


# vim:ft=mbd
