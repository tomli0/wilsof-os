# Wilsof update layer — first bounded implementation

Status: **RC4's bounded TEST ONLY update/recovery path passed virtual acceptance**.
The exact image completed a real 22-package snapshot advancement, fresh boot and
controlled interruption/refusal/explicit recovery. See
[Getting started](getting-started.md) for the frozen source/image identity.
This is not a production update service, ongoing security-update guarantee or
atomic-update system. No new transaction or image test is run by this document.

## Exposed commands

- `wilsof version` / `wilsof version --json`: read the immutable installed
  `SOURCE_COMMIT`; never invent a 1.0 version or advance image identity after
  changing packages or user configuration.
- `wilsof doctor`: invoke the existing read-only desktop diagnostic. Warnings
  and missing dependencies retain its nonzero status. No daemon is launched.
- `wilsof update --check`: offline prechecks only, no database refresh or write.
- `wilsof update`: require an ordinary desktop user's interactive terminal;
  execute exactly `sudo -- /usr/bin/pacman -Syu`, with native authentication,
  signature verification, package/global lock, CheckSpace and confirmation.

Menu Software > Update system enters that same command in Terminal. No install,
remove or rollback subcommand is advertised by this CLI. Existing separate
application install/remove actions are not a replacement package manager.

## Current repository and compatibility boundary

Build, live and installed systems currently share the reviewed dated
`runtime/repository-snapshot.py` policy. Maintenance verifies exact pacman.conf,
mirrorlist and snapshot manifest, checks safe ownership/non-writable ancestors,
and rejects symlinks. The installed policy helper is checked **before** loading.
No environment variable or CLI flag switches to arbitrary repositories or a
rolling mirror. No `-Sy`-only transaction, `--nodeps`, `--overwrite`, automatic
confirmation, signature weakening or downgrade is used.

The command performs full-package maintenance **on the existing frozen
snapshot**. A successful no-op is reported as no package-version change, not
an OS version upgrade. This cannot supply future security updates while the
snapshot stays frozen. Advancing to a new dated policy, including the private
compositor and patched idle-daemon compatibility, is a separate administrative
operation below; it is never an implicit side effect of `wilsof update`.
Do not treat a passing `--check` as daily-driver update readiness. Review the
actual Pacman proposed transaction/replacements before answering its prompt.

## Administrative snapshot advancement

The normal image materializer and live/installed provisioner install the existing
`wilsof-release-update` companion at `/usr/local/bin/wilsof-release-update` with
mode 0755 (Archiso explicitly assigns root:root). It is a required reviewed image
input, not an optional download. Lifecycle source/fixture checks do not establish
ISO, boot, native transaction or physical-client acceptance.

On an installed system, an administrator can explicitly propose a **forward**
full-snapshot update. For example, from the initial 2026-11-01 policy:

```sh
sudo /usr/local/bin/wilsof-release-update --plan 2026-11-02 /var/lib/wilsof-release-update/proposal-20261102
```

Use a new, unused absolute proposal path under root-owned, non-writable ancestors;
the helper creates its directory. Planning resolves/downloads using a separate
package database; it does not sign or install the proposal.
Independently review its exact `manifest.json`, package closure and baseline, then
provide `manifest.json.sig` using the **already pinned and trusted signer**.
TEST ONLY proposals remain TEST ONLY; production signer approval is separate.
The helper never imports/enrolls keys or substitutes another trust policy.
Execute only that reviewed signed proposal in an interactive terminal:

```sh
sudo /usr/local/bin/wilsof-release-update --execute /var/lib/wilsof-release-update/proposal-20261102
```

Preserve the proposal, signature, package cache and transaction receipts under
`/var/lib/wilsof-release-update/`. Policy advances only after the installed package
inventory matches the signed final closure, database checks pass and kernel/boot
artifacts are bound to the installed package/release. Installation
of the companion does not run it, schedule updates, grant passwordless sudo,
change `SOURCE_COMMIT`, migrate personal configuration or restart the desktop.

