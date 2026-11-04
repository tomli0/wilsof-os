# Approved private-image repository baseline

## Policy and scope

The compatibility investigation in issue #16 selected Arch Linux Archive
2026-11-01 core + extra for x86_64, rather than mixing old ABI providers into a
rolling system. This is a bounded experimental baseline, not a maintained
security release. The source of truth is `runtime/repository-snapshot.py`:

    https://archive.archlinux.org/repos/2026/11/01/$repo/os/$arch

The generated configuration has no Include, custom downloader, extra repository,
rolling fallback or environment override. Official packages require trusted
signatures (`Required TrustedOnly DatabaseOptional`), with CheckSpace retained.
DatabaseOptional does not mean unsigned official packages are accepted. The
pre-existing effective local-file policy (`LocalFileSigLevel = Optional`) is
retained only alongside the unchanged independently pinned private package
contracts; these inputs are not represented as officially signed packages.
No dependency bypass, force overwrite, fake SONAME link or private rebuild is added.

This policy applies to separately prepared image and target roots. It does not
configure/downgrade the builder operating system. Archiso 92 with its matching
releng is the intended tool; 91 remains explicitly supported, and other major
versions are refused. Matching metadata is not runtime or security acceptance.

## Producer and consumer chain

1. `prepare-iso.py` stages identical build/live pacman.conf and a dated live
   mirrorlist, plus `REPOSITORY-SNAPSHOT.json`. The runtime helper and existing
   package verifier are included through the explicit image-file allowlist.
2. `build-inputs.py` checks the exact dated policy and the matching boot contract
   before making `.build-inputs`. Its existing empty local DB resolves all image
   dependencies, including the private package's full versioned constraints.
   Every archive must match the DB SHA256, .PKGINFO and trusted detached signature.
3. Only the builder's generated config is subsequently converted to the retained
   local `file://` closure. The image's own configuration stays dated HTTPS;
   no build-machine cache/keyring path is embedded as a live repository.
   `BUILD-INPUTS.json` records both the repository and early-KMS boot contracts.
4. Before loading the disk-handling API or formatting anything, the interactive
   installer checks live policy and preflights its own complete official closure
   in a new temporary database. It copies only existing accepted public keyring
   material, uses the same signature verifier, includes private ABI constraints,
   and rejects official Hyprland fallback. The package receipt is included in
   the reviewed plan identity. Policy is checked again before disk operations.
5. Archinstall 4.5 pacstrap consumes live `/etc/pacman.conf`. After minimal
   installation, the adapter explicitly stages the approved configuration in the
   fresh target and checks every resolved official package name/version, before
   private package replacement. It saves `REPOSITORY-INPUTS.json`. Provisioning
   refuses policy drift before package work and after successful configuration.
6. Existing private Hyprland/Hypridle archives, names, hashes, binary checks,
   local transaction ordering and refusal/fallback rules remain unchanged.
   Hypridle is still an independent required input, never supplied through the
   private-Hyprland opt-in. No private artifact or locator belongs in Git/CI.

A missing/corrupt manifest, changed date, rolling mirror, weaker policy or symlink
is an error, not an invitation to repair or silently replace the live policy.
Only explicit materialization of a fresh image/target writes configuration;
validation itself is side-effect free. Runtime temporary files are not builder
OS configuration changes.

## Resource, reproducibility and maintenance limits

Target preflight downloads a complete signed official closure into a temporary
`/var/tmp/wilsof-target-inputs-*` directory, then removes it. Pacstrap downloads
again. This is intentionally simple and fails before formatting on preflight
errors, but needs archive bandwidth and enough writable live storage/RAM for
the cache. The first native test must measure this footprint; the old 4 GiB VM
example is not acceptance of the new full-preflight requirement. No offline
installer or low-memory guarantee is claimed. The preflight does not install
packages into the live system or synchronize its installed-package DB.

A dated repository and captured package/keyring inputs make selection traceable;
they do not establish byte-identical ISO output, full native dependency
acceptance or security. Archive availability, accepted key/trust state, complete
libalpm resolution, loader compatibility and the real installed target still
need native evidence. Existing wrapper checks remain mandatory.

`pacman -Syu` in the installed system remains on this date, normally a no-op for
official package versions. This baseline receives no later security fixes.
Advancing it requires a coherent repository-date change, complete dependency/
signature/ABI checks and VM regression; it is not a two-library downgrade or a
mirror-only edit. Rebuilding the retained private package requires separate
approval if no suitably maintained coherent baseline remains compatible.

## Verification and first-build authorization

Nonprivileged tests cover real tagged releng91/92 inputs, explicit early KMS,
memtest paths, version/contract mismatch, idempotence, exact build/live policy,
frozen-build separation, drift/symlink refusals, full private constraints in the
solver request, target signature/dependency failures before formatting, review
binding, target policy persistence and installed name/version comparison.
Package-manager, GPG and disk operations are substituted in these source tests;
they are not native acceptance.

Before the first private build is authorized:

1. Approve the exact reviewed feature commit/export, private experimental scope,
   existing independent package contracts, image version and source epoch.
   Source publication alone is not build approval or AS-02 acceptance.
2. Separately authorize any missing builder-tool/privilege setup. Verify actual
   Archiso 92 and matching releng, accepted public keyring, required tools,
   dedicated new work/profile/output paths, at least the documented 25 GiB free
   build space and sufficient measured memory/PID headroom. Do not downgrade the
   builder or turn this source change into an implicit package installation.
3. Establish the VM112 isolation boundary: preserved Fedora disk must not be
   exposed to build/installer work, no reference VM113 or physical disks, host
   homes or credentials. Any required disk detachment/protection or VM changes
   need separate explicit approval; none are performed by this change.
4. Verify both retained private inputs against their existing independent custody
   records. Preserve bytes/pins and reject missing input, signature failure,
   dependency failure or unexpected repository fallback. Do not publish artifacts.
5. Require complete native libalpm/signature preflight before `mkarchiso` proceeds;
   stop and preserve evidence on failure. Retained-package ABI/loadability is
   still an explicit native gate, not established by source tests or metadata.
6. Authorize one exact private build attempt separately. Retain inputs/logs/ISO
   and checksum privately. Live boot, disposable blank-disk installation, normal
   login, desktop/lock security, AS-02 independent review, updates and physical
   client checks are subsequent separately authorized acceptance gates.

The investigation's evidence and recommendation are in issue #16. This document
is an implementation contract, not evidence that an ISO was built or accepted.
