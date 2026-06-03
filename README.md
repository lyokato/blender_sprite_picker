# Sprite Sheet Material Picker

Blender material add-on for selecting cells from a sprite sheet image and driving a shader UV node group with `material.sprite_sheet_settings.sprite_index`.

Tested with Blender 4.5 LTS and Blender 5.1.

## Install

1. Run `make dist`, or point Blender at the folder during development.
2. In Blender, open `Edit > Preferences > Add-ons > Install...`.
3. Install `sprite_sheet_picker.zip`.
4. Enable `Sprite Sheet Material Picker`.

## Development

```sh
make dist
make test
make ui-smoke
```

`make test` runs the background add-on tests with Blender 4.5 and 5.1. `make ui-smoke` opens Blender 4.5, creates a test material, shows the Material Properties panel, and saves a screenshot.

## Basic Workflow

1. Select an object with a material.
2. Open `Properties > Material > Sprite Sheet Picker`.
3. Choose a sprite sheet image.
4. Set `Cell Width` and `Cell Height`.
5. Press `Setup Nodes`.
6. Press `Refresh` if thumbnails are not shown yet.
7. Pick an image in the `Sprite Cell` thumbnail view to update `Sprite Index`.
8. Use `Insert Key`, or enable `Auto Key on Pick`, to keyframe `sprite_index`.

The add-on sets keyframe interpolation for `sprite_index` to `CONSTANT`.

Sprite cells are calculated with floor division. For example, a 512 x 512 image with 50 x 50 cells becomes 10 columns x 10 rows. The 12 px remainder on the right and bottom edges is ignored, and valid indices are 0 through 99.

## Notes

- Thumbnails are generated from Blender image pixels and cached for the active page.
- Preview display is paged at up to 256 cells per page.
- The panel uses Blender's icon view for the selected cell preview and tile picker.
- The `Choose Cell` popup contains the page controls and the visible cell choices for the active thumbnail page.
- Thumbnail caches are cleared automatically when the sprite sheet image, cell size, or page changes. A deferred sync also runs after image/cell changes so the initial preview value is initialized without extra navigation.
- `sprite_index` is an internal animated property. Users pick cells from the thumbnail view instead of typing index numbers directly.
- The shader setup creates or reuses:
  - `SPRITE_SHEET_IMAGE`
  - `SPRITE_SHEET_UV`
  - `Sprite Sheet UV` node group

## UI Smoke Test

Run this from the project root to open Blender, create a test material, show the Material Properties panel, and save a screenshot:

```sh
make ui-smoke
```

The screenshot is written to `ui_test_output/sprite_sheet_picker_panel.png`.
