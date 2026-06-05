---
name: blender-sprite-development
description: Use when modifying, testing, packaging, or preparing releases for the Sprite Sheet Material Picker Blender add-on in this repository. Covers repository-specific Blender commands, version metadata, distribution zip creation, UI smoke checks, and release preparation.
---

# Sprite Sheet Material Picker Development

Use this skill when working on the add-on code, tests, packaging, or release prep. Do not add these development details to `README.md`; that file is for Blender users.

## Repository Shape

- Add-on package: `sprite_sheet_picker/`
- Add-on metadata: `sprite_sheet_picker/__init__.py`
- Blender extension metadata: `sprite_sheet_picker/blender_manifest.toml`
- Background test script: `test_blender_addon.py`
- UI smoke test script: `test_blender_ui_smoke.py`
- Distribution output: `dist/`
- UI smoke output: `ui_test_output/sprite_sheet_picker_panel.png`

## Common Commands

Run commands from the repository root.

```sh
make dist
make test
make ui-smoke
```

- `make dist` reads `bl_info["version"]` from `sprite_sheet_picker/__init__.py` and writes a versioned zip such as `dist/sprite_sheet_picker-v1.0.0.zip`.
- `make test` runs the background add-on tests with Blender 4.5 and Blender 5.1.
- `make ui-smoke` opens Blender 4.5, creates a test material, shows the Material Properties panel, and saves a screenshot.

If Blender is installed somewhere else, override the paths:

```sh
make test BLENDER_45=/path/to/blender-4.5 BLENDER_51=/path/to/blender-5.1
make ui-smoke BLENDER_45=/path/to/blender-4.5
```

## Packaging Notes

This add-on keeps traditional `bl_info` metadata in `sprite_sheet_picker/__init__.py`, which is enough for GitHub zip distribution and manual installation through Blender's Add-ons preferences.

The package also includes `sprite_sheet_picker/blender_manifest.toml` for Blender 4.2+ extension metadata. This supports newer extension-style installation flows, but publishing on the official Blender Extensions platform is not required.

The distribution zip includes:

- `sprite_sheet_picker/`
- `README.md`
- `CHANGELOG.md`
- `LICENSE`

## Release Checklist

1. Update `bl_info["version"]` in `sprite_sheet_picker/__init__.py`.
2. Update `version` in `sprite_sheet_picker/blender_manifest.toml`.
3. Update `CHANGELOG.md`.
4. Run `make test`.
5. Run `make dist`.
6. Commit the version bump and changelog.
7. Create and push a matching tag:

```sh
git tag v1.0.0
git push origin main --tags
```

Pushing a tag like `v1.0.0` runs the release workflow. GitHub creates a release for that tag and attaches the versioned zip from `make dist`.

## User Documentation Boundary

Keep `README.md` focused on Blender users who may not understand code:

- Installation from the GitHub release zip
- Enabling the add-on in Blender
- Selecting a sprite sheet
- Setting cell size
- Running **Setup Nodes**
- Choosing cells
- Inserting animation keyframes

Do not put build commands, packaging rationale, release checklists, test commands, or internal implementation notes in `README.md`.
