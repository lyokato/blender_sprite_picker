from .utils import PROP_SPRITE_INDEX


def insert_sprite_index_key(context, material):
    props = material.sprite_sheet_settings
    props.keyframe_insert(
        data_path=PROP_SPRITE_INDEX,
        frame=context.scene.frame_current,
    )
    set_sprite_index_interpolation_constant(material)


def set_sprite_index_interpolation_constant(material):
    props = material.sprite_sheet_settings
    data_path = props.path_from_id(PROP_SPRITE_INDEX)
    anim = material.animation_data

    if not anim or not anim.action:
        return

    for fcurve in iter_action_fcurves(anim.action):
        if fcurve.data_path == data_path:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = "CONSTANT"


def iter_action_fcurves(action):
    if hasattr(action, "fcurves"):
        yield from action.fcurves
        return

    for layer in getattr(action, "layers", []):
        for strip in getattr(layer, "strips", []):
            for channelbag in getattr(strip, "channelbags", []):
                yield from getattr(channelbag, "fcurves", [])


def register():
    pass


def unregister():
    pass
