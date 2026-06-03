import bpy

from . import previews, properties
from .utils import active_material


class MATERIAL_PT_sprite_sheet_picker(bpy.types.Panel):
    bl_label = "Sprite Sheet Picker"
    bl_idname = "MATERIAL_PT_sprite_sheet_picker"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return active_material(context) is not None

    def draw(self, context):
        layout = self.layout
        material = active_material(context)
        props = material.sprite_sheet_settings

        layout.prop(props, "image")

        cell_row = layout.row(align=True)
        cell_row.prop(props, "cell_width")
        cell_row.prop(props, "cell_height")

        grid_info = layout.row(align=True)
        grid_info.label(text="Columns: {}".format(props.columns))
        grid_info.label(text="Rows: {}".format(props.rows))

        total = props.columns * props.rows
        max_index = max(0, total - 1)
        layout.label(text="Selected: {} / {}".format(props.sprite_index, max_index))
        layout.prop(props, "auto_key_on_pick")

        buttons = layout.row(align=True)
        buttons.operator("material.sprite_setup_nodes", text="Setup Nodes", icon="NODETREE")
        buttons.operator("material.sprite_refresh_thumbnails", text="Refresh", icon="FILE_REFRESH")
        buttons.operator("material.sprite_insert_key", text="Insert Key", icon="KEY_HLT")

        self.draw_thumbnail_grid(layout, material, props)

    def draw_thumbnail_grid(self, layout, material, props):
        total = props.columns * props.rows
        if not props.image:
            layout.label(text="Select a sprite sheet image.")
            return
        if total <= 0:
            layout.label(text="Set valid cell width and height.")
            return

        preview_items = previews.get_material_previews(material)
        if not preview_items:
            layout.label(text="No thumbnails available.")
            return

        visible_indices = {str(index) for index, _ in preview_items}
        if str(props.sprite_index) not in visible_indices or props.preview_index not in visible_indices:
            properties.schedule_preview_sync(material.name)

        layout.template_icon_view(
            props,
            "preview_index",
            show_labels=False,
            scale=6.0,
            scale_popup=1.0,
        )
        choose_op = layout.operator("material.sprite_pick_cell_popup", text="Choose Cell", icon="IMAGE")
        choose_op.material_name = material.name


classes = (
    MATERIAL_PT_sprite_sheet_picker,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
