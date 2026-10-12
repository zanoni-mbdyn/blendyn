"""Load MBDynLib and the model builder core from an MBDyn source checkout.

The checkout is the add-on preference `mbdyn_source_path`, or else the
environment variable `MBDYN_SRC`. Its `contrib/PythonModelBuilder` provides
the `mbdyn_builder` package, which finds `contrib/PythonPreprocessor` next
to it. Changing the checkout unloads the previous one.
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

_loaded: dict = {"path": None, "error": None}
_MODULES = ("MBDynLib", "MBDynModel", "mbdyn_builder")


def source_path() -> str:
    import bpy
    preferences = bpy.context.preferences.addons.get(__package__.rsplit(".", 1)[0])
    path = getattr(preferences.preferences, "mbdyn_source_path", "") if preferences else ""
    return bpy.path.abspath(path) if path else os.environ.get("MBDYN_SRC", "")


def _unload(builder: Path) -> None:
    for name in list(sys.modules):
        if name.split(".")[0] in _MODULES:
            del sys.modules[name]
    for entry in (str(builder), str(builder.parent / "PythonPreprocessor")):
        while entry in sys.path:
            sys.path.remove(entry)


def builder(path: str | None = None):
    """The `mbdyn_builder` package of the configured checkout; raises RuntimeError if unusable."""
    path = source_path() if path is None else path
    if not path:
        raise RuntimeError("Set the MBDyn source checkout in the Blendyn preferences")
    root = Path(path).expanduser().resolve()
    package = root / "contrib" / "PythonModelBuilder"
    if _loaded["path"] != root:
        if _loaded["path"] is not None:
            _unload(_loaded["path"] / "contrib" / "PythonModelBuilder")
        _loaded.update(path=root, error=None)
        if not (package / "mbdyn_builder").is_dir():
            _loaded["error"] = f"{package} has no mbdyn_builder package"
        else:
            sys.path.insert(0, str(package))
            try:
                importlib.import_module("mbdyn_builder.compiler")
            except Exception as exc:  # report any import failure in the UI
                _loaded["error"] = f"Cannot load the model builder: {exc}"
                _unload(package)
    if _loaded["error"]:
        raise RuntimeError(_loaded["error"])
    return importlib.import_module("mbdyn_builder")


def module(name: str):
    """A module of the loaded builder: model, compiler, catalog, ..."""
    builder()
    return importlib.import_module(f"mbdyn_builder.{name}")


def status() -> tuple[bool, str]:
    try:
        lib = module("library").lib
    except RuntimeError as exc:
        return False, str(exc)
    pydantic = "with" if lib.imported_pydantic else "WITHOUT"
    return True, f"MBDynLib from {Path(lib.__file__).parent} ({pydantic} pydantic)"
