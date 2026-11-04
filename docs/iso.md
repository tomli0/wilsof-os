# Internal test ISO design

## Decision and current status

Wilsof overlays a separately supplied, matching Archiso 91 or 92 `releng` profile.
Archiso 92 is the intended builder for the approved dated baseline; unknown
versions and tool/releng-major mismatches are refused. The builder
requires a reviewed archive, explicit source marker, pinned internal Hypridle
artifact, fixed epoch/version and isolated work/output paths. Source remediation
is not authorization to build: Integration3's AS-02 deployment blocker remains.
Only x86_64 UEFI/systemd-boot is configured; BIOS/Secure Boot are not certified.

## Live and installed environments

The live image intentionally autologins an unlocked ephemeral `live` graphical
session. It is not suitable for private work. A fresh recovery-console password
is generated at boot, never baked into the image; root remains locked. No SSH
login or automatic disk installation is enabled. The launcher includes an
explicit installer for an eligible disposable blank target. This is no longer
a no-installer image. Installed users use normal password login and their
separate installed-session policy. See the authoritative
[internal test runbook](internal-test-runbook.md) for recovery, installation,
updates, remaining native blockers and physical-client acceptance.

## Separate build environment and isolation boundary

Use only a separately authorized disposable x86_64 Arch build machine. Never
use the Hermes/Proxmox host, VM 113, a workstation with private data, or an
installation target. No original QA disks, physical block devices, credentials,
private homes or SSH material may be exposed to it. Isolation is an external
prerequisite, not a sandbox created by this wrapper.

Required tools: supported Archiso 91/92, pacman/pacman-conf, Python 3, GnuPG and bsdtar, with
an accepted public Arch keyring and at least 25 GiB available on the dedicated
build filesystem. Record actual free space with `df -h /srv` before starting.
Do not install/upgrade tools as an implicit part of a build attempt.

Work must be new, output absent or empty, and the derived profile
`${WILSOF_ISO_WORKDIR}-profile` must be new. All three canonical paths must be
pairwise disjoint and disjoint from source, releng and the supplied package.
Equality, nesting, symlink aliases into an input/another output, dangling
symlinks and file-valued output are refused before any output is created.
The profile is a sibling of work, not `work/profile`.

## Safe, reversible build-only test — separately authorized future use

1. In a non-root shell on that isolated machine, verify `uname -m` is `x86_64`,
   `command -v mkarchiso`, `pacman -Q archiso` (92 for this baseline), the accepted releng/keyring,
   available capacity and clean reviewed checkout. Set `WILSOF_APPROVED_COMMIT`
   to the independently approved full commit, `WILSOF_EXPORT_ROOT` to a new
   absolute archive-export path, `WILSOF_HYPRIDLE_PACKAGE` to the existing verified
   artifact, and `WILSOF_ISO_VERSION` to a unique internal version. Do not reuse
   previous artifacts. The source marker alone does not authenticate an archive.

2. Export the exact reviewed source, create its marker and explicitly pass every
   required value through sudo. This entire command block is regression-tested
   in a sanitized scratch fixture with substituted build/package boundaries:

<!-- build-command:start -->
       set -euC
       : "${WILSOF_APPROVED_COMMIT:?Set the independently approved full source commit}"
       : "${WILSOF_EXPORT_ROOT:?Set a new absolute archive-export directory}"
       : "${WILSOF_HYPRIDLE_PACKAGE:?Set the exact verified internal package path}"
       : "${WILSOF_ISO_VERSION:?Set a unique internal image version}"
       : "${WILSOF_ISO_WORKDIR:=/srv/wilsof-iso-work}"
       : "${WILSOF_ISO_OUTDIR:=/srv/wilsof-iso-out}"
       : "${WILSOF_ARCHISO_RELENG:=/usr/share/archiso/configs/releng}"
       test -z "$(git status --porcelain)"
       test "$(git rev-parse HEAD)" = "$WILSOF_APPROVED_COMMIT"
       SOURCE_DATE_EPOCH=$(git show -s --format=%ct "$WILSOF_APPROVED_COMMIT")
       mkdir -- "$WILSOF_EXPORT_ROOT"
       git archive --format=tar "$WILSOF_APPROVED_COMMIT" > "$WILSOF_EXPORT_ROOT.tar"
       tar -xf "$WILSOF_EXPORT_ROOT.tar" -C "$WILSOF_EXPORT_ROOT"
       printf '%s\n' "$WILSOF_APPROVED_COMMIT" > "$WILSOF_EXPORT_ROOT/SOURCE_COMMIT"
       sudo WILSOF_ISO_WORKDIR="$WILSOF_ISO_WORKDIR" \
           WILSOF_ISO_OUTDIR="$WILSOF_ISO_OUTDIR" \
           WILSOF_SOURCE_COMMIT="$WILSOF_APPROVED_COMMIT" \
           WILSOF_HYPRIDLE_PACKAGE="$WILSOF_HYPRIDLE_PACKAGE" \
           WILSOF_ARCHISO_RELENG="$WILSOF_ARCHISO_RELENG" \
           SOURCE_DATE_EPOCH="$SOURCE_DATE_EPOCH" \
           WILSOF_ISO_VERSION="$WILSOF_ISO_VERSION" \
           "$WILSOF_EXPORT_ROOT/scripts/build-iso.sh" --build
