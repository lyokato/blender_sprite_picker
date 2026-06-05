BLENDER_45 ?= /Applications/Blender_4_5.app/Contents/MacOS/Blender
BLENDER_51 ?= /Applications/Blender_5_1.app/Contents/MacOS/Blender

ADDON_NAME := sprite_sheet_picker
VERSION := $(shell sed -nE 's/.*"version": \(([0-9]+),[[:space:]]*([0-9]+),[[:space:]]*([0-9]+)\).*/\1.\2.\3/p' $(ADDON_NAME)/__init__.py)
DIST_DIR := dist
DIST_ZIP := $(DIST_DIR)/$(ADDON_NAME)-v$(VERSION).zip

.PHONY: dist print-version test test-45 test-51 ui-smoke clean

dist:
	mkdir -p $(DIST_DIR)
	zip -r -FS $(DIST_ZIP) $(ADDON_NAME) README.md CHANGELOG.md LICENSE -x '*/__pycache__/*'

print-version:
	@printf '%s\n' $(VERSION)

test: test-45 test-51

test-45:
	$(BLENDER_45) --background --factory-startup --python test_blender_addon.py

test-51:
	$(BLENDER_51) --background --factory-startup --python test_blender_addon.py

ui-smoke:
	$(BLENDER_45) --factory-startup --python test_blender_ui_smoke.py

clean:
	rm -rf __pycache__ $(ADDON_NAME)/__pycache__ ui_test_output $(DIST_DIR)
