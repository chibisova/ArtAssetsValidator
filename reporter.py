import json
import pathlib
from datetime import datetime

report_dir = pathlib.Path("reports")
report_dir.mkdir(exist_ok=True)

report_filename = report_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

report_data = []

def add_entry(file_path: str, validation_result: str, new_name: str = None, mesh_data: dict = None, entry_type: str = "mesh"):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": entry_type,
        "original_filename": pathlib.Path(file_path).name,
        "validation": "PASS" if validation_result.startswith("PASS") else "FAIL",
        "validation_detail": validation_result,
        "renamed_to": new_name
    }
    if entry_type == "mesh" and mesh_data:
        entry["mesh_data"] = mesh_data

    report_data.append(entry)
    _write()

def _write():
    with open(report_filename, "w") as f:
        json.dump(report_data, f, indent=2)
