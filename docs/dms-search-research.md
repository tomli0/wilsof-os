# DMS providers and privacy-safe path to universal search

Updated: 2026-10-16 UTC

Issue: #7

## Decision boundary

Wilsof must not call the existing DMS Spotlight integration “universal search” yet. Current repository evidence establishes only the application/DMS-tools entry point and records that the `dsearch` file provider was absent on the test VM. No package was installed, no service was enabled, and no target configuration or session state was changed for this research.

## Upstream DMS capability evidence

DMS documents Spotlight IPC with application and file entry modes (`openWith apps` and `toggleWith files`):

- https://danklinux.com/docs/dankmaterialshell/keybinds-ipc
- https://github.com/AvengeMedia/DankMaterialShell/commit/39220704883f2766facb541623fcdbb54e3ea907 (commit-pinned upstream implementation adding Spotlight `openWith`/`toggleWith` modes)

The upstream DMS project describes Spotlight as searching applications, `dsearch`-backed files, emojis, running windows, calculator results and commands; it also describes a plugin system:

- https://github.com/AvengeMedia/DankMaterialShell

This is upstream capability documentation, not validation on Wilsof's locked target.

| Need | Upstream support | Wilsof status | Claim allowed now |
| --- | --- | --- | --- |
| Installed applications | DMS Spotlight | Visually observed as the default entry point | Application search is supported and locally invoked |
| Files | DMS identifies `dsearch` as its file-search dependency | `dsearch` was reported absent on the test VM | Not available on the target; no file-search claim |
| Open/running windows | DMS upstream describes running-window results | Not exercised in Wilsof | Capability is upstream-documented only |
| Settings | DMS exposes a separate Settings IPC surface; no evidence that arbitrary settings are a Spotlight provider | `Super+I` opens Settings; no settings-result search test | Direct settings entry only, not searchable-settings coverage |
| Actions/commands | DMS upstream describes command results | No Wilsof test of command scope, confirmation, or destructive-action behavior | No action-search claim; system power remains outside this scope |
| Plugins | Upstream documents extensibility | No plugin installed or evaluated | No plugin capability claim |

## `dsearch` provenance, compatibility, and maintenance signals

The relevant `dsearch` is AvengeMedia/danksearch, not the unrelated `icampana/dsearch` DevDocs terminal tool. Upstream identifies it as an MIT-licensed Go filesystem-search service and documents it as the DMS file-search dependency:

- https://github.com/AvengeMedia/danksearch
- https://github.com/AvengeMedia/DankMaterialShell

At research time the upstream repository was public, non-archived, and had a current stable release `v1.6.0` (2026-09-03) with Linux amd64 and arm64 release assets. Its release history is available at:

- https://github.com/AvengeMedia/danksearch/releases

For Arch, the official Dank Linux installation page names `dsearch-bin` and `dsearch-git` as AUR options; they are user-contributed packages rather than official Arch repositories. The Arch AUR RPC listed `dsearch-bin` version `1.6.0-1`, providing/conflicting with `dsearch`, and `dsearch-git` as a source build. Treat either AUR package as a separate supply-chain approval decision; do not use an unpinned curl pipeline.

- https://danklinux.com/docs/1.5/danksearch/installation
- https://aur.archlinux.org/packages/dsearch-bin
- https://aur.archlinux.org/packages/dsearch-git

Compatibility is plausible but unproven: Wilsof uses Arch, Hyprland, DMS 1.6.3 and a user-session service model; upstream documents DMS file results through `dsearch` and `dsearch` documents Linux/static release artifacts. Compatibility must still be demonstrated with the exact DMS and `dsearch` package versions on an approved disposable target.

## Data and privacy assessment

Confirmed from the upstream example configuration:

- `dsearch` stores its index under `$XDG_CACHE_HOME/danksearch/index` by default and configuration under `~/.config/danksearch/config.toml`.
- It can index configured paths, including a home directory, and can extract text from configured text extensions and EXIF metadata when enabled.
- The example binds its server to `127.0.0.1:43654`.
- The example's coverage and exclusions are configuration-dependent; it shows an indexed home path, hidden-file controls, depth limits, excluded directories and `max_file_bytes`.

Source: https://github.com/AvengeMedia/danksearch/blob/v1.6.0/config.example.toml

Therefore “local” does not mean “minimal data collection.” A broad home-directory index may create searchable local copies of file names, text content and image metadata in the user cache. A loopback bind is host-wide, not automatically user-scoped: upstream issue #28 reports that its HTTP API can be reachable by every local account without per-user authentication (https://github.com/AvengeMedia/danksearch/issues/28). The cited configuration does not by itself establish encryption at rest, effective cross-account access control, deletion semantics, telemetry behavior, or every network behavior. Those remain unconfirmed and must not be asserted without a version-pinned source/audit and runtime observation.

Privacy-safe default for any later evaluation:

1. Use an explicitly approved disposable target; do not install on the current test VM or a personal machine.
2. Pin the exact package/release, repository URL, version, checksum/signature evidence and installer source before approval.
3. Start with a deliberately small non-sensitive fixture directory, not `$HOME`; set explicit depth, file-size and exclude rules.
4. Disable text extraction and EXIF extraction for the first functional test unless a specific acceptance test requires them.
5. Verify the service bind address, index/config paths, permissions, logs and outbound network behavior before testing broader data.
6. Remove the service, configuration and index after the experiment, then verify removal.

## Non-installing next steps and acceptance gate

No installation is proposed by this document. Before a future change can claim universal search, require explicit approval for a disposable-target plan and demonstrate all of the following:

1. Files: DMS returns only the approved fixture files through `dsearch`; configured exclusions and disabled content/EXIF extraction behave as intended.
2. Windows: an open window appears in Spotlight and selects/focuses correctly.
3. Settings: a defined settings-search provider exists and returns an approved settings result, or the product wording remains “open Settings,” not “search settings.”
4. Actions: permitted non-destructive commands are enumerated and tested; destructive power/session actions are excluded or require their documented confirmation without executing them.
5. Privacy: index location, configured paths, extracted fields, local listener, log contents and cleanup are inspected on the exact versions used. On a multi-user target, a second local account must be unable to query the first account’s index, or an effective authentication/isolation mitigation must be demonstrated before broader or sensitive indexing.
6. Physical client: the MacBook → Omarchy → Proxmox input path must verify `Super+Space`, query typing, arrows, Enter and Esc. That check cannot be completed from this worker.

Until those gates are met, the accurate product statement is: Wilsof provides local application/DMS-tool entry through Spotlight; file, window, settings and action search are not demonstrated as a universal search experience.
