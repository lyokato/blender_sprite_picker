import bpy

from . import animation, nodes, previews, properties
from .utils import active_material, clamp, max_index, material_from_name, redraw_properties


class MATERIAL_OT_sprite_setup_nodes(bpy.types.Operator):
    bl_idname = "material.sprite_setup_nodes"
    bl_label = "Setup Nodes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        material = active_material(context)
        if not material:
            self.report({"ERROR"}, "No active material")
            return {"CANCELLED"}

        nodes.setup_material_nodes(material)
        self.report({"INFO"}, "Sprite sheet nodes are ready")
        return {"FINISHED"}


class MATERIAL_OT_sprite_select_cell(bpy.types.Operator):
    bl_idname = "material.sprite_select_cell"
    bl_label = "Select Sprite Cell"
    bl_options = {"REGISTER", "UNDO"}

    material_name: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        material = material_from_name(self.material_name) or active_material(context)
        if not material:
            self.report({"ERROR"}, "Material not found")
            return {"CANCELLED"}

        props = material.sprite_sheet_settings
        props.sprite_index = clamp(self.index, 0, max_index(props.columns, props.rows))

        if props.auto_key_on_pick:
            animation.insert_sprite_index_key(context, material)

        redraw_properties()
        return {"FINISHED"}


class MATERIAL_OT_sprite_insert_key(bpy.types.Operator):
    bl_idname = "material.sprite_insert_key"
    bl_label = "Insert Key"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        material = active_material(context)
        if not material:
            self.report({"ERROR"}, "No active material")
            return {"CANCELLED"}

        animation.insert_sprite_index_key(context, material)
        self.report({"INFO"}, "Inserted constant sprite_index key")
        return {"FINISHED"}


class MATERIAL_OT_sprite_refresh_thumbnails(bpy.types.Operator):
    bl_idname = "material.sprite_refresh_thumbnails"
    bl_label = "Build/Refresh Thumbnails"
    bl_options = {"REGISTER"}

    def execute(self, context):
        material = active_material(context)
        if not material:
            self.report({"ERROR"}, "No active material")
            return {"CANCELLED"}

        previews.clear_material_previews(material)
        redraw_properties()
        return {"FINISHED"}


class MATERIAL_OT_sprite_step_index(bpy.types.Operator):
    bl_idname = "material.sprite_step_index"
    bl_label = "Step Sprite Index"
    bl_options = {"REGISTER", "UNDO"}

    step: bpy.props.IntProperty(default=1)

    def execute(self, context):
        material = active_material(context)
        if not material:
            self.report({"ERROR"}, "No active material")
            return {"CANCELLED"}

        props = material.sprite_sheet_settings
        props.sprite_index = clamp(
            props.sprite_index + self.step,
            0,
            max_index(props.columns, props.rows),
        )
        redraw_properties()
        return {"FINISHED"}


class MATERIAL_OT_sprite_set_preview_page(bpy.types.Operator):
    bl_idname = "material.sprite_set_preview_page"
    bl_label = "Set Sprite Preview Page"
    bl_options = {"REGISTER"}

    step: bpy.props.IntProperty(default=1)

    def execute(self, context):
        material = active_material(context)
        if not material:
            self.report({"ERROR"}, "No active material")
            return {"CANCELLED"}

        props = material.sprite_sheet_settings
        total = props.columns * props.rows
        max_page = max(0, (total - 1) // previews.MAX_THUMBNAILS_PER_PAGE)
        props.preview_page = clamp(props.preview_page + self.step, 0, max_page)
        properties.set_preview_index_for_page(props)
        previews.clear_material_previews(material)
        redraw_properties()
        return {"FINISHED"}


classes = (
    MATERIAL_OT_sprite_setup_nodes,
    MATERIAL_OT_sprite_select_cell,
    MATERIAL_OT_sprite_insert_key,
    MATERIAL_OT_sprite_refresh_thumbnails,
    MATERIAL_OT_sprite_step_index,
    MATERIAL_OT_sprite_set_preview_page,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
