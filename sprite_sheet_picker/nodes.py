import bpy

IMAGE_NODE_NAME = "SPRITE_SHEET_IMAGE"
UV_NODE_NAME = "SPRITE_SHEET_UV"
UV_GROUP_NAME = "Sprite Sheet UV"


def setup_material_nodes(material):
    props = material.sprite_sheet_settings
    material.use_nodes = True

    tree = material.node_tree
    image_node = get_or_create_image_node(tree)
    uv_node = get_or_create_uv_group_node(tree)

    image_node.image = props.image
    set_socket_default(uv_node, "Columns", max(1, props.columns))
    set_socket_default(uv_node, "Rows", max(1, props.rows))

    setup_index_driver(material, uv_node)
    link_sprite_nodes(tree, image_node, uv_node)


def sync_material_nodes(material):
    if not material or not material.use_nodes or not material.node_tree:
        return

    props = material.sprite_sheet_settings
    tree = material.node_tree
    image_node = tree.nodes.get(IMAGE_NODE_NAME)
    uv_node = tree.nodes.get(UV_NODE_NAME)

    if image_node:
        image_node.image = props.image
    if uv_node:
        set_socket_default(uv_node, "Columns", max(1, props.columns))
        set_socket_default(uv_node, "Rows", max(1, props.rows))


def get_or_create_image_node(tree):
    node = tree.nodes.get(IMAGE_NODE_NAME)
    if not node:
        node = tree.nodes.new("ShaderNodeTexImage")
        node.name = IMAGE_NODE_NAME
        node.label = "Sprite Sheet Image"
        node.location = (-360, 180)
        node.extension = "CLIP"
        node.interpolation = "Closest"
    return node


def get_or_create_uv_group_node(tree):
    node = tree.nodes.get(UV_NODE_NAME)
    if not node:
        node = tree.nodes.new("ShaderNodeGroup")
        node.name = UV_NODE_NAME
        node.label = "Sprite Sheet UV"
        node.location = (-580, 120)
    node.node_tree = get_or_create_uv_group()
    return node


def get_or_create_uv_group():
    group = bpy.data.node_groups.get(UV_GROUP_NAME)
    if group:
        return group

    group = bpy.data.node_groups.new(UV_GROUP_NAME, "ShaderNodeTree")
    ensure_group_socket(group, "UV", "INPUT", "NodeSocketVector")
    ensure_group_socket(group, "Index", "INPUT", "NodeSocketFloat")
    ensure_group_socket(group, "Columns", "INPUT", "NodeSocketFloat")
    ensure_group_socket(group, "Rows", "INPUT", "NodeSocketFloat")
    ensure_group_socket(group, "Vector", "OUTPUT", "NodeSocketVector")

    nodes = group.nodes
    links = group.links

    group_in = nodes.new("NodeGroupInput")
    group_in.location = (-900, 0)
    group_out = nodes.new("NodeGroupOutput")
    group_out.location = (620, 0)

    mod_x = math_node(nodes, "MODULO", "Column", (-680, 120))
    div_y = math_node(nodes, "DIVIDE", "Index / Columns", (-680, -60))
    floor_y = math_node(nodes, "FLOOR", "Row", (-500, -60))

    div_offset_x = math_node(nodes, "DIVIDE", "Offset X", (-310, 150))
    add_row = math_node(nodes, "ADD", "Row + 1", (-310, -50), value_1=1.0)
    div_row = math_node(nodes, "DIVIDE", "(Row + 1) / Rows", (-120, -50))
    sub_offset_y = math_node(nodes, "SUBTRACT", "Offset Y", (70, -50), value_0=1.0)

    inv_columns = math_node(nodes, "DIVIDE", "1 / Columns", (-310, -280), value_0=1.0)
    inv_rows = math_node(nodes, "DIVIDE", "1 / Rows", (-310, -450), value_0=1.0)

    scale_vec = nodes.new("ShaderNodeCombineXYZ")
    scale_vec.label = "Scale"
    scale_vec.location = (-80, -340)
    set_input_default(scale_vec.inputs.get("Z"), 1.0)

    offset_vec = nodes.new("ShaderNodeCombineXYZ")
    offset_vec.label = "Offset"
    offset_vec.location = (260, 60)
    set_input_default(offset_vec.inputs.get("Z"), 0.0)

    multiply_uv = vector_math_node(nodes, "MULTIPLY", "UV * Scale", (170, -210))
    add_uv = vector_math_node(nodes, "ADD", "UV + Offset", (440, -110))

    link(links, group_in.outputs.get("Index"), mod_x.inputs[0])
    link(links, group_in.outputs.get("Columns"), mod_x.inputs[1])
    link(links, group_in.outputs.get("Index"), div_y.inputs[0])
    link(links, group_in.outputs.get("Columns"), div_y.inputs[1])
    link(links, div_y.outputs[0], floor_y.inputs[0])

    link(links, mod_x.outputs[0], div_offset_x.inputs[0])
    link(links, group_in.outputs.get("Columns"), div_offset_x.inputs[1])
    link(links, floor_y.outputs[0], add_row.inputs[0])
    link(links, add_row.outputs[0], div_row.inputs[0])
    link(links, group_in.outputs.get("Rows"), div_row.inputs[1])
    link(links, div_row.outputs[0], sub_offset_y.inputs[1])

    link(links, group_in.outputs.get("Columns"), inv_columns.inputs[1])
    link(links, group_in.outputs.get("Rows"), inv_rows.inputs[1])
    link(links, inv_columns.outputs[0], scale_vec.inputs.get("X"))
    link(links, inv_rows.outputs[0], scale_vec.inputs.get("Y"))

    link(links, div_offset_x.outputs[0], offset_vec.inputs.get("X"))
    link(links, sub_offset_y.outputs[0], offset_vec.inputs.get("Y"))

    link(links, group_in.outputs.get("UV"), multiply_uv.inputs[0])
    link(links, scale_vec.outputs.get("Vector"), multiply_uv.inputs[1])
    link(links, multiply_uv.outputs.get("Vector"), add_uv.inputs[0])
    link(links, offset_vec.outputs.get("Vector"), add_uv.inputs[1])
    link(links, add_uv.outputs.get("Vector"), group_out.inputs.get("Vector"))

    return group


