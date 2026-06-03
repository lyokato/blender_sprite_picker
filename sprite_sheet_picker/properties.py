import bpy

from . import nodes, previews
from .utils import clamp, compute_grid, max_index, redraw_properties

_syncing_preview_index = False
_scheduled_materials = set()


def update_image(self, context):
    sync_settings(self, context, rebuild_previews=True)
    schedule_preview_sync(self.id_data.name)


def update_cell_size(self, context):
    sync_settings(self, context, rebuild_previews=True)
    schedule_preview_sync(self.id_data.name)


def update_sprite_index(self, context):
    sync_settings(self, context, rebuild_previews=False)
    sync_preview_page_to_sprite_index(self)
    sync_preview_index(self)


def update_preview_index(self, context):
    if _syncing_preview_index:
        return
    if not self.preview_index.isdigit():
        return

    index = int(self.preview_index)
    if self.sprite_index != index:
        self.sprite_index = index

    if self.auto_key_on_pick:
        from . import animation
        animation.insert_sprite_index_key(context, self.id_data)


def preview_index_items(self, context):
    material = self.id_data
    if not material or not self.image:
        return [("__NONE__", "No Thumbnails", "", 0, 0)]

    items = []
    for index, icon_id in previews.get_material_previews(material):
        items.append((
            str(index),
            str(index),
            "Sprite cell {}".format(index),
            icon_id,
            index,
        ))

    return items or [("__NONE__", "No Thumbnails", "", 0, 0)]


def sync_preview_index(settings):
    global _syncing_preview_index

    identifier = str(settings.sprite_index)
    try:
        _syncing_preview_index = True
        settings.preview_index = identifier
    except TypeError:
        pass
    finally:
        _syncing_preview_index = False


def set_preview_index_for_page(settings):
    page_start = settings.preview_page * previews.MAX_THUMBNAILS_PER_PAGE
    set_preview_index_without_update(settings, page_start)


def set_preview_index_without_update(settings, index):
    global _syncing_preview_index

    try:
        _syncing_preview_index = True
        settings.preview_index = str(index)
    except TypeError:
        pass
    finally:
        _syncing_preview_index = False


def sync_preview_page_to_sprite_index(settings):
    page = settings.sprite_index // previews.MAX_THUMBNAILS_PER_PAGE
    if settings.preview_page != page:
        settings.preview_page = page


def sync_settings(settings, context, rebuild_previews=False):
    material = settings.id_data
    columns, rows = compute_grid(settings.image, settings.cell_width, settings.cell_height)

    if settings.columns != columns:
        settings.columns = columns
    if settings.rows != rows:
        settings.rows = rows

    limit = max_index(columns, rows)
    clamped = clamp(settings.sprite_index, 0, limit)
    if settings.sprite_index != clamped:
        settings.sprite_index = clamped
        return

    if material and material.use_nodes:
        nodes.sync_material_nodes(material)

    if rebuild_previews:
        sync_preview_page_to_sprite_index(settings)
        previews.clear_material_previews(material)
        sync_preview_index(settings)
        redraw_properties()


def schedule_preview_sync(material_name):
    if material_name in _scheduled_materials:
        return
    _scheduled_materials.add(material_name)

    def sync_later():
        _scheduled_materials.discard(material_name)
        material = bpy.data.materials.get(material_name)
        if not material:
            return None
        settings = material.sprite_sheet_settings
        previews.get_material_previews(material)
        sync_preview_page_to_sprite_index(settings)
        sync_preview_index(settings)
        redraw_properties()
        return None

    try:
        bpy.app.timers.register(sync_later, first_interval=0.05)
    except ValueError:
        pass


class SpriteSheetSettings(bpy.types.PropertyGroup):
    image: bpy.props.PointerProperty(
        name="Sprite Sheet",
        type=bpy.types.Image,
        update=update_image,
    )
    cell_width: bpy.props.IntProperty(
        name="Cell Width",
        default=32,
        min=1,
        update=update_cell_size,
    )
    cell_height: bpy.props.IntProperty(
        name="Cell Height",
        default=32,
        min=1,
        update=update_cell_size,
    )
    sprite_index: bpy.props.IntProperty(
        name="Sprite Index",
        default=0,
        min=0,
        update=update_sprite_index,
    )
    columns: bpy.props.IntProperty(
        name="Columns",
        default=0,
        min=0,
    )
    rows: bpy.props.IntProperty(
        name="Rows",
        default=0,
        min=0,
    )
    auto_key_on_pick: bpy.props.BoolProperty(
        name="Auto Key on Pick",
        default=False,
    )
    preview_page: bpy.props.IntProperty(
        name="Preview Page",
        default=0,
        min=0,
    )
    preview_index: bpy.props.EnumProperty(
        name="Sprite Cell",
        items=preview_index_items,
        update=update_preview_index,
    )


classes = (
    SpriteSheetSettings,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Material.sprite_sheet_settings = bpy.props.PointerProperty(type=SpriteSheetSettings)


def unregister():
    del bpy.types.Material.sprite_sheet_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
