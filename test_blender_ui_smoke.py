import os
import sys

import bpy

ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import sprite_sheet_picker

OUTPUT_DIR = os.path.join(ROOT, "ui_test_output")
SCREENSHOT_PATH = os.path.join(OUTPUT_DIR, "sprite_sheet_picker_panel.png")


def make_sprite_sheet():
    image = bpy.data.images.new("UI Smoke Sprite Sheet", width=256, height=256, alpha=True)
    pixels = []
    for y in range(256):
        for x in range(256):
            col = x // 64
            row = y // 64
            pixels.extend((
                (col + 1) / 4.0,
                (row + 1) / 4.0,
                ((col + row) % 2) * 0.7 + 0.2,
                1.0,
            ))
    image.pixels.foreach_set(pixels)
    image.update()
    return image


def setup_scene():
    try:
        sprite_sheet_picker.unregister()
    except Exception:
        pass
    sprite_sheet_picker.register()

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.mesh.primitive_plane_add(size=2)
    obj = bpy.context.object
    material = bpy.data.materials.new("UI Smoke Material")
    obj.data.materials.append(material)
    obj.active_material = material
    bpy.context.view_layer.objects.active = obj

    props = material.sprite_sheet_settings
    props.image = make_sprite_sheet()
    props.cell_width = 64
    props.cell_height = 64
    props.sprite_index = 5

    # Emulate the action that used to make the preview appear.
    bpy.ops.material.sprite_step_index(step=1)
    bpy.ops.material.sprite_step_index(step=-1)

    for area in bpy.context.screen.areas:
        if area.type == "PROPERTIES":
            space = area.spaces.active
            space.context = "MATERIAL"
            area.tag_redraw()

    os.makedirs(OUTPUT_DIR, exist_ok=True)


def take_screenshot():
    bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=3)
    bpy.ops.screen.screenshot(filepath=SCREENSHOT_PATH)
    print("SPRITE_SHEET_PICKER_UI_SCREENSHOT", SCREENSHOT_PATH)
    bpy.ops.wm.quit_blender()
    return None


def main():
    setup_scene()
    bpy.app.timers.register(take_screenshot, first_interval=1.0)


if __name__ == "__main__":
    main()
