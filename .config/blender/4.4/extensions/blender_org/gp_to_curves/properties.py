import bpy

# Define a property group
class GPToCurveProperties(bpy.types.PropertyGroup):
    spline_type_items = [
        ('CURVE', "Curve", "Convert to Poly curve without Bezier conversion"),
        ('BEZIER', "Bezier", "Convert to Bezier curve"),
        ('BEZIER_TO_POLY', "Bezier to Poly", "Convert to Bezier, then to Poly curve")
    ]

    spline_type: bpy.props.EnumProperty(
        name="Spline Type",
        description="Type of spline to convert to",
        items=spline_type_items,
        default='CURVE'  # Set "Curve" as the default selection
    )

    decimate_ratio: bpy.props.FloatProperty(
        name="Decimate Ratio",
        description="Ratio of decimation",
        default=0.07,
        min=0.01,
        max=1.0
    )

    resample_amount: bpy.props.IntProperty(
        name="Resample Amount",
        description="Number of points for resampling the curve",
        default=10,
        min=1,
        max=100
    )

    # Simplify Modifier Properties
    simplify_mode_items = [
        ('FIXED', "Fixed", "Simplify using a fixed number of steps"),
        ('ADAPTIVE', "Adaptive", "Simplify using an adaptive method"),
        ('SAMPLE', "Sample", "Simplify by sampling points"),
        ('MERGED', "Merged", "Simplify by merging points")
    ]

    simplify_mode: bpy.props.EnumProperty(
        name="Simplify Mode",
        description="Method for simplifying Grease Pencil strokes",
        items=simplify_mode_items,
        default='FIXED'
    )

    simplify_steps: bpy.props.IntProperty(
        name="Simplify Steps",
        description="Number of steps for the simplify modifier",
        default=2,
        min=1,
        max=50
    )

    # Properties for Hair Prep
    snap_to_surface: bpy.props.BoolProperty(
        name="Snap Curves to Surface",
        description="Enable snapping curves to the nearest surface",
        default=True
    )

    target_surface: bpy.props.StringProperty(
        name="Target Surface",
        description="Name of the surface object to attach hair to"
    )

    surface_target: bpy.props.PointerProperty(
        name="Surface Target",
        description="Target surface object for hair attachment",
        type=bpy.types.Object
    )

    surface_uv_map: bpy.props.StringProperty(
        name="UV Map",
        description="UV Map for the target surface"
    )


def register():
    bpy.utils.register_class(GPToCurveProperties)
    bpy.types.Scene.gpto_curve_properties = bpy.props.PointerProperty(type=GPToCurveProperties)


def unregister():
    bpy.utils.unregister_class(GPToCurveProperties)
    del bpy.types.Scene.gpto_curve_properties
