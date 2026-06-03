import os
import sys

import bpy

ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import sprite_sheet_picker
from sprite_sheet_picker import nodes, previews


def main():
    sprite_sheet_picker.register()

    material = bpy.data.materials.new("Sprite Test Material")
    material.use_nodes = True

    image = bpy.data.images.new("Sprite Test Image", width=64, height=64, alpha=True)
    pixels = [1.0, 0.0, 0.0, 1.0] * (64 * 64)
    image.pixels.foreach_set(pixels)

    props = material.sprite_sheet_settings
    props.image = image
    props.cell_width = 16
    props.cell_height = 16
    props.sprite_index = 5

    assert props.columns == 4, props.columns
    assert props.rows == 4, props.rows
    assert len(previews.get_material_previews(material)) == 16

    nodes.setup_material_nodes(material)

    tree = material.node_tree
    image_node = tree.nodes.get(nodes.IMAGE_NODE_NAME)
    uv_node = tree.nodes.get(nodes.UV_NODE_NAME)
    assert image_node is not None
    assert uv_node is not None
    assert image_node.image == image
    assert uv_node.inputs["Columns"].default_value == 4
    assert uv_node.inputs["Rows"].default_value == 4

    driver = None
    for fcurve in tree.animation_data.drivers:
        if "inputs[1].default_value" in fcurve.data_path:
            driver = fcurve.driver
            break
    assert driver is not None
    assert driver.variables[0].targets[0].id == material
    assert driver.variables[0].targets[0].data_path == "sprite_sheet_settings.sprite_index"

    props.keyframe_insert(data_path="sprite_index", frame=1)
    from sprite_sheet_picker.animation import iter_action_fcurves, set_sprite_index_interpolation_constant
    set_sprite_index_interpolation_constant(material)
    fcurve = next(iter_action_fcurves(material.animation_data.action))
    assert fcurve.keyframe_points[0].interpolation == "CONSTANT"

    preview_items = previews.get_material_previews(material)
    assert len(preview_items) == 16, len(preview_items)
    assert isinstance(preview_items[0], tuple), type(preview_items[0])

    cached_preview_items = previews.get_material_previews(material)
    assert len(cached_preview_items) == 16, len(cached_preview_items)
    assert isinstance(cached_preview_items[0], tuple), type(cached_preview_items[0])
    assert cached_preview_items[0][0] == 0

    props.preview_index = "7"
    assert props.sprite_index == 7, props.sprite_index

    paged_material = bpy.data.materials.new("Paged Sprite Test Material")
    paged_image = bpy.data.images.new("Paged Sprite Test Image", width=512, height=544, alpha=True)
    paged_pixels = [0.0, 1.0, 0.0, 1.0] * (512 * 544)
    paged_image.pixels.foreach_set(paged_pixels)

    paged_props = paged_material.sprite_sheet_settings
    paged_props.image = paged_image
    paged_props.cell_width = 32
    paged_props.cell_height = 32

    assert paged_props.columns == 16, paged_props.columns
    assert paged_props.rows == 17, paged_props.rows

    first_page_items = previews.get_material_previews(paged_material)
    assert len(first_page_items) == 256, len(first_page_items)

    from sprite_sheet_picker import properties
    paged_props.preview_page = 1
    properties.set_preview_index_for_page(paged_props)
    assert paged_props.preview_index == "256", paged_props.preview_index
    assert paged_props.sprite_index == 0, paged_props.sprite_index

    second_page_items = previews.get_material_previews(paged_material)
    assert len(second_page_items) == 16, len(second_page_items)
    assert second_page_items[0][0] == 256, second_page_items[0]

    remainder_material = bpy.data.materials.new("Remainder Sprite Test Material")
    remainder_image = bpy.data.images.new("Remainder Sprite Test Image", width=512, height=512, alpha=True)
    remainder_pixels = [0.0, 0.0, 1.0, 1.0] * (512 * 512)
    remainder_image.pixels.foreach_set(remainder_pixels)

    remainder_props = remainder_material.sprite_sheet_settings
    remainder_props.image = remainder_image
    remainder_props.cell_width = 50
    remainder_props.cell_height = 50

    assert remainder_props.columns == 10, remainder_props.columns
    assert remainder_props.rows == 10, remainder_props.rows

    remainder_items = previews.get_material_previews(remainder_material)
    assert len(remainder_items) == 100, len(remainder_items)
    assert remainder_items[0][0] == 0, remainder_items[0]
    assert remainder_items[-1][0] == 99, remainder_items[-1]

    remainder_props.cell_width = 64
    remainder_props.cell_height = 64
    rebuilt_items = previews.get_material_previews(remainder_material)
    assert remainder_props.columns == 8, remainder_props.columns
    assert remainder_props.rows == 8, remainder_props.rows
    assert len(rebuilt_items) == 64, len(rebuilt_items)

    original_image_pixels = previews.image_pixels
    previews.image_pixels = lambda image: None
    try:
        previews.clear_material_previews(remainder_material)
        fallback_items = previews.get_material_previews(remainder_material)
        assert len(fallback_items) == 64, len(fallback_items)
        assert fallback_items[0] == (0, 0), fallback_items[0]
    finally:
        previews.image_pixels = original_image_pixels

    sprite_sheet_picker.unregister()
    print("SPRITE_SHEET_PICKER_TEST_OK")


if __name__ == "__main__":
    main()
