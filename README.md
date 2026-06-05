# Sprite Sheet Material Picker

Blender material add-on for selecting cells from a sprite sheet image and driving a shader UV node group with `material.sprite_sheet_settings.sprite_index`.

Tested with Blender 4.5 LTS and Blender 5.1.

https://github.com/user-attachments/assets/cf367699-d7c6-43b8-b086-9cbf3160332d

## Installation

Download the zip file from the [releases page](https://github.com/lyokato/blender_sprite_picker/releases), then drag and drop the zip file into Blender to install the add-on.


<img width="960" height="720" alt="install_addon" src="https://github.com/user-attachments/assets/7af4144b-fb82-4f38-825c-0bdd783106a2" />

Open `Edit > Preferences > Add-ons`, then enable **Sprite Sheet Material Picker**.

## Usage

<img width="960" height="602" alt="material_setting_panel" src="https://github.com/user-attachments/assets/547cd1d4-338b-4453-a989-023cbc51046b" />

Create or select a mesh, then create a material for it. When the material is selected, a **Sprite Sheet Picker** panel appears in the Material properties.

<img width="960" height="494" alt="pick_sprite_texture" src="https://github.com/user-attachments/assets/a1cc0c0f-7f13-4fe3-843a-f3858d24eba1" />

1. Click the folder icon in the panel, then choose the image you want to use as a sprite sheet.

2. Enter the size of one sprite cell in **Cell Width** and **Cell Height**. In this example, the image is 1024 x 1024 px and contains 16 cells arranged in a 4 x 4 grid, so each cell is 256 x 256 px.

The preview in the material panel shows the first cell. At this point, the sprite sheet is selected, but it has not been connected to the material in the 3D Viewport yet.

To show it on the mesh, set up the shader nodes.

<img width="960" height="629" alt="setup_nodes" src="https://github.com/user-attachments/assets/4cbc6116-f6a4-4242-aed2-c5f73132913a" />

Click **Setup Nodes**. The add-on automatically adds the required nodes to the selected material's shader node graph.

The currently selected cell from the sprite sheet is now drawn on the mesh in the 3D Viewport. To see it in the viewport, use **Material Preview** or **Rendered** mode instead of **Solid** mode.

You can freely change the rest of the shader node graph, except for the nodes highlighted in red in the screenshot.

Next, switch to a different cell.

<img width="960" height="596" alt="choose_cell" src="https://github.com/user-attachments/assets/8fb6a9d5-145b-4780-80c2-5e83b5155ab3" />

Click **Choose Cell**. A popup window shows the sprite cells as tiles. Click **Select** on the cell you want to use.

<img width="960" height="682" alt="cell_change" src="https://github.com/user-attachments/assets/3a515e8e-99fb-47e7-ae24-f1053c6ed451" />

The node index value is updated automatically, and the mesh in the 3D Viewport changes to the selected cell.

To animate cell changes, insert keyframes as you switch cells.

<img width="960" height="589" alt="key_for_animation" src="https://github.com/user-attachments/assets/618f7608-258a-4ba6-ae47-5b1c9ea7dd11" />

Click **Insert Key** to add a keyframe on the timeline.

Move to another frame, choose another cell, then click **Insert Key** again. Repeating this creates an animation where the displayed sprite cell changes over time.

## License

Sprite Sheet Material Picker is released under the MIT License. See `LICENSE`.
