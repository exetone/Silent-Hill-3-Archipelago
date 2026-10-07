# Silent Hill 3 Archipelago 1.0.2

Close SH3 and its client. Install sh3_1.0.2.apworld in Archipelago/custom_worlds,
removing older SH3 APWorld copies. Open Silent Hill 3 Client and select your existing
PC game folder. The supported executable is checked before setup changes files.

The client installs the five supplied PC Fix files automatically, including their
INI. A separate Steam006 download/presence gate is no longer part of setup. Existing
replaced files are backed up, and later INI edits are preserved. The four settings
needed for AP save format and Normal/Normal difficulty are still applied.
XInput Plus remains optional and is not included.

Upgrading from experimental standalone builds removes their plugin/config/marker
and restores the earliest verified display backup where available. Existing AP and
Vanilla save profiles are retained. Keep the game closed during this migration.

Version 1.0.1 seeds remain supported when their catalogue, location, travel and
script protocols match. Version 1.0.2 does not change item/location IDs or logic.

The gameplay-overlay row and the keybind/reset mouse rectangles are aligned with
the connection/keybind column. Windows rendering has not been confirmed for this
build. Sassy's AP-only launch report is not marked resolved without a new live test.

See SOURCE_AND_COMPLIANCE.md for source availability and third-party attribution.

The client installs the supplied custom title image with the release version in
the bottom-left corner. Close SH3 before reopening the client after upgrading.
The original local picture archive is backed up under
`scripts/SH3AP_Mode_Data/TitleBackups` before replacement. An unsupported texture
layout skips the cosmetic update and reports a warning in the client log.
