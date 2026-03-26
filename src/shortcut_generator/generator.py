"""Generate .shortcut files and write them to disk."""
import os
import plistlib
from src.shortcut_generator.shortcuts import (
    build_setup_shortcut,
    build_trip_start_shortcut,
    build_trip_end_shortcut,
)


def generate_shortcuts(output_dir: str = "output") -> list[str]:
    os.makedirs(output_dir, exist_ok=True)
    shortcuts = {
        "Travel Tracker Setup": build_setup_shortcut(),
        "Trip Start": build_trip_start_shortcut(),
        "Trip End": build_trip_end_shortcut(),
    }
    written = []
    for name, shortcut_data in shortcuts.items():
        path = os.path.join(output_dir, f"{name}.shortcut")
        with open(path, "wb") as f:
            plistlib.dump(shortcut_data, f, fmt=plistlib.FMT_BINARY)
        written.append(path)
    return written
