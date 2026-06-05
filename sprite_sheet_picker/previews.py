import os
import shutil
import tempfile
from array import array

import bpy
import bpy.utils.previews

from .utils import compute_grid, grid_total, max_page

MAX_THUMBNAILS_PER_PAGE = 256

_preview_collections = {}
_preview_dirs = {}
_preview_items = {}


def material_cache_key(material, page=None):
    props = material.sprite_sheet_settings
    image = props.image
    image_size = tuple(int(v) for v in image.size) if image else (0, 0)
    preview_page = props.preview_page if page is None else page
    library = image.library.filepath if image and image.library else ""
    filepath = image.filepath if image else ""
    return (
        material.name_full,
        image.name_full if image else "",
        filepath,
        image_size,
        props.cell_width,
        props.cell_height,
        library,
        preview_page,
    )


def get_material_previews(material, page=None):
    props = material.sprite_sheet_settings
    columns, rows = compute_grid(props.image, props.cell_width, props.cell_height)
    if not props.image or columns <= 0 or rows <= 0:
        return []

    total = grid_total(columns, rows)
    page_limit = max_page(total, MAX_THUMBNAILS_PER_PAGE)
    resolved_page = max(0, min(props.preview_page if page is None else page, page_limit))
    start = resolved_page * MAX_THUMBNAILS_PER_PAGE
    end = min(total, start + MAX_THUMBNAILS_PER_PAGE)

    key = material_cache_key(material, resolved_page)
    if key in _preview_items:
        return _preview_items[key]

    clear_preview_key(key)

    collection = bpy.utils.previews.new()
    directory = tempfile.mkdtemp(prefix="sprite_sheet_picker_")
    _preview_collections[key] = collection
    _preview_dirs[key] = directory

    previews = []
    pixel_source = image_pixels(props.image)
    image_width = int(props.image.size[0])
    image_height = int(props.image.size[1])

    for index in range(start, end):
        if not pixel_source:
            previews.append((index, 0))
            continue

        name = "page_{:04d}_cell_{:04d}".format(resolved_page, index)
        path = os.path.join(directory, "{}.png".format(name))
        try:
            save_cell_image(
                pixel_source,
                image_width,
                image_height,
                props.cell_width,
                props.cell_height,
                columns,
                index,
                path,
            )
            icon = collection.load(name, path, "IMAGE", force_reload=True)
            previews.append((index, icon.icon_id))
        except Exception:
            previews.append((index, 0))

    if not previews:
        clear_preview_key(key)
        return []

    _preview_items[key] = previews
    return previews


def image_pixels(image):
    try:
        if not image.has_data:
            image.reload()
        return list(image.pixels)
    except Exception:
        return None


def cell_pixels(pixels, image_width, image_height, cell_width, cell_height, columns, index):
    column = index % columns
    row = index // columns
    left = column * cell_width
    top = row * cell_height
    data = array("f", [0.0] * (cell_width * cell_height * 4))

    for target_y in range(cell_height):
        source_y = image_height - top - cell_height + target_y
        if source_y < 0 or source_y >= image_height:
            continue
        for target_x in range(cell_width):
            source_x = left + target_x
            if source_x < 0 or source_x >= image_width:
                continue
            source_offset = (source_y * image_width + source_x) * 4
            target_offset = (target_y * cell_width + target_x) * 4
            data[target_offset:target_offset + 4] = array(
                "f",
                pixels[source_offset:source_offset + 4],
            )

    return data


def save_cell_image(
    pixels,
    image_width,
    image_height,
    cell_width,
    cell_height,
    columns,
    index,
    path,
):
    thumb = bpy.data.images.new(
        "sprite_sheet_picker_cell_{:04d}".format(index),
        width=cell_width,
        height=cell_height,
        alpha=True,
    )
    try:
        thumb.pixels.foreach_set(
            cell_pixels(
                pixels,
                image_width,
                image_height,
                cell_width,
                cell_height,
                columns,
                index,
            )
        )
        thumb.file_format = "PNG"
        thumb.filepath_raw = path
        thumb.save()
    finally:
        bpy.data.images.remove(thumb)


def clear_preview_key(key):
    collection = _preview_collections.pop(key, None)
    directory = _preview_dirs.pop(key, None)
    _preview_items.pop(key, None)

    if collection:
        bpy.utils.previews.remove(collection)
    if directory and os.path.isdir(directory):
        shutil.rmtree(directory, ignore_errors=True)


def clear_material_previews(material):
    material_name = material.name_full if material else None
    known_keys = set(_preview_collections) | set(_preview_dirs) | set(_preview_items)
    keys = [
        key for key in known_keys
        if material_name is None or key[0] == material_name
    ]

    for key in keys:
        clear_preview_key(key)


def clear_all_previews():
    for collection in _preview_collections.values():
        bpy.utils.previews.remove(collection)
    _preview_collections.clear()
    _preview_items.clear()

    for directory in _preview_dirs.values():
        if os.path.isdir(directory):
            shutil.rmtree(directory, ignore_errors=True)
    _preview_dirs.clear()


def register():
    pass


def unregister():
    clear_all_previews()
