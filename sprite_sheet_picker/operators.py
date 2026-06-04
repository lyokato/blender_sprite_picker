import bpy
from bpy_extras.io_utils import ImportHelper

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

        redraw_properties()
        return {"FINISHED"}


class MATERIAL_OT_sprite_open_image(bpy.types.Operator, ImportHelper):
    bl_idname = "material.sprite_open_image"
    bl_label = "Open Sprite Sheet Image"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ""
    filter_glob: bpy.props.StringProperty(
        default="*.png;*.jpg;*.jpeg;*.tif;*.tiff;*.bmp;*.tga;*.webp;*.exr;*.hdr",
        options={"HIDDEN"},
    )

    def execute(self, context):
        material = active_material(context)
        if not material:
            self.report({"ERROR"}, "No active material")
            return {"CANCELLED"}

        try:
            image = bpy.data.images.load(self.filepath, check_existing=True)
        except RuntimeError as exc:
            self.report({"ERROR"}, "Could not open image: {}".format(exc))
            return {"CANCELLED"}

        material.sprite_sheet_settings.image = image
        redraw_properties()
        return {"FINISHED"}


class MATERIAL_OT_sprite_pick_cell_popup(bpy.types.Operator):
    bl_idname = "material.sprite_pick_cell_popup"
    bl_label = "Pick Sprite Cell"
    bl_options = {"REGISTER"}

    material_name: bpy.props.StringProperty()
    page: bpy.props.IntProperty(default=-1)

    def invoke(self, context, event):
        material = material_from_name(self.material_name) or active_material(context)
        if material:
            props = material.sprite_sheet_settings
            columns = min(max(1, props.columns), 6)
            width = min(max(560, columns * 144 + 72), 980)
        else:
            width = 520
        return context.window_manager.invoke_popup(self, width=width)

    def draw(self, context):
        material = material_from_name(self.material_name) or active_material(context)
        layout = self.layout
        if not material:
            layout.label(text="Material not found")
            return

        props = material.sprite_sheet_settings
        total = props.columns * props.rows
        if total <= 0:
            layout.label(text="Set valid sprite sheet image and cell size.")
            return

        max_page = max(0, (total - 1) // previews.MAX_THUMBNAILS_PER_PAGE)
        page = clamp(props.preview_page if self.page < 0 else self.page, 0, max_page)
        start = page * previews.MAX_THUMBNAILS_PER_PAGE
        end = min(total, start + previews.MAX_THUMBNAILS_PER_PAGE)

        page_row = layout.row(align=True)
        previous_col = page_row.row(align=True)
        previous_col.enabled = page > 0
        previous_col.operator_context = "INVOKE_DEFAULT"
        previous_page = previous_col.operator(
            "material.sprite_pick_cell_popup",
            text="Prev Page",
            icon="TRIA_LEFT",
        )
        previous_page.material_name = material.name
        previous_page.page = max(0, page - 1)

        page_row.separator(factor=0.8)
        page_row.label(text="Cells {}-{} of {}".format(start, max(start, end - 1), total))
        page_row.separator(factor=0.8)

        next_col = page_row.row(align=True)
        next_col.enabled = page < max_page
        next_col.operator_context = "INVOKE_DEFAULT"
        next_page = next_col.operator(
            "material.sprite_pick_cell_popup",
            text="Next Page",
            icon="TRIA_RIGHT",
        )
        next_page.material_name = material.name
        next_page.page = min(max_page, page + 1)

        layout.separator(factor=0.7)

        preview_items = previews.get_material_previews(material, page=page)
        if not preview_items:
            layout.label(text="No thumbnails available.")
            return

        grid_box = layout.box()
        grid_box.use_property_split = False
        grid_box.use_property_decorate = False
        columns = min(max(1, props.columns), 6)
        grid = grid_box.grid_flow(
            row_major=True,
            columns=columns,
            even_columns=True,
            even_rows=True,
            align=True,
        )
        grid.operator_context = "EXEC_DEFAULT"
        for index, icon_id in preview_items:
            selected = index == props.sprite_index
            cell = grid.box()
            cell.use_property_split = False
            cell.use_property_decorate = False
            if icon_id:
                cell.template_icon(icon_value=icon_id, scale=8.0)
            else:
                placeholder = cell.row(align=True)
                placeholder.scale_y = 8.0
                placeholder.label(text="", icon="IMAGE_DATA")

            select_row = cell.row(align=True)
            select_row.scale_y = 1.15
            if selected:
                select_row.alignment = "CENTER"
                select_row.label(text="", icon="CHECKMARK")
            else:
                select_op = select_row.operator(
                    "material.sprite_select_cell",
                    text="Select",
                    emboss=True,
                )
                select_op.material_name = material.name
                select_op.index = index

    def execute(self, context):
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
    MATERIAL_OT_sprite_open_image,
    MATERIAL_OT_sprite_pick_cell_popup,
    MATERIAL_OT_sprite_insert_key,
    MATERIAL_OT_sprite_step_index,
    MATERIAL_OT_sprite_set_preview_page,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
