# BLADE_PITCH + 0:  4.320000e-01 ->  9.361429e-01 ->  1.440286e+00 m (0.058 -> 0.125 -> 0.192 R)
aerodynamic beam: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 0,
  CURR_ROTOR + CURR_BLADE + BLADE_BODY + 0,
  induced velocity, CURR_ROTOR,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: 0.00 deg
          1,  0.000000e+00,  1.000000e+00,  0.000000e+00,
          2,  0.000000e+00, -0.000000e+00,  1.000000e+00,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: 0.00 deg
          1,  0.000000e+00,  1.000000e+00,  0.000000e+00,
          2,  0.000000e+00, -0.000000e+00,  1.000000e+00,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: 0.00 deg
          1,  0.000000e+00,  1.000000e+00,  0.000000e+00,
          2,  0.000000e+00, -0.000000e+00,  1.000000e+00,
  const, 0.,
  const, 0.,
  const, 0.,
  const, 0.,
  integration_points,
  c81, NACA0012,
  #theodorsen, c81, NACA0012,
  jacobian, aero_jacobian;

# BLADE_PITCH + 1:  1.440286e+00 ->  1.944429e+00 ->  2.448571e+00 m (0.192 -> 0.260 -> 0.327 R)
aerodynamic beam: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 1,
  CURR_ROTOR + CURR_BLADE + BLADE_BODY + 1,
  induced velocity, CURR_ROTOR,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: 0.00 deg
          1,  0.000000e+00,  1.000000e+00,  0.000000e+00,
          2,  0.000000e+00, -0.000000e+00,  1.000000e+00,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -0.05 deg
          1,  0.000000e+00,  9.999996e-01, -8.716672e-04,
          2,  0.000000e+00,  8.716672e-04,  9.999996e-01,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -0.53 deg
          1,  0.000000e+00,  9.999570e-01, -9.275604e-03,
          2,  0.000000e+00,  9.275604e-03,  9.999570e-01,
  piecewise linear, 4,
          -1.000000e+00, 0.,
           2.689146e-01, 0.,
           2.689148e-01, blade_chord,
           1.000000e+00, blade_chord,
  const, 0.,
  piecewise linear, 4,
          -1.000000e+00, 0.,
           2.689146e-01, 0.,
           2.689148e-01, -blade_chord/2.,
           1.000000e+00, -blade_chord/2.,
  const, 0.,
  integration_points,
  c81, NACA0012,
  #theodorsen, c81, NACA0012,
  jacobian, aero_jacobian;

# BLADE_PITCH + 2:  2.448571e+00 ->  2.952714e+00 ->  3.456857e+00 m (0.327 -> 0.394 -> 0.462 R)
aerodynamic beam: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 2,
  CURR_ROTOR + CURR_BLADE + BLADE_BODY + 2,
  induced velocity, CURR_ROTOR,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -0.54 deg
          1,  0.000000e+00,  9.999551e-01, -9.475470e-03,
          2,  0.000000e+00,  9.475470e-03,  9.999551e-01,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -1.21 deg
          1,  0.000000e+00,  9.997755e-01, -2.118960e-02,
          2,  0.000000e+00,  2.118960e-02,  9.997755e-01,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -1.81 deg
          1,  0.000000e+00,  9.994991e-01, -3.164662e-02,
          2,  0.000000e+00,  3.164662e-02,  9.994991e-01,
  const, blade_chord,
  const, 0.,
  const, -blade_chord/2.,
  const, 0.,
  integration_points,
  c81, NACA0012,
  #theodorsen, c81, NACA0012,
  jacobian, aero_jacobian;

