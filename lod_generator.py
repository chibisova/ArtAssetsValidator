import subprocess
import pathlib
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

BLENDER_PATH = os.getenv("BLENDER_PATH")

LOD_SCRIPT = """
import bpy
import sys
import os

fbx_path = sys.argv[sys.argv.index("--") + 1]
output_dir = sys.argv[sys.argv.index("--") + 2]
asset_name = os.path.splitext(os.path.basename(fbx_path))[0]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fbx_path)

original_meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
for obj in original_meshes:
    obj.hide_set(True)
    obj.hide_render = True

lod_ratios = [0.5, 0.25, 0.1]
lod_names = ["LOD1", "LOD2", "LOD3"]

for ratio, lod_name in zip(lod_ratios, lod_names):
    lod_objects = []

    for obj in original_meshes:
        obj.hide_set(False)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        bpy.ops.object.duplicate()
        lod_obj = bpy.context.active_object

        mod = lod_obj.modifiers.new(name="Decimate", type='DECIMATE')
        mod.ratio = ratio
        bpy.ops.object.modifier_apply(modifier="Decimate")

        obj.hide_set(True)
        obj.select_set(False)

        lod_objects.append(lod_obj)

    bpy.ops.object.select_all(action='DESELECT')
    for lod_obj in lod_objects:
        lod_obj.select_set(True)

    out_path = os.path.join(output_dir, f"{asset_name}_LOD{lod_names.index(lod_name) + 1}.fbx")
    bpy.ops.export_scene.fbx(filepath=out_path, use_selection=True)

    bpy.ops.object.delete()

print("LOD generation complete")
"""

def generate_lods(fbx_path: str) -> list[str]:
    fbx_path = str(pathlib.Path(fbx_path).resolve())
    output_dir = str(pathlib.Path(fbx_path).parent.resolve())

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(LOD_SCRIPT)
        script_path = f.name

    print(f"FBX path: {fbx_path}")
    print(f"Output dir: {output_dir}")
    print(f"Script path: {script_path}")

    try:
        result = subprocess.run(
            [
                BLENDER_PATH,
                "--background",
                "--python", script_path,
                "--", fbx_path, output_dir
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        print("=== BLENDER STDOUT ===")
        print(result.stdout[-3000:])
        print("=== BLENDER STDERR ===")
        print(result.stderr[-3000:])
        print("=== RETURN CODE ===")
        print(result.returncode)

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        stem = pathlib.Path(fbx_path).stem
        lods = []
        for i in range(1, 4):
            lod_path = pathlib.Path(output_dir) / f"{stem}_LOD{i}.fbx"
            print(f"Checking for: {lod_path} — exists: {lod_path.exists()}")
            if lod_path.exists():
                lods.append(str(lod_path))

        return lods

    finally:
        os.unlink(script_path)
