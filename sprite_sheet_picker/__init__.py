bl_info = {
    "name": "Sprite Sheet Material Picker",
    "author": "Codex",
    "version": (1, 0, 1),
    "blender": (4, 5, 0),
    "location": "Properties > Material > Sprite Sheet Picker",
    "description": "Pick cells from a sprite sheet image and drive material UVs by sprite_index.",
    "category": "Material",
}

if "animation" in locals():
    import importlib

    for module in (utils, animation, nodes, previews, properties, operators, ui):
        importlib.reload(module)
else:
    from . import animation, nodes, operators, previews, properties, ui, utils


modules = (
    properties,
    animation,
    nodes,
    previews,
    operators,
    ui,
)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
