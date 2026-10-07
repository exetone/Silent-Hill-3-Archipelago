from __future__ import annotations

import hashlib
import os
import pkgutil
import tempfile

from .silent_hill_client import CLIENT_NAME

from worlds.LauncherComponents import Component, Type, components, icon_paths, launch


def get_sh3_icon_path() -> str:
    """Return a normal filesystem path for the SH3 icon bundled in this APWorld."""
    data = None
    try:
        data = pkgutil.get_data(__package__, "sh3.png")
    except (OSError, ImportError):
        data = None

    if not data:
        return r"data/icon.png"

    digest = hashlib.sha256(data).hexdigest()[:16]
    path = os.path.join(tempfile.gettempdir(), f"sh3ap_icon_{digest}.png")
    try:
        current = None
        if os.path.isfile(path):
            with open(path, "rb") as existing:
                current = existing.read()
        if current != data:
            with open(path, "wb") as out:
                out.write(data)
        return path
    except OSError:
        return r"data/icon.png"


# Kivy's Launcher card is given a regular local path instead of an APWorld URI.
icon_paths["sh3"] = get_sh3_icon_path()


def run_client(*args: str) -> None:
    from .silent_hill_client import launch_client
    launch(launch_client, name=CLIENT_NAME, args=args)


components.append(Component(
    CLIENT_NAME,
    func=run_client,
    game_name="Silent Hill 3",
    component_type=Type.CLIENT,
    supports_uri=True,
    icon="sh3",
))