# BLADE_PITCH + 3:  3.456857e+00 ->  3.961000e+00 ->  4.465143e+00 m (0.462 -> 0.529 -> 0.596 R)
aerodynamic beam: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 3,
  CURR_ROTOR + CURR_BLADE + BLADE_BODY + 3,
  induced velocity, CURR_ROTOR,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -1.81 deg
          1,  0.000000e+00,  9.994992e-01, -3.164534e-02,
          2,  0.000000e+00,  3.164534e-02,  9.994992e-01,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -2.35 deg
          1,  0.000000e+00,  9.991581e-01, -4.102487e-02,
          2,  0.000000e+00,  4.102487e-02,  9.991581e-01,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -2.89 deg
          1,  0.000000e+00,  9.987291e-01, -5.039951e-02,
          2,  0.000000e+00,  5.039951e-02,  9.987291e-01,
  const, blade_chord,
  const, 0.,
  const, -blade_chord/2.,
  const, 0.,
  integration_points,
  c81, NACA0012,
  #theodorsen, c81, NACA0012,
  jacobian, aero_jacobian;

# BLADE_PITCH + 4:  4.465143e+00 ->  4.969286e+00 ->  5.473429e+00 m (0.596 -> 0.663 -> 0.731 R)
aerodynamic beam: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 4,
  CURR_ROTOR + CURR_BLADE + BLADE_BODY + 4,
  induced velocity, CURR_ROTOR,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -2.89 deg
          1,  0.000000e+00,  9.987291e-01, -5.039951e-02,
          2,  0.000000e+00,  5.039951e-02,  9.987291e-01,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -3.43 deg
          1,  0.000000e+00,  9.982122e-01, -5.976971e-02,
          2,  0.000000e+00,  5.976971e-02,  9.982122e-01,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -3.96 deg
          1,  0.000000e+00,  9.976073e-01, -6.913464e-02,
          2,  0.000000e+00,  6.913464e-02,  9.976073e-01,
  const, blade_chord,
  const, 0.,
  const, -blade_chord/2.,
  const, 0.,
  integration_points,
  c81, NACA0012,
  #theodorsen, c81, NACA0012,
  jacobian, aero_jacobian;

# BLADE_PITCH + 5:  5.473429e+00 ->  5.977571e+00 ->  6.481714e+00 m (0.731 -> 0.798 -> 0.865 R)
aerodynamic beam: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 5,
  CURR_ROTOR + CURR_BLADE + BLADE_BODY + 5,
  induced velocity, CURR_ROTOR,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -3.96 deg
          1,  0.000000e+00,  9.976073e-01, -6.913464e-02,
          2,  0.000000e+00,  6.913464e-02,  9.976073e-01,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -4.50 deg
          1,  0.000000e+00,  9.969146e-01, -7.849349e-02,
          2,  0.000000e+00,  7.849349e-02,  9.969146e-01,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -5.04 deg
          1,  0.000000e+00,  9.961336e-01, -8.785160e-02,
          2,  0.000000e+00,  8.785160e-02,  9.961336e-01,
  const, blade_chord,
  const, 0.,
  const, -blade_chord/2.,
  const, 0.,
  integration_points,
  c81, NACA0012,
  #theodorsen, c81, NACA0012,
  jacobian, aero_jacobian;

# BLADE_PITCH + 6:  6.481714e+00 ->  6.985857e+00 ->  7.490000e+00 m (0.865 -> 0.933 -> 1.000 R)
aerodynamic beam: CURR_ROTOR + CURR_BLADE + BLADE_BODY + 6,
  CURR_ROTOR + CURR_BLADE + BLADE_BODY + 6,
  induced velocity, CURR_ROTOR,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -5.04 deg
          1,  0.000000e+00,  9.961336e-01, -8.785160e-02,
          2,  0.000000e+00,  8.785160e-02,  9.961336e-01,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -5.58 deg
          1,  0.000000e+00,  9.952639e-01, -9.720964e-02,
          2,  0.000000e+00,  9.720964e-02,  9.952639e-01,
  reference, node,
           0.000000e+00,  0.000000e+00,  0.000000e+00,
  reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, # twist: -6.12 deg
          1,  0.000000e+00,  9.943064e-01, -1.065591e-01,
          2,  0.000000e+00,  1.065591e-01,  9.943064e-01,
  const, blade_chord,
  const, 0.,
  const, -blade_chord/2.,
  const, 0.,
  integration_points,
  c81, NACA0012,
  #theodorsen, c81, NACA0012,
  jacobian, aero_jacobian;


# vim:ft=mbd
