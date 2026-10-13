# HOT ATL2TM

The `.atlpart` files are the maintained source of the ATL2TM higher-order transformation. `ATL2TM.generated.atl` is assembled from them and is the file passed to the ATL runtime. Do not edit the generated file directly.

The folders group declarations by purpose: shared helpers in `common/`, the four main transformation stages in `steps/`, and lazy-rule, `resolveTemp`, and provenance support in `extensions/`. ATL requires a single module, so `build.py` restores the original declaration order using the numbered `-- @hot-atl2tm-part` markers. Keep each marker with its following declaration when moving code. Marker numbers must remain unique and consecutive.

From this directory, run `python build.py` after editing a fragment. Run `python build.py --check` to verify that the generated file is current. The formal-verification Python runner rebuilds automatically before invoking ATL2TM. Java tests use the generated file; rebuild it before running those tests directly.
