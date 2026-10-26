"""metadata for research records numeric measurements are unchanged"""

import json
import re
from pathlib import Path
from typing import Any


def portable_profile_path(value: str) -> str:
    """Retain a logical source location without publishing an absolute host path"""
    normalized = value.replace("\\", "/")
    if not (normalized.startswith("/") or re.match(r"^[A-Za-z]:/", normalized)):
        return value
    for marker, prefix in (
        ("/site-packages/", "site-packages/"),
        ("/langgraph/checkpoint/", "langgraph/checkpoint/"),
        ("/benchmarks/issue_9410/", "benchmarks/issue_9410/"),
        ("/Lib/", "stdlib/"),
    ):
        if marker in normalized:
            return prefix + normalized.rsplit(marker, 1)[1]
    match = re.search(r"/lib/python\d+\.\d+/(.+)", normalized)
    return "stdlib/" + match[1] if match else "<host>/" + normalized.rsplit("/", 1)[-1]


def portable_record(value: Any) -> Any:
    """Copy records, replacing only executable/editable/source path metadata"""
    if isinstance(value, list):
        return [portable_record(item) for item in value]
    if isinstance(value, dict):
        return {
            key: (
                "<host-python>"
                if key == "executable"
                else "<editable-project>"
                if key == "editable_project_location"
                else portable_profile_path(item)
                if key == "file" and isinstance(item, str)
                else portable_record(item)
            )
            for key, item in value.items()
        }
    return value


def write_record(path: Path, record: Any) -> None:
    """Write json after timing without changing num fields"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(portable_record(record), separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
