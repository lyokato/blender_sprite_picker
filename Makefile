BLENDER_45 ?= /Applications/Blender_4_5.app/Contents/MacOS/Blender
BLENDER_51 ?= /Applications/Blender_5_1.app/Contents/MacOS/Blender

ADDON_NAME := sprite_sheet_picker
DIST_ZIP := $(ADDON_NAME).zip

.PHONY: dist test test-45 test-51 ui-smoke clean

dist:
	zip -r -FS $(DIST_ZIP) $(ADDON_NAME) README.md -x '*/__pycache__/*'

test: test-45 test-51

test-45:
	$(BLENDER_45) --background --factory-startup --python test_blender_addon.py

test-51:
	$(BLENDER_51) --background --factory-startup --python test_blender_addon.py

ui-smoke:
	$(BLENDER_45) --factory-startup --python test_blender_ui_smoke.py

clean:
	rm -rf __pycache__ $(ADDON_NAME)/__pycache__ ui_test_output