def link_sprite_nodes(tree, image_node, uv_node):
    texcoord = get_or_create_texture_coordinate(tree)
    principled = get_or_create_principled(tree)
    output = get_or_create_output(tree)

    ensure_link(tree, texcoord.outputs.get("UV"), uv_node.inputs.get("UV"))
    ensure_link(tree, uv_node.outputs.get("Vector"), image_node.inputs.get("Vector"))
    ensure_link(tree, image_node.outputs.get("Color"), principled.inputs.get("Base Color"))

    alpha_input = principled.inputs.get("Alpha")
    if alpha_input:
        ensure_link(tree, image_node.outputs.get("Alpha"), alpha_input)
        material = tree.id_data
        if hasattr(material, "blend_method"):
            material.blend_method = "BLEND"

    ensure_link(tree, principled.outputs.get("BSDF"), output.inputs.get("Surface"))


def get_or_create_texture_coordinate(tree):
    for node in tree.nodes:
        if node.bl_idname == "ShaderNodeTexCoord":
            return node
    node = tree.nodes.new("ShaderNodeTexCoord")
    node.location = (-800, 280)
    return node


def get_or_create_principled(tree):
    for node in tree.nodes:
        if node.bl_idname == "ShaderNodeBsdfPrincipled":
            return node
    node = tree.nodes.new("ShaderNodeBsdfPrincipled")
    node.location = (-80, 180)
    return node


def get_or_create_output(tree):
    for node in tree.nodes:
        if node.bl_idname == "ShaderNodeOutputMaterial":
            return node
    node = tree.nodes.new("ShaderNodeOutputMaterial")
    node.location = (220, 180)
    return node


def setup_index_driver(material, node):
    socket = node.inputs.get("Index")
    if not socket:
        return

    try:
        socket.driver_remove("default_value")
    except (TypeError, RuntimeError):
        pass

    fcurve = socket.driver_add("default_value")
    driver = fcurve.driver
    driver.type = "SCRIPTED"
    driver.expression = "idx"
    while driver.variables:
        driver.variables.remove(driver.variables[0])

    variable = driver.variables.new()
    variable.name = "idx"
    variable.type = "SINGLE_PROP"

    target = variable.targets[0]
    target.id_type = "MATERIAL"
    target.id = material
    target.data_path = "sprite_sheet_settings.sprite_index"


def ensure_group_socket(group, name, direction, socket_type):
    if hasattr(group, "interface"):
        if interface_socket_exists(group, name, direction):
            return
        group.interface.new_socket(name=name, in_out=direction, socket_type=socket_type)
        return

    socket_map = group.inputs if direction == "INPUT" else group.outputs
    if not socket_map.get(name):
        socket_map.new(socket_type, name)


def interface_socket_exists(group, name, direction):
    for item in group.interface.items_tree:
        if getattr(item, "item_type", None) != "SOCKET":
            continue
        if item.name == name and getattr(item, "in_out", None) == direction:
            return True
    return False


def math_node(nodes, operation, label, location, value_0=None, value_1=None):
    node = nodes.new("ShaderNodeMath")
    node.operation = operation
    node.label = label
    node.location = location
    if value_0 is not None:
        set_input_default(node.inputs[0], value_0)
    if value_1 is not None:
        set_input_default(node.inputs[1], value_1)
    return node


def vector_math_node(nodes, operation, label, location):
    node = nodes.new("ShaderNodeVectorMath")
    node.operation = operation
    node.label = label
    node.location = location
    return node


def set_socket_default(node, socket_name, value):
    socket = node.inputs.get(socket_name)
    set_input_default(socket, value)


def set_input_default(socket, value):
    if socket and hasattr(socket, "default_value"):
        socket.default_value = value


def ensure_link(tree, from_socket, to_socket):
    if not from_socket or not to_socket:
        return
    for existing in tree.links:
        if existing.to_socket == to_socket:
            tree.links.remove(existing)
    tree.links.new(from_socket, to_socket)


def link(links, from_socket, to_socket):
    if from_socket and to_socket:
        links.new(from_socket, to_socket)


def register():
    pass


def unregister():
    pass
