"""Shared launcher contract. Game-specific clients retain their own runtime state.

Future adapters implement launch_client(*args: str) and register an import path.
Adding a name here does not provide game support: each adapter must implement
its own process detection, checks, grants, save handling and native setup.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from importlib import import_module

CLIENT_NAME = "Silent Hill 3 Client"
CLIENT_BRAND = "SHAP"
ADAPTER_API_VERSION = 1

@dataclass(frozen=True)
class GameAdapter:
    key: str
    game_name: str
    module: str
    entry_point: str = "launch_client"
    api_version: int = ADAPTER_API_VERSION

_ADAPTERS: dict[str, GameAdapter] = {}

def register_adapter(adapter: GameAdapter) -> None:
    if adapter.api_version != ADAPTER_API_VERSION:
        raise ValueError(f"Unsupported Silent Hill adapter API: {adapter.api_version}")
    if not adapter.key or not adapter.module or not adapter.game_name:
        raise ValueError("Adapter key, game name and module are required")
    existing = _ADAPTERS.get(adapter.key)
    if existing is not None and existing != adapter:
        raise ValueError(f"Silent Hill adapter already registered: {adapter.key}")
    _ADAPTERS[adapter.key] = adapter

def available_adapters() -> tuple[GameAdapter, ...]:
    return tuple(_ADAPTERS.values())

register_adapter(GameAdapter("sh3", "Silent Hill 3", __package__ + ".client"))

def launch_client(*args: str) -> None:
    # Parse only routing; connection URLs and all game-specific options pass
    # through unchanged. Existing SH3 launch links still default to SH3.
    parser = argparse.ArgumentParser(prog=CLIENT_NAME, add_help=False, allow_abbrev=False)
    parser.add_argument("--game", choices=tuple(_ADAPTERS), default="sh3")
    selected, remaining = parser.parse_known_args(args)
    adapter = _ADAPTERS[selected.game]
    entry = getattr(import_module(adapter.module), adapter.entry_point)
    entry(*remaining)
