import bpy  # Define a custom panel in the N-Panel

class GP_TO_CURVE_PT_Panel(bpy.types.Panel):
    bl_label = "GP to Curves"
    bl_idname = "GP_TO_CURVE_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Edit'

    def draw(self, context):
        layout = self.layout
        props = context.scene.gpto_curve_properties

        # --- SIMPLIFY MODIFIER UI ---
        #layout.label(text="Grease Pencil Simplify")
        row = layout.row()
        #layout.prop(props, "simplify_mode", text="Mode")
        #layout.prop(props, "simplify_steps", text="Steps")
        layout.operator("object.gpto_add_simplify_modifier", text="Add Simplify Modifier")

        layout.separator()

        # --- SMOOTH MODIFIER UI ---
        #layout.label(text="Grease Pencil Smoothing")
        row = layout.row()
        op = row.operator("object.gpto_add_smooth_modifier", text="Add Smooth Modifier")
        op.smooth_factor = 0.5
        op.smooth_steps = 12

        layout.separator()
        layout.label(text="IMPORTANT: Apply modifiers")
        layout.label(text="before converting to curve")
        layout.separator()

        layout.prop(props, "spline_type", text="Spline Type")
        layout.prop(props, "decimate_ratio", text="Decimate Ratio")
        layout.separator()

        layout.operator("object.gpto_simple_curve_convert", text="Convert GP to Curve")
        layout.separator()  


        # New UI elements for resampling
        layout.separator()
        layout.prop(props, "resample_amount", text="Resample Amount")
        layout.operator("object.gpto_simple_curve_resample", text="Resample Curve")

        layout.separator()
        layout.prop_search(props, "surface_target", bpy.data, "objects", text="Surface")
        layout.prop(props, "snap_to_surface", text="Snap Curves to Surface")

        if props.surface_target and props.surface_target.type == 'MESH':
            uv_map_names = [uv.name for uv in props.surface_target.data.uv_layers]
            layout.prop(props, "surface_uv_map", text="UV Map", icon='GROUP_UVS')
            if props.surface_uv_map not in uv_map_names:
                layout.label(text="Type in a valid UV Map", icon='ERROR')

        layout.operator("object.gpto_simple_curve_hair_prep", text="Hair Prep")


# Register and Unregister functions
def register():
    bpy.utils.register_class(GP_TO_CURVE_PT_Panel)

def unregister():
    bpy.utils.unregister_class(GP_TO_CURVE_PT_Panel)
