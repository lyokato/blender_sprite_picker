import bpy

PROP_SPRITE_INDEX = "sprite_index"


def active_material(context):
    obj = context.object
    if obj and obj.active_material:
        return obj.active_material
    return None


def material_from_name(name):
    return bpy.data.materials.get(name)


def image_dimensions(image):
    if not image:
        return 0, 0
    width, height = image.size
    return int(width), int(height)


def compute_grid(image, cell_width, cell_height):
    width, height = image_dimensions(image)
    if not image or cell_width <= 0 or cell_height <= 0:
        return 0, 0
    return width // cell_width, height // cell_height


def grid_total(columns, rows):
    return columns * rows


def max_index(columns, rows):
    return max(0, grid_total(columns, rows) - 1)


def max_page(total, page_size):
    return max(0, (total - 1) // page_size)


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def redraw_properties():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "PROPERTIES":
                area.tag_redraw()