<!-- build-command:end -->

   The materializer merges releng, ISO and shared desktop packages; boot
   configuration adds Plymouth/pv before resolution. A fresh isolated local
   pacman database resolves the whole image transaction, including dependencies
   already installed on the host. The preflight uses the expanded profile
   configuration and an explicit cache under the new profile, never `--needed`
   or the historical host cache. Every resolved file must match its repository
   SHA256, `.PKGINFO` name/version/architecture and trusted detached signature;
   bsdtar also traverses the archive. Unrelated cache entries are ignored.
   Empty, missing, corrupt or unverifiable transactions fail closed. Signature
   policy is not weakened; mkarchiso still performs pacman's own verification.

   This verifies the resolved repository transaction, not all future installed
   system updates, firmware/hardware behavior or the custom local Hypridle
   trust exception. The latter retains its existing package/binary SHA256 pin
   and must not be described as an officially Arch-signed package.

   After verification, the exact sync DBs/packages/public keyring are retained;
   Server entries become local `file://` inputs for mkarchiso, preventing a later
   live mirror refresh from silently selecting another closure. No historical
   cache is cleared. On failure retain evidence and diagnose; never weaken
   SigLevel, force-install, remove owned locks or indiscriminately delete caches.

3. After a successful command, validate the local artifact without booting or attaching it:

       find /srv/wilsof-iso-out -maxdepth 1 -type f -name '*.iso' -printf '%f %s bytes\n'
       sha256sum /srv/wilsof-iso-out/*.iso
       ls -ld /srv/wilsof-iso-out

   Use your actual explicit output path if different. Retain `BUILD-INPUTS.json`
   beside the ISO and the profile's `BUILD-SOURCE.json`, packages, signatures,
   repository databases and public keyring. The input record contains source
   revision/content/modes, releng identity, generated profile/package manifest,
   exact package versions/hashes/signers, effective original/frozen pacman policy,
   installed tool/environment identities, epoch and image version. Compare input
   records before attempting a separately authorized repeat build.

   The builder omits `mkarchiso -r` and retains work/profile: Archiso 91 otherwise
   recursively removes airootfs before ISO creation, which fails while a
   namespace-owned self-bind is active. See the
   [mount-lifetime contract](internal-test-runbook.md#scope-and-prerequisites).
   Record actual command/exit status, ISO filename/byte size/SHA256 and input
   manifest identity. Local tests or CI are not proof that an ISO was built.
   The input record also contains the dated repository and explicit early-KMS
   boot contracts; neither is a runtime or security acceptance result.

4. To revert a separately authorized test, preserve artifacts and logs first.
   Cleanup itself requires separate exact-path authorization, exited namespace
   owners and proof no mounts remain. There is no automatic recursive cleanup;
   never delete mounted work or use forced/lazy unmounts.

## Reproducibility boundary

Labels and default version derive from SOURCE_DATE_EPOCH, never the current
month/time. Equivalent controlled inputs produce equivalent metadata, excluding
filesystem mtimes. Tool versions and public trust state are captured, supported
Archiso 91/92 and matching releng are enforced, and mkarchiso consumes the frozen
local package closure. Initial resolution uses only Arch Linux Archive
2026-11-01 core/extra x86_64 and the accepted public keyring. Retain those bytes
and the input record; a dated URL alone is not a complete reproducibility proof.
See [the shared repository policy](repository-snapshot.md). No build-host
pacman configuration is changed or host downgrade performed.

This is traceable input freezing, NOT a demonstrated byte-for-byte reproducible
ISO. Full toolchain/image identity, kernel/namespace behavior, package hooks,
filesystem timestamps, compression/ISO implementation and native execution can
still affect image bytes. No independent repeat ISO builds have demonstrated
equality. Metadata hashes establish identity, not publisher authentication or
release acceptance. Never treat `FILES.sha256.json` (only embedded source) as a
complete package/build-environment attestation.

## Explicit authorization gates

No source change here authorizes an ISO build, boot, installation, physical disk
operation, Proxmox change, merge or public release. AS-02 and all unrelated
native/physical-client gates remain open. Stop on failed prerequisites or build
errors, retain partial output, and document the specific blocker.
