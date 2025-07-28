bl_info = {
    "name": "GP to Curve",
    "blender": (4, 0, 3),
    "category": "Object",
    "description": "Convert Grease Pencil to Simplified Bezier Curve, with optional conversion to Poly, and Hair Prep feature",
    "author": "DadsCastle",
    "version": (0, 4, 4),
}

from . import operators, ui, properties

def register():
    properties.register()
    operators.register()
    ui.register()

def unregister():
    ui.unregister()
    operators.unregister()
    properties.unregister()

if __name__ == "__main__":
    register()
