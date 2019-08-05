# --------------------------------------------------------------------------
# Blendyn - file __init__.py
# Copyright (C) 2015 -- 2019 Andrea Zanoni -- andrea.zanoni@polimi.it
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of Blendyn, add-on script for Blender.
#
#    Blendyn is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Blendyn  is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Blendyn.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# -------------------------------------------------------------------------- 
import inspect

bl_info = {
    "name": "Blendyn -- MBDyn physics, Blender graphics",
    "author": "Andrea Zanoni - <andrea.zanoni@polimi.it>",
    "version": (1, 1, 0),
    "blender": (2, 80, 0),
    "location": "View3D -> Properties -> Physics",
    "description": "Imports simulation results of MBDyn (Open Source MultiBody\
    Dynamics solver -- https://www.mbdyn.org/).",
    "wiki_url": "https://github.com/zanoni-mbdyn/blendyn/wiki",
    "bugtracker": "https://github.com/zanoni-mbdyn/blendyn/issues",
    "category": "Animation"}

# if "bpy" in locals():
#    import importlib
#    if "blendyn" in locals():
#        importlib.reload(base)
# else:
#    import bpy
#    from . import blendyn

import bpy
from . blendyn import *

classes = (
        BLENDYN_OT_load_section,
        BLENDYN_OT_import_aerodynamic_body,
        BLENDYN_OT_import_aerodynamic_beam2,
        BLENDYN_OT_import_aerodynamic_beam3,
        BLENDYN_OT_import_angularvelocity,
        BLENDYN_OT_import_angularacceleration,
        BLENDYN_OT_import_axialrot,
        BLENDYN_OT_import_beam2,
        BLENDYN_OT_import_beam3,
        BLENDYN_OT_update_beam3,
        BLENDYN_OT_import_body,
        BLENDYN_OT_import_brake,
        BLENDYN_OT_import_cardano_hinge,
        BLENDYN_OT_import_cardano_pin,
        BLENDYN_OT_import_clamp,
        BLENDYN_OT_import_deformable_displacement,
        BLENDYN_OT_import_distance,
        BLENDYN_OT_import_drive_displacement,
        BLENDYN_OT_import_structural_absolute_force,
        BLENDYN_OT_import_structural_follower_force,
        BLENDYN_OT_import_structural_absolute_couple,
        BLENDYN_OT_import_structural_follower_couple,
        BLENDYN_OT_import_gimbal,
        BLENDYN_OT_import_inline,
        BLENDYN_OT_import_inplane,
        BLENDYN_OT_import_linearvelocity,
        BLENDYN_OT_import_linearacceleration,
        BLENDYN_OT_import_prismatic,
        BLENDYN_OT_import_revolute_hinge,
        BLENDYN_OT_import_revolute_pin,
        BLENDYN_OT_import_revolute_rotation,
        BLENDYN_OT_import_rod,
        BLENDYN_OT_write_rod_input,
        BLENDYN_OT_import_shell4,
        BLENDYN_OT_import_spherical_hinge,
        BLENDYN_OT_import_spherical_pin,
        BLENDYN_OT_import_total,
        BLENDYN_OT_import_total_pin,
        BLENDYN_PT_bevel,
        BLENDYN_OT_import_reference,
        BLENDYN_OT_plot_var_sxx_scene,
        BLENDYN_OT_plot_var_sxx_object,
        BLENDYN_OT_plot_variables_list,
        BLENDYN_OT_plot_var_scene,
        BLENDYN_OT_plot_var_object,
        BLENDYN_OT_set_plot_freq,
        BLENDYN_OT_set_render_variable,
        BLENDYN_OT_delete_render_variable,
        BLENDYN_OT_delete_all_render_variables,
        BLENDYN_OT_show_display_group,
        BLENDYN_OT_set_display_group,
        BLENDYN_PT_object_plot,
        BLENDYN_PT_plot_scene,
        BLENDYN_PG_eigenanalysis,
        BLENDYN_OT_eigen_geometry,
        BLENDYN_OT_animate_eigenmode,
        BLENDYN_PG_elem_pos_offset,
        BLENDYN_PG_elem_rot_offset,
        BLENDYN_PG_nodes_collection,
        BLENDYN_PG_elem_to_be_updated,
        BLENDYN_PG_elems_dictionary,
        BLENDYN_OT_import_elements_as_mesh,
        BLENDYN_PG_nodes_dictionary,
        BLENDYN_PG_refence_dictionary,
        BLENDYN_PG_mbtime,
        BLENDYN_PG_render_vars_dictionary,
        BLENDYN_PG_driver_vars_dictionary,
        BLENDYN_PG_display_vars_dictionary,
        BLENDYN_PG_environment_vars_dictionary,
        BLENDYN_PG_plot_vars,
        BLENDYN_PG_settings_scene,
        BLENDYN_PG_settings_object,
        BLENDYN_OT_standard_import,
        BLENDYN_OT_read_mbdyn_log,
        BLENDYN_OT_select_output_file,
        BLENDYN_OT_assign_labels,
        BLENDYN_OT_clear_data,
        BLENDYN_OT_set_mbdyn_install_path,
        BLENDYN_OT_mbdyn_default_install_path,
        BLENDYN_OT_config_mbdyn_install_path,
        BLENDYN_OT_select_mbdyn_input_file,
        BLENDYN_OT_set_env_variable,
        BLENDYN_OT_delete_env_variable,
        BLENDYN_OT_run_mbdyn_simulation,
        BLENDYN_OT_stop_mbdyn_simulation,
        BLENDYN_OT_set_motion_paths,
        BLENDYN_OT_set_import_freq_auto,
        BLENDYN_OT_set_render_variables,
        BLENDYN_OT_delete_render_variables,
        BLENDYN_OT_delete_all_render_variables,
        BLENDYN_OT_show_display_group,
        BLENDYN_OT_set_display_group,
        BLENDYN_PT_physics,
        BLENDYN_PT_import,
        BLENDYN_PT_animate,
        BLENDYN_PT_simulation,
        BLENDYN_PT_eigenanalysis,
        BLENDYN_PT_active_object,
        BLENDYN_UL_mbdyn_nodes_list,
        BLENDYN_UL_elements_list,
        BLENDYN_UL_render_vars_list,
        BLENDYN_UL_env_vars_list,
        BLENDYN_UL_refs_lists,
        BLENDYN_PT_nodes_scene,
        BLENDYN_PT_elems_scene,
        BLENDYN_PT_scaling,
        BLENDYN_PT_reference_scene,
        BLENDYN_PT_obj_select,
        BLENDYN_OT_node_import_all,
        BLENDYN_OT_single_node_import,
        BLENDYN_OT_references_import_all,
        BLENDYN_OT_references_import_single,
        BLENDYN_OT_select_all_nodes,
        BLENDYN_OT_select_elements_by_type,
        BLENDYN_OT_scale_node,
        BLENDYN_OT_scale_sel_nodes,
        BLENDYN_OT_scale_elements_by_type,
        BLENDYN_OT_import_elements_by_type,
        BLENDYN_OT_elements_import_all,
        BLENDYN_OT_obj_select_node,
        BLENDYN_OT_create_vertices_from_nodes,
        BLENDYN_OT_delete_override
)

register, unregister = bpy.utils.register_classes_factory(classes)