After interruption, inspect the receipts, Pacman logs, lock ownership and installed
packages before choosing a reviewed repair. `--recover DIRECTORY` accepts only the
same recorded signed plan whose package closure is **already complete**; it never
retries packages, deletes locks or provides atomic rollback. Live media, missing
trust, changed baselines and unsupported removals/replacements fail closed.

## Sequencing and failure contract

1. Require installed Arch/Wilsof identity; refuse live media and malformed image
   identity. `--check` does not request elevation.
2. Verify repository policy, its installed helper and safe path ownership.
3. Refuse an existing Pacman lock without removing it. Require at least 2 GiB
   free on root and 64 MiB on `/boot`, and the installed `/boot` mount. These are
   conservative floors, **not** a computed transaction-space guarantee.
4. Run only local `pacman -Dk`; refuse an inconsistent package database.
5. Recheck before the interactive full transaction. Pacman alone is elevated;
   Wilsof source code and user configuration are never executed as root here.
6. Preserve transaction failure/cancellation status, report possibly partial
   state, never retry automatically or proceed to configuration migration.
7. On exit 0 compare real pre/post `pacman -Q` inventories. Do not restart a
   running desktop, rewrite identity, advance configuration or reboot silently.
   After real binary updates, check `.pacnew` files and test a fresh login.

An inventory read failing after a completed transaction is an operation error,
not permission to repeat the transaction. Interrupts report unknown/possibly
partial package state; inspect `/var/log/pacman.log` first.

## Versioned configuration migration (separate operation)

`wilsof-config-update /absolute/path/to/reviewed-source` remains explicit,
unprivileged and offline. The existing owned-file installation is the legacy
schema-to-v1 migration. It checks
`~/.local/state/wilsof-os/config-version.json` before any writes, rejects invalid
or newer schemas, and records schema 1 only after the full deployment succeeds.
The record includes the configuration bundle's source SHA if a valid
`SOURCE_COMMIT` exists; a development tree without that marker records unknown,
not the installed image SHA. Personal DMS preferences, shell additions, shortcut
overrides and historical data retain the existing preservation contracts.

An identical rerun is idempotent. Replaced owned files have per-file backups
under the existing Wilsof state directory; tested manual file recovery is not
transactional rollback. A failed multi-file deployment can be partial. No remote
source download, arbitrary root script, migration-after-failed-package-update
or automatic restore is introduced. Future schema upgrades need new explicit
migration code and regression tests; schema numbers alone do not migrate data.

## Recovery limitations and next acceptance gate

The current installer documents GPT, a FAT32 ESP mounted at `/boot`, ext4 root
and systemd-boot. It does not create Btrfs subvolumes, LVM snapshots, A/B slots,
a fallback kernel or atomic package/config/bootloader rollback. Consequently no
`wilsof rollback` is exposed and no recovery guarantee is made.

Before any real update, preserve a separate verified user-data backup, a known
bootable recovery medium and relevant Pacman package cache. Do not delete old
ISOs/backups, automatically remove locks, guess a downgrade package closure or
claim reinstalling restores user data. In a failed update, preserve logs and
inspect installed packages, mounts and boot files from recovery media before
choosing a reviewed repair. Cache availability is not guaranteed rollback.

The retained RC4 acceptance supplies the separately executed native transaction,
refusal, interruption, recovery and fresh-boot evidence for that exact image.
Source tests still substitute package boundaries and do not establish native
results themselves. Do not repeat unchanged passed gates during physical testing.
Any future closure, signer or runtime-source change needs its own reviewed inputs
and relevant fresh acceptance; no production update cadence is established here.

Primary references used: upstream Arch `pacman(8)` for `-Syu`, `-Dk`, transaction
confirmation and config-file handling; existing [repository policy](repository-snapshot.md)
and [installer layout/API](installer-runtime.md). No distribution-specific
implementation was copied.
