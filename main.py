from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from agents import validate_asset, rename_asset, rename_texture, notify_slack
from mesh_utils import get_mesh_data
import pathlib
import os
import time
from logger import logger
from reporter import add_entry
from lod_generator import generate_lods


TEXTURE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tga', '.tiff', '.exr')

from lod_generator import generate_lods

def process_asset(fbx_path: str):
    logger.info(f"Found: {fbx_path}")
    logger.info("Validating...")

    try:
        mesh_data = get_mesh_data(fbx_path)
    except Exception as e:
        logger.error(f"Could not read mesh data — {e}")
        return

    try:
        result = validate_asset(fbx_path, mesh_data)
    except Exception as e:
        logger.error(f"Validation agent failed — {e}")
        return

    logger.info(result)
    new_name = None
    final_path = fbx_path

    if result.startswith("FAIL"):
        try:
            notify_slack(fbx_path, result)
            logger.info("Slack notified.")
        except Exception as e:
            logger.error(f"Slack notification failed — {e}")

        try:
            new_name = rename_asset(fbx_path, result)
            new_name = pathlib.Path(new_name).stem + ".fbx"
            new_path = pathlib.Path(fbx_path).parent / new_name
            pathlib.Path(fbx_path).rename(new_path)
            final_path = str(new_path)
            logger.info(f"Renamed to: {new_name}")
        except Exception as e:
            logger.error(f"Rename failed — {e}")

    # generate LODs regardless of pass/fail — use final_path after rename
    logger.info("Generating LODs...")
    try:
        lods = generate_lods(final_path)
        for lod in lods:
            logger.info(f"Generated: {lod}")
    except Exception as e:
        logger.error(f"LOD generation failed — {e}")

    add_entry(fbx_path, result, new_name, mesh_data, entry_type="mesh")

def process_texture(tex_path: str):
    filename = pathlib.Path(tex_path).name
    original_ext = pathlib.Path(tex_path).suffix
    logger.info(f"Texture detected: {filename}")
    new_name = None

    try:
        new_name = rename_texture(tex_path)
        new_name = pathlib.Path(new_name).stem + original_ext
        new_path = pathlib.Path(tex_path).parent / new_name
        pathlib.Path(tex_path).rename(new_path)
        logger.info(f"Renamed to: {new_name}")
    except Exception as e:
        logger.error(f"Texture rename failed — {e}")

    add_entry(tex_path, "TEXTURE", new_name, entry_type="texture")


class AssetHandler(FileSystemEventHandler):
    def on_created(self, event):
        filename = pathlib.Path(event.src_path).name
        if event.src_path.endswith('.fbx'):
            if '_LOD1' in filename or '_LOD2' in filename or '_LOD3' in filename:
                logger.info(f"Skipping LOD file: {filename}")
                return
            process_asset(event.src_path)
        elif event.src_path.endswith(TEXTURE_EXTENSIONS):
            process_texture(event.src_path)

def scan_existing(folder: str):
    logger.info("Scanning existing files...")
    for filename in os.listdir(folder):
        full_path = os.path.join(folder, filename)
        if filename.endswith('.fbx'):
            if '_LOD1' in filename or '_LOD2' in filename or '_LOD3' in filename:
                continue
            process_asset(full_path)
        elif filename.endswith(TEXTURE_EXTENSIONS):
            process_texture(full_path)

observer = Observer()
observer.schedule(AssetHandler(), path='./watch_folder', recursive=False)
observer.start()

scan_existing('./watch_folder')
print("\nWatching for new files... (Ctrl+C to stop)")

try:
    while True: time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
