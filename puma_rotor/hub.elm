# Dynamics and Aeroelasticity of Rotors 
# MBDyn training #2
# Introduction to rotor dynamics with MBDyn
# author Giuseppe Quaranta <giuseppe.quaranta@polimi.it>
# This is part of the MBDyn model of the AS330 Puma
# vim: ft=mbd


   	joint: CURR_ROTOR + HUB, axial rotation,
                BASE_BODY,
                        position, reference, CURR_ROTOR, null,
                        orientation, reference, CURR_ROTOR, eye,
                CURR_ROTOR + HUB,
                        position, reference, CURR_ROTOR, null,
                        orientation, reference, CURR_ROTOR, eye,
                const, omega;

        /*
        joint: CURR_ROTOR + HUB, total joint,
                BASE_BODY,
                        position, reference, CURR_ROTOR, null,
                        position orientation, reference,CURR_ROTOR, eye,
                        rotation orientation, reference,CURR_ROTOR, eye,
                CURR_ROTOR + HUB,
                        position, reference,CURR_ROTOR, RF_hub, null,
                        position orientation, reference,CURR_ROTOR, eye,
                        rotation orientation, reference,CURR_ROTOR, eye,
                position constraint, 1, 1, 1, null,
                orientation constraint, 1, 1, 1,
                        0., 0., 1., linear, 0., omega;

        */

 	#fixed swashplate constraints
	joint: CURR_ROTOR + SWASHPLATE_FIXED, total joint,
		BASE_BODY,
			position, reference, CURR_ROTOR + SWASHPLATE_FIXED, null,
			position orientation, reference, CURR_ROTOR + SWASHPLATE_FIXED, eye,
			rotation orientation, reference, CURR_ROTOR + SWASHPLATE_FIXED, eye,
		CURR_ROTOR + SWASHPLATE_FIXED,
			position, reference, CURR_ROTOR + SWASHPLATE_FIXED, null,
			position orientation, reference, CURR_ROTOR + SWASHPLATE_FIXED, eye,
			rotation orientation, reference, CURR_ROTOR + SWASHPLATE_FIXED, eye,
		position constraint, 1, 1, 1,
			component, 
				0., 
				0.,
				cosine, (2./omega_h), pi/(5./omega_h), 1/coll_pitch_tau * theta_coll/2., half, 0.,
		orientation constraint, 1, 1, 1,
			component,
				cosine, (2./omega_h), pi/(5./omega_h), theta_fore_aft/2./1.90358, half, 0.,
				cosine, (2./omega_h), pi/(5./omega_h), theta_lateral/2./1.90358, half, 0.,
				0.;

		/*	component,
				0.,
				0.,
				node, SW_ACTUATOR_COLLECTIVE, abstract, string, "x", linear, 0., -l_pitch_link_y,
		orientation constraint, 1, 1, 1,
			component,
				node, SW_ACTUATOR_FORE_AFT, abstract, string, "x", linear, 0., -l_pitch_link_y/l_pitch_link_x/1.20, # note: empirical correction 1/1.20
				node, SW_ACTUATOR_LATERAL, abstract, string, "x", linear, 0., -l_pitch_link_y/l_pitch_link_x/1.20,
				0.;
		*/

	joint: CURR_ROTOR + SWASHPLATE_ROTATING, revolute hinge,
		CURR_ROTOR + SWASHPLATE_FIXED,
			position, reference, CURR_ROTOR + SWASHPLATE_FIXED, null,
			orientation, reference, CURR_ROTOR + SWASHPLATE_FIXED, eye,
		CURR_ROTOR + SWASHPLATE_ROTATING,
			position, reference, CURR_ROTOR + SWASHPLATE_FIXED, null,
			orientation, reference, CURR_ROTOR + SWASHPLATE_FIXED, eye;

	joint: CURR_ROTOR + SWASHPLATE_ROTATING + 1, total joint,
		CURR_ROTOR + HUB,
			position, reference, CURR_ROTOR + SWASHPLATE_ROTATING, null,
			position orientation, reference, CURR_ROTOR + SWASHPLATE_ROTATING, eye,
			rotation orientation, reference, CURR_ROTOR + SWASHPLATE_ROTATING, eye,
		CURR_ROTOR + SWASHPLATE_ROTATING,
			position, reference, CURR_ROTOR + SWASHPLATE_ROTATING, null,
			position orientation, reference, CURR_ROTOR + SWASHPLATE_ROTATING, eye,
			rotation orientation, reference, CURR_ROTOR + SWASHPLATE_ROTATING, eye,
		position constraint, 0, 0, 0, null,
		orientation constraint, 0, 0, 1, null;

	/*
	genel: CURR_ROTOR + HUB, state space MIMO,
		3,
			CURR_ROTOR + SW_ACTUATOR_COLLECTIVE, abstract, algebraic,
			CURR_ROTOR + SW_ACTUATOR_FORE_AFT, abstract, algebraic,
			CURR_ROTOR + SW_ACTUATOR_LATERAL, abstract, algebraic,
		3,
			nodedof, CURR_ROTOR + SW_COLLECTIVE, abstract, algebraic,
			nodedof, CURR_ROTOR + SW_FORE_AFT, abstract, algebraic,
			nodedof, CURR_ROTOR + SW_LATERAL, abstract, algebraic,
		3,
		matrix A,
			-1./rotor_tau,       0.,                 0.,
		 	 0.,                -1./rotor_tau,       0.,
		 	 0.,                 0.,                -1./rotor_tau,
		matrix B,
			1./rotor_tau,  	     0.,                 0.,
		 	0.,                  1./rotor_tau,       0.,
		 	0.,                  0.,                 1./rotor_tau,
		matrix C,
			1., 0., 0.,
			0., 1., 0.,
			0., 0., 1.;

	genel: CURR_ROTOR + HUB + 1, spring support,
		CURR_ROTOR + SW_COLLECTIVE, abstract, algebraic,
		linear elastic, 1.;

	genel: CURR_ROTOR +  HUB + 2, spring support,
		CURR_ROTOR + SW_FORE_AFT, abstract, algebraic,
		linear elastic, 1.;

	genel: CURR_ROTOR + HUB + 3, spring support,
		CURR_ROTOR + SW_LATERAL, abstract, algebraic,
		linear elastic, 1.;
	
	*/
# vim:ft=mbd
