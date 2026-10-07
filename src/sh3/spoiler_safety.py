"""Preserve required-step reachability while Archipelago prunes SH3 spoilers.

SH3 has an irreversible Hospital transition. The visit-event ordering safeguard
can also change its active prerequisites as inventory is removed. AP's ordinary
``can_beat_game`` may stop at the goal without visiting every retained spoiler
step. That is not a sufficient deletion test for these rules.

Only during this multiworld's create_playthrough call, a supplied retained-
location set must be replayable in full before a deletion is accepted. Calls
without a retained-location set retain their ordinary behavior. The original
playthrough builder, final reachability check, and all world rules are unchanged.
No AP installation files or process-global classes are patched.
"""
from __future__ import annotations

from types import MethodType
from typing import TYPE_CHECKING, Iterable

from BaseClasses import CollectionState

if TYPE_CHECKING:
    from BaseClasses import Location, MultiWorld

_MISSING = object()


def retained_steps_reachable(
    multiworld: MultiWorld,
    starting_state: CollectionState | None,
    locations: Iterable[Location],
) -> bool:
    """Prove both the goal and every retained step using simultaneous spheres.

    The caller supplies AP's candidate spoiler locations, not the entire world.
    A copied prefix state includes steps already collected in earlier spheres.
    No collection is performed until the entire next sphere has been evaluated,
    matching the final spoiler rebuild even for items sent between players.
    ``locations_checked`` is only replay bookkeeping here, never an access rule.
    """
    state = starting_state.copy() if starting_state is not None else CollectionState(multiworld)
    remaining = set(locations).difference(state.locations_checked)
    while remaining:
        sphere = {location for location in remaining if state.can_reach(location)}
        if not sphere:
            return False
        for location in sphere:
            if location.item is None:
                return False
            state.collect(location.item, True, location)
        remaining.difference_update(sphere)
    return multiworld.has_beaten_game(state)


def install_spoiler_safety(multiworld: MultiWorld) -> None:
    """Wrap just this spoiler instance, after filling, once per multiworld."""
    spoiler = multiworld.spoiler
    if getattr(spoiler, "_sh3_retained_steps_safety", False):
        return
    original_create_playthrough = spoiler.create_playthrough

    def create_playthrough_with_retained_steps(_spoiler, *args, **kwargs):
        previous_instance_method = multiworld.__dict__.get("can_beat_game", _MISSING)
        original_can_beat_game = multiworld.can_beat_game

        def can_beat_with_retained_steps(_multiworld, starting_state=None, locations=None):
            if locations is None:
                return original_can_beat_game(starting_state)
            return retained_steps_reachable(_multiworld, starting_state, locations)

        multiworld.can_beat_game = MethodType(can_beat_with_retained_steps, multiworld)
        try:
            # Keep AP's own builder and its final failure checks in control.
            return original_create_playthrough(*args, **kwargs)
        finally:
            # Restoration is required on both success and a generation error.
            if previous_instance_method is _MISSING:
                del multiworld.can_beat_game
            else:
                multiworld.can_beat_game = previous_instance_method

    spoiler.create_playthrough = MethodType(create_playthrough_with_retained_steps, spoiler)
    spoiler._sh3_retained_steps_safety = True
