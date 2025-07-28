import bpy
from .properties import GPToCurveProperties

# -----------------------------------------------------------------
# 1) Operator: Add a Simplify Modifier to the active GP object
# -----------------------------------------------------------------
class GPTO_SIMPLE_CURVE_OT_AddSimplifyModifier(bpy.types.Operator):
    bl_idname = "object.gpto_add_simplify_modifier"
    bl_label = "Simplify Stroke"
    bl_description = "Add a Grease Pencil Simplify modifier to the active Grease Pencil object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Access the properties set by the user in the UI
        props = context.scene.gpto_curve_properties

        # Use default values if the properties are not set
        simplify_mode = props.simplify_mode if props.simplify_mode else 'FIXED'
        simplify_steps = props.simplify_steps if props.simplify_steps > 0 else 2

        gp_obj = context.active_object
        if not gp_obj or gp_obj.type != 'GREASEPENCIL':
            self.report({'WARNING'}, "Active object is not a Grease Pencil!")
            return {'CANCELLED'}

        # Add a Simplify modifier to the active Grease Pencil object
        simplify_mod = gp_obj.modifiers.new(name="GP_Simplify", type='GREASE_PENCIL_SIMPLIFY')
        simplify_mod.mode = simplify_mode
        simplify_mod.step = simplify_steps

        self.report({'INFO'}, f"Grease Pencil Simplify modifier added (mode={simplify_mode}, steps={simplify_steps}).")
        return {'FINISHED'}

# -----------------------------------------------------------------
# 2) Operator: Add a Smooth Modifier to the active GP object
# -----------------------------------------------------------------
class GPTO_SIMPLE_CURVE_OT_AddSmoothModifier(bpy.types.Operator):
    bl_idname = "object.gpto_add_smooth_modifier"
    bl_label = "Add GP Smooth Modifier"
    bl_description = "Add a live Grease Pencil Smooth modifier to the active Grease Pencil object"
    bl_options = {'REGISTER', 'UNDO'}

    smooth_factor: bpy.props.FloatProperty(
        name="Smooth Factor",
        default=0.5,
        min=0.0,
        max=10.0
    )
    smooth_steps: bpy.props.IntProperty(
        name="Smooth Steps",
        default=12,
        min=1,
        max=50
    )

    def execute(self, context):
        gp_obj = context.active_object
        if not gp_obj or gp_obj.type != 'GREASEPENCIL':
            self.report({'WARNING'}, "Active object is not a Grease Pencil!")
            return {'CANCELLED'}

        # Add a Smooth modifier
        smooth_mod = gp_obj.modifiers.new(name="GP_Smooth", type='GREASE_PENCIL_SMOOTH')
        smooth_mod.factor = self.smooth_factor
        smooth_mod.step = self.smooth_steps

        self.report({'INFO'}, f"Grease Pencil Smooth modifier added (factor={self.smooth_factor}, steps={self.smooth_steps}).")
        return {'FINISHED'}

