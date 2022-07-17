bl_info = {
    "name": "Blendyn",
    "category": "Physics",
    "blender": (2, 80, 0),
    "author": "Andrea Zanoni - <andrea.zanoni@polimi.it>",
    "location": "View3D -> Properties -> Physics",
    "description": "Imports simulation results of MBDyn (Open Source MultiBody\
    Dynamics solver -- https://www.mbdyn.org/).",
    "wiki_url": "https://github.com/zanoni-mbdyn/blendyn/wiki",
    "bugtracker": "https://github.com/zanoni-mbdyn/blendyn/issues"
}

import bpy
from . utilslib     import *
from . aerolib      import *
from . angularjlib  import *
from . axialrotjlib import *
from . beamlib      import *
from . beamsliderlib import *
from . bodylib      import *
from . brakejlib    import *
from . carjlib      import *
from . clampjlib    import *
from . defdispjlib  import *
from . drivejlib    import *
from . forcelib     import *
from . gimbaljlib   import *
from . inlinejlib   import *
from . inplanejlib  import *
from . linearjlib   import *
from . modallib     import *
from . prismjlib    import *
from . revjlib      import *
from . rodjlib      import *
from . shell4lib    import *
from . membrane4lib import *
from . sphjlib      import *
from . totjlib      import *
from . elementlib   import *
from . logwatcher   import *
from . nodelib      import *
from . eigenlib     import *
from . elements     import *
from . components   import *
from . baselib      import *
from . matplotlib   import *
from . pygalplotlib import *
from . bokehplotlib import *
from . plotlib      import *
from . blendyn      import *

classes = (
        BLENDYN_OT_install_dependencies,
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
        BLENDYN_OT_import_beam_slider,
        BLENDYN_OT_import_modal,
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
        BLENDYN_OT_import_membrane4,
        BLENDYN_OT_import_spherical_hinge,
        BLENDYN_OT_import_spherical_pin,
        BLENDYN_OT_import_total,
        BLENDYN_OT_import_total_pin,
        BLENDYN_PT_bevel,
        BLENDYN_OT_import_reference,
        BLENDYN_OT_mplot_var_scene,
        BLENDYN_OT_mplot_var_object,
        BLENDYN_OT_mplot_variables_list,
        BLENDYN_OT_mplot_var_sxx_scene,
        BLENDYN_OT_mplot_var_sxx_object,
        BLENDYN_OT_mplot_trajectory_object,
        BLENDYN_OT_mplot_trajectory_scene,
        BLENDYN_OT_bplot_var_scene,
        BLENDYN_OT_bplot_var_object,
        BLENDYN_OT_bplot_variables_list,
        BLENDYN_OT_bplot_var_sxx_scene,
        BLENDYN_OT_bplot_var_sxx_object,
        BLENDYN_OT_bplot_trajectory_object,
        BLENDYN_OT_bplot_trajectory_scene,
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
        BLENDYN_OT_eigen_geometry,
        BLENDYN_OT_animate_eigenmode,
        BLENDYN_OT_import_elements_as_mesh,
        BLENDYN_OT_standard_import,
        BLENDYN_OT_read_mbdyn_log_file,
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
        BLENDYN_OT_component_add,
        BLENDYN_OT_component_edit,
        BLENDYN_OT_component_remove,
        BLENDYN_OT_component_add_confirm,
        BLENDYN_OT_component_edit_confirm,
        BLENDYN_OT_component_add_cancel,
        BLENDYN_OT_component_edit_cancel,
        BLENDYN_OT_component_add_elem,
        BLENDYN_OT_component_remove_elem,
        BLENDYN_OT_component_remove_all_elems,
        BLENDYN_OT_component_add_selected_elems,
        BLENDYN_OT_element_add_node,
        BLENDYN_OT_element_add_all_selected_nodes,
        BLENDYN_OT_element_remove_node,
        BLENDYN_OT_element_remove_all_nodes,
        BLENDYN_OT_element_add_new_connect,
        BLENDYN_OT_element_remove_connect,
        BLENDYN_OT_element_remove_all_connects,
        BLENDYN_preferences,
        BLENDYN_PT_import,
        BLENDYN_PT_animate,
        BLENDYN_PT_simulation,
        BLENDYN_PT_eigenanalysis,
        BLENDYN_PT_components,
        BLENDYN_PT_active_object,
        BLENDYN_PT_nodes_scene,
        BLENDYN_PT_elems_scene,
        BLENDYN_PT_reference_scene,
        BLENDYN_PT_plot_scene,
        BLENDYN_PT_obj_select,
        BLENDYN_OT_node_import_all,
        BLENDYN_OT_node_import_single,
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
        BLENDYN_OT_delete_override,
        BLENDYN_OT_outline_collapse,
        BLENDYN_OT_outline_expand,
        BLENDYN_PT_utilities
)

register, unregister_fact = bpy.utils.register_classes_factory(classes)

def unregister():
    bpy.utils.unregister_class(BLENDYN_PG_elems_dictionary)
    bpy.utils.unregister_class(BLENDYN_PG_elem_to_be_updated)
    bpy.utils.unregister_class(BLENDYN_PG_nodes_collection)
    bpy.utils.unregister_class(BLENDYN_PG_elem_rot_offset)
    bpy.utils.unregister_class(BLENDYN_PG_elem_pos_offset)
    bpy.utils.unregister_class(BLENDYN_PG_eigenanalysis)
    bpy.utils.unregister_class(BLENDYN_PG_render_vars_dictionary)
    bpy.utils.unregister_class(BLENDYN_PG_settings_object)
    bpy.utils.unregister_class(BLENDYN_PG_settings_scene)
    bpy.utils.unregister_class(BLENDYN_PG_plot_vars)
    bpy.utils.unregister_class(BLENDYN_PG_environment_vars_dictionary)
    bpy.utils.unregister_class(BLENDYN_PG_display_vars_dictionary)
    bpy.utils.unregister_class(BLENDYN_PG_driver_vars_dictionary)
    bpy.utils.unregister_class(BLENDYN_PG_mbtime)
    bpy.utils.unregister_class(BLENDYN_PG_reference_dictionary)
    bpy.utils.unregister_class(BLENDYN_PG_nodes_dictionary)
    bpy.utils.unregister_class(BLENDYN_PG_components_dictionary)
    bpy.utils.unregister_class(BLENDYN_PG_component_element)
    bpy.utils.unregister_class(BLENDYN_UL_env_vars_list)
    bpy.utils.unregister_class(BLENDYN_UL_mbdyn_nodes_list)
    bpy.utils.unregister_class(BLENDYN_UL_elements_list)
    bpy.utils.unregister_class(BLENDYN_UL_refs_list)
    bpy.utils.unregister_class(BLENDYN_UL_render_vars_list)
    bpy.utils.unregister_class(BLENDYN_UL_object_plot_var_list)
    bpy.utils.unregister_class(BLENDYN_UL_plot_var_list)
    bpy.utils.unregister_class(BLENDYN_UL_component_object_list)
    bpy.utils.unregister_class(BLENDYN_UL_components_list)
    bpy.utils.unregister_class(BLENDYN_UL_component_elements_list) 
    unregister_fact()
