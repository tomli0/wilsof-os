# Wilsof Command Center (development candidate)

Source baseline: `19a68247b0f406965db25e6ea950ce12ed0707f2`, the verified head of PR #43. The feature branch is stacked on `fix/internal4-completion`; no cherry-pick, merge, modification of #42/#43, or ISO build is needed. Stabilization/release gates remain separate.

## Integration decision

The packaged target is `dux-shell 2.0.0-1`. Its embedded QML corresponds to the inspected Dux source tree `9b413296b16721f7679fb62e624cb1ed2433fa58` (the upstream `v2.0.0` source used by the baseline). See upstream `quickshell/Services/AppSearchService.qml`, `SessionService.qml`, `PluginService.qml`, and `Modals/Common/DModal.qml` at that revision.

The native Spotlight launcher provides apps/actions and settings search, but its provider plugin API returns rows to upstream-owned layout/default sections. It cannot replace the empty-query view with exactly three Wilsof shortcuts and seven shallow navigation entries. We therefore add a DMS plugin modal, not an independent launcher executable or framework. It reuses DMS DModal, focused-screen selection, focus grab, theme, desktop-entry search/launch, settings search/navigation, and confirmation-protected Power menu. Existing Spotlight remains the fallback if our IPC marker is absent. Profile plugin/top bar/control center and their triggers remain unchanged.

The manifest's `daemon` component is an Item inside the already-running DMS process. It installs no service, socket listener, network backend or additional daemon. A short-lived Python process runs only for an eligible query, is cancelled on query change/close, and rejects stale results using generation and query equality. No generic shell execution of search text occurs. Application desktop entries use DMS launch helpers, not a handwritten Exec parser. File paths use encoded file URIs, passed as one argument to `xdg-open`.

## Local home-name search

`wilsof-file-search` has no index or persistent state. Breadth-first home traversal excludes all hidden paths, symlinks, other filesystems, Trash, node_modules, build/dist/target, vendor, Python caches and virtual environments. No content or EXIF reads, no external queries. Defaults: 80 ms traversal budget, 20,000 entries, 40 results; local process startup, slow filesystem calls and UI rendering are additional costs. These bounds deliberately make results best-effort, not exhaustive. The UI discloses bounded/unreadable results. Large/generated directories cannot cause a whole-filesystem index.

Known limitation: late matches can be omitted once a bound is reached; refine the query or use Nautilus for exhaustive browsing. Mounted storage and hidden files are intentionally omitted. Default file scope is home, not root. Common XDG folders must actually exist to appear.

## Deployment and rollback

The existing confined, backup-producing `runtime/desktop.py` installer distributes explicit manifest files. New homes enable the plugin. Existing `plugin_settings.json` bytes/explicit disables and personal DMS settings are preserved; enable Wilsof Command Center in DMS Plugins when upgrading an existing home. No automatic migration overwrites manual settings.

`Super+Space` still invokes the same `wilsof-search toggle` wrapper. The wrapper accepts only `toggle`, requires `WILSOF_COMMAND_CENTER_OK`, and falls back to Spotlight on missing/disabled/broken plugin. Disable the plugin to revert the launcher immediately. DMS-managed Hyprland modules are not edited.

## Acceptance boundary

Automated model tests execute the exact QML JavaScript model under Node; selection is one index into the displayed array, retained by stable ID when async file rows arrive. Empty results select -1. Mouse activation snapshots the clicked row; Enter snapshots the same highlighted array entry. File tests cover exclusions, literal shell-like filenames, symlink escape and traversal bounds. Deployment uses existing confinement/preservation tests.

Real QEMU evidence, measured performance and remaining GUI/physical gates are recorded in the dated development report. Model/search-completion time is not time-to-visible-frame. The 150 ms target is not certified from TCG tests. Until the whole acceptance matrix passes this is a draft development candidate, not release-ready universal search.
