# Source availability — 1.0.2

All Python world/client/installer code and the PowerShell/batch tools are available.
The accompanying GitHub source archive includes those sources, tests, native patch
scripts, exact payload hashes and a reproducible APWorld packaging tool.

The nine legacy ASI plugins are not source-complete: their original C/C++ projects
are absent. The UI alignment patch and Reset Keybinds relocation repair can be
reviewed as binary patch scripts, but these do not reconstruct the plugins' source.
The five supplied third-party PC Fix files likewise do not have source in this repo.

The source-only archive excludes executable binaries and binary assets. To rebuild
the distributed APWorld, the packaging script reads the exact hash-verified binary
payloads from the supplied 1.0.2 APWorld. This repackages native binaries; it does not
compile them from source. No claim of a complete open-source native build is made.

No project-wide source license was supplied, so no new license is assigned here.
Existing third-party notices remain intact. Bundling files does not establish their
redistribution license or Archipelago public-submission approval.
