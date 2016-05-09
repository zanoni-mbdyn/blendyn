# Dynamics and Aeroelasticity of Rotors 
# MBDyn training #2
# Introduction to rotor dynamics with MBDyn
# author Giuseppe Quaranta <giuseppe.quaranta@polimi.it>
# This is part of the MBDyn model of the AS330 Puma
# vim: ft=mbd

	# lag hinge
	joint: CURR_ROTOR + CURR_BLADE + BLADE_LAG, revolute hinge,
       		CURR_ROTOR + CURR_BLADE + BLADE_LAG ,
                	reference, CURR_ROTOR + CURR_BLADE + BLADE_LAG, null,
                	hinge, reference, CURR_ROTOR + CURR_BLADE + BLADE_LAG, eye,
        	CURR_ROTOR + HUB,
                	reference, CURR_ROTOR + CURR_BLADE + BLADE_LAG, null,
                	hinge, reference, CURR_ROTOR + CURR_BLADE + BLADE_LAG, eye;

	# lag hinge damper 
	joint: CURR_ROTOR + CURR_BLADE + BLADE_LAG + 1, deformable hinge,
        	CURR_ROTOR + CURR_BLADE + BLADE_LAG ,
                	hinge, reference, CURR_ROTOR + CURR_BLADE + BLADE_LAG, eye,
        	CURR_ROTOR + HUB,
                	hinge, reference, CURR_ROTOR + CURR_BLADE + BLADE_LAG, eye,
        	linear viscoelastic, lead_lag_stiffness, lead_lag_damping;
        	# linear time variant viscoelastic generic, null, 0., diag, 0., 0., 7000., cosine, 8., pi/1., -.5, half, 1.; # WARNING: zero out damping


	# flap hinge
	joint: CURR_ROTOR + CURR_BLADE + BLADE_FLAP, revolute hinge,
        	CURR_ROTOR + CURR_BLADE + BLADE_FLAP,
               		reference, CURR_ROTOR + CURR_BLADE + BLADE_FLAP, null,
                	hinge, reference, CURR_ROTOR +  CURR_BLADE + BLADE_FLAP,
				1, 1.,  0., 0.,
				3, 0., -1., 0., 
        	CURR_ROTOR + CURR_BLADE + BLADE_LAG,
                	reference, CURR_ROTOR + CURR_BLADE + BLADE_FLAP, null,
                	hinge, reference, CURR_ROTOR + CURR_BLADE + BLADE_FLAP, 
				1, 1.,  0., 0.,
				3, 0., -1., 0.; 

	# flap hinge stiffness 
	joint: CURR_ROTOR + CURR_BLADE + BLADE_FLAP + 1, deformable hinge,
        	CURR_ROTOR + CURR_BLADE + BLADE_FLAP,
                	hinge, reference, CURR_ROTOR + CURR_BLADE + BLADE_FLAP, eye,
        	CURR_ROTOR + HUB,
                	hinge, reference, CURR_ROTOR + CURR_BLADE + BLADE_FLAP, eye,
        	linear viscoelastic, flap_stiffness, flap_damping;
	
	# pitch bearing
	joint: CURR_ROTOR + CURR_BLADE + BLADE_PITCH, revolute hinge,
        	CURR_ROTOR + CURR_BLADE + BLADE_BODY,
                	reference, CURR_ROTOR +  CURR_BLADE + BLADE_PITCH, null,
                	hinge, reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
				2, 0., 1., 0.,
				3, 1., 0., 0., 
        	CURR_ROTOR + CURR_BLADE + BLADE_FLAP,
                	reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, null,
                	hinge, reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH,
				2, 0., 1., 0.,
				3, 1., 0., 0.; 

	 # flexible pitch link
	joint: CURR_ROTOR + CURR_BLADE + PITCH_LINK, rod with offset,
		CURR_ROTOR + CURR_BLADE + BLADE_BODY,
			reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, 
				-pitch_bearing + pitch_link_x,
				pitch_link_y,
				0.,
		CURR_ROTOR + SWASHPLATE_ROTATING,
			reference, CURR_ROTOR + CURR_BLADE,
				pitch_link_x,
				pitch_link_y,
				-pitch_link_length,
		pitch_link_length,
		linear viscoelastic, pitch_link_stiffness, proportional, pitch_link_dampingf;


	/*	
	 # rigid pitch link
	joint: CURR_ROTOR + CURR_BLADE + PITCH_LINK, distance with offset,
		CURR_ROTOR + CURR_BLADE + BLADE_BODY,
			reference, CURR_ROTOR + CURR_BLADE + BLADE_PITCH, 
				-pitch_bearing + pitch_link_x,
				pitch_link_y,
				0.,
		CURR_ROTOR + SWASHPLATE_ROTATING,
			reference, CURR_ROTOR + CURR_BLADE,
				pitch_link_x,
				pitch_link_y,
				-pitch_link_length,
		pitch_link_length;

	*/
# vim: ft=mbd