# Operator to convert GP to Curve
class GPTO_SIMPLE_CURVE_OT_Convert(bpy.types.Operator):
    bl_idname = "object.gpto_simple_curve_convert"
    bl_label = "Convert GP to Curve"
    bl_options = {'REGISTER', 'UNDO'}

    def add_and_apply_modifiers(self, gpencil, smooth_factor, smooth_step):
        if gpencil.type == 'GREASEPENCIL':
            bpy.ops.object.mode_set(mode='OBJECT')

    def new_convert_curve_object(self, collection, name):
        curve = bpy.data.curves.new(name=name, type="CURVE")
        curve.dimensions = "3D"
        convert_object = bpy.data.objects.new(name=name, object_data=curve)
        collection.objects.link(convert_object)
        return convert_object

    def convert_gpencil_to_curve(self, gpencil_object):
        gp_col = gpencil_object.users_collection[0] if gpencil_object.users_collection else bpy.context.scene.collection
        gp_data = gpencil_object.data
        curve_objects = []

        # Get the transformation matrix of the Grease Pencil object
        gp_matrix = gpencil_object.matrix_world

        for layer in gp_data.layers:
            if layer.hide:
                continue

            obj = self.new_convert_curve_object(gp_col, f"{gpencil_object.name}_curve_{layer.name}")

            for frame in layer.frames:
                if not frame.drawing:  # Skip frames without drawings
                    continue

                for stroke in frame.drawing.strokes:
                    if not stroke.points:
                        continue
                    spline = obj.data.splines.new(type="POLY")
                    spline.points.add(len(stroke.points) - 1)
                    for i, point in enumerate(stroke.points):
                        # Convert point position to world space
                        world_position = gp_matrix @ point.position
                        spline.points[i].co = (world_position[0], world_position[1], world_position[2], 1.0)
            curve_objects.append(obj)

        return curve_objects

    def convert_curve_to_bezier_and_decimate(self, curve_object, decimate_ratio, spline_type):
        bpy.context.view_layer.objects.active = curve_object
        curve_object.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')

        bpy.ops.curve.spline_type_set(type='BEZIER', use_handles=True)
        bpy.ops.curve.decimate(ratio=decimate_ratio)

        if spline_type == 'BEZIER_TO_POLY':
            bpy.ops.curve.spline_type_set(type='POLY')

        bpy.ops.object.mode_set(mode='OBJECT')

    def execute(self, context):
        props = context.scene.gpto_curve_properties
        gpencil = context.active_object

        if gpencil and gpencil.type == 'GREASEPENCIL':
            #self.add_and_apply_modifiers(gpencil, props.smooth_factor, props.smooth_step)
            gpencil.hide_set(True)
            curve_objects = self.convert_gpencil_to_curve(gpencil)

            last_curve_obj = None
            for curve_object in curve_objects:
                if props.spline_type == 'BEZIER' or props.spline_type == 'BEZIER_TO_POLY':
                    self.convert_curve_to_bezier_and_decimate(curve_object, props.decimate_ratio, props.spline_type)
                last_curve_obj = curve_object

            if last_curve_obj:
                context.view_layer.objects.active = last_curve_obj
                last_curve_obj.select_set(True)

            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No active grease pencil object selected")
            return {'CANCELLED'}


# Operator for Resample
class GPTO_SIMPLE_CURVE_OT_Resample(bpy.types.Operator):
    bl_idname = "object.gpto_simple_curve_resample"
    bl_label = "Resample Curve"
    bl_description = "Resample the active curve to a specified number of points"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.gpto_curve_properties
        curve_obj = context.active_object

        if not curve_obj or curve_obj.type != 'CURVE':
            self.report({'WARNING'}, "Active object is not a curve")
            return {'CANCELLED'}
        
        # Resampling the curve
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.decimate(ratio=1.0)  # Ensure decimate is in ratio mode
        bpy.ops.curve.subdivide(number_cuts=props.resample_amount - 1)
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


# Operator for Hair Prep
class GPTO_SIMPLE_CURVE_OT_HairPrep(bpy.types.Operator):
    bl_idname = "object.gpto_simple_curve_hair_prep"
    bl_label = "Hair Prep"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.gpto_curve_properties
        curve_obj = context.active_object

        if not curve_obj or curve_obj.type != 'CURVE':
            self.report({'WARNING'}, "Active object is not a curve")
            return {'CANCELLED'}

        # Convert the curve spline type to 'CURVES'
        bpy.ops.object.convert(target='CURVES')

        if curve_obj.type == 'CURVES':
            curve_obj.data.surface = props.surface_target
            curve_obj.data.surface_uv_map = props.surface_uv_map

        if props.snap_to_surface:
            bpy.ops.curves.snap_curves_to_surface(attach_mode='NEAREST')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(GPTO_SIMPLE_CURVE_OT_AddSimplifyModifier)
    bpy.utils.register_class(GPTO_SIMPLE_CURVE_OT_AddSmoothModifier)
    bpy.utils.register_class(GPTO_SIMPLE_CURVE_OT_Convert)
    bpy.utils.register_class(GPTO_SIMPLE_CURVE_OT_Resample)
    bpy.utils.register_class(GPTO_SIMPLE_CURVE_OT_HairPrep)

def unregister():
    bpy.utils.unregister_class(GPTO_SIMPLE_CURVE_OT_AddSimplifyModifier)
    bpy.utils.unregister_class(GPTO_SIMPLE_CURVE_OT_AddSmoothModifier)
    bpy.utils.unregister_class(GPTO_SIMPLE_CURVE_OT_Convert)
    bpy.utils.unregister_class(GPTO_SIMPLE_CURVE_OT_Resample)
    bpy.utils.unregister_class(GPTO_SIMPLE_CURVE_OT_HairPrep)
