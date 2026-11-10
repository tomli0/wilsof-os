# Coherent update transition and recovery gates

Status: **transition BLOCKED**, not an accepted daily-driver update release.
The installed approved snapshot remains 2026-11-01. A successful full `pacman -Syu`
on that snapshot can be a no-op; it is not delivery of later security versions.
Do not replace the package manager or partially upgrade individual libraries.

## Measured dependency boundary

Native planning against a copied installed database and proposed complete official
snapshot 2026-11-08 refused both of these changes:

| Proposed provider | Retained private compositor requirement | Result |
| --- | --- | --- |
| aquamarine 0.16.0-1 | `libaquamarine.so=14-64` | Native dependency preparation refused |
| hyprgraphics 0.6.0-1 | `libhyprgraphics.so=4-64` | Native dependency preparation refused |

The real installed database and production repository policy stayed unchanged.
Those observed versions describe the examined snapshot, not today's rolling
repositories or an already approved future closure. Planning did not download and
verify every future package, install it, migrate configuration or reboot it.

## One selected transition, no mixed-version workaround

The selected engineering path is a separately built and reviewed compatible
private-compositor package for **one complete 2026-11-08 snapshot**, retaining the
required session-lock integration. This is a proposed transition target, not an
approved build input or proof that the existing patched compositor source compiles
against those APIs. If compatibility cannot be established, stop this transition
and obtain a new complete-baseline decision; do not accumulate cherry-picked
provider downgrades or silently switch mirrors.

1. Preserve the accepted old package/source/patch evidence. Freeze the private
   compositor's exact source revision and required local lock patch set. Review
   any source adaptations against the new aquamarine/hyprgraphics APIs. Keep the
   Dux lifecycle and owning lock-notification contract, not just ELF loading.
2. Resolve the complete official image/target/installed transaction using native
   libalpm in dedicated copied databases. Capture repository/database hashes,
   complete names/versions/architecture/archive digests, detached signatures,
   public keyring/trust identity and both private runtime/build constraints.
   Resolve all providers together; no ignored dependencies or SONAME symlinks.
3. Build only in a separately authorized disposable matching environment. Verify
   packaged ELF NEEDED entries and actual provider SONAMEs, full relocation/
   loader resolution, package-owned binary hashes and no public-Hyprland fallback.
   Inspect corrected portal dependencies and private Hypridle independently.
   All production local packages need an authenticated, approved signing/trust
   route: historical hash-pinned local exceptions are not new signed-production
   acceptance. The [portal signing gate](package-signing.md) is the first such
   gate, not blanket approval of every private artifact.
4. Reconcile Dux's packaged integration and actual compositor IPC/API behavior.
   Test normal fresh PAM login, bar/menu, portal Screenshot/file chooser,
   native locking/wrong-password rejection/unlock/input isolation and at least
   five ordinary logout/relogin cycles. Inspect per-service results and cores;
   do not conceal the separately disclosed Dux/GTK portal/Hypridle teardown exits.
5. Treat `linux`, its matching headers, DKMS/compiler closure and Broadcom wl as
   one tested transition. Require actual DKMS success and installed module
   vermagic/ABI, effective binding policy and initramfs contents for the selected
   kernel. Repeat the module-loading gate in the disposable guest. Virtual load
   is not BCM4360 connectivity or Secure Boot acceptance. Do not upgrade a kernel
   while retaining an unverified out-of-tree module/header combination.
6. Freeze the reviewed compatible signed closure and source/manifest identities.
   Only then prepare the explicit new repository-baseline source/configuration
   transition. The existing validator deliberately refuses mirror/date drift;
   do not edit an installed mirror by hand to bypass it. Configuration migrations
   remain explicit, schema-versioned and separate from package transactions.
7. In a new COW over an independently verified stopped installed baseline, perform
   the reviewed full transaction through the normal unprivileged controller and
   authenticated fixed pacman boundary. Record before/after inventories and actual
   changed versions, signature receipts, configuration/backup identities, logs,
   clean reboot, fresh PAM login, services, core applications and user persistence.
   Do not count an old still-running process or no-op as upgraded acceptance.
8. Exercise interrupted transaction, lock ownership/database consistency, failed
   and repeated configuration migration and manual recovery with exact trusted
   inputs. Preserve the original failure. Require another clean boot/login and
   application gate after recovery. Do not invent atomic or automatic rollback.

## Recovery contract

The installed layout is ext4 plus FAT32 ESP/systemd-boot, not an A/B or snapshot
rollback system. [Manual EFI repair](recovery.md) has separate direct native
proof. Managed-file backups permit explicit per-file restoration only.

On transaction failure, the controller must retain failure and possible partial
state, with no automatic retry or migration. Preserve inventory, pacman log,
transaction inputs and configuration backups. Reconcile the actual lock owner
before any separately approved recovery. A stale lock can be removed only after
that exact transaction's processes have exited and the operator has reviewed
consistency; never delete a production lock automatically.

Recovery uses independently authenticated trusted media and a coherent exact
package set. Do not restore only the compositor libraries, ignore ABI dependencies,
use a broken installed network stack as the sole source, or assume the current
image supplies a later compatible update set. Owner data restoration and physical
recovery remain independent acceptance gates.

## Release decision

No production forward transition is accepted until the signed coherent closure,
real version progression, migrations, reboot/login/apps and post-interruption
recovery have direct evidence. Synthetic harmless package transaction fixtures
can validate libalpm failure/recovery behavior; they cannot pass this OS transition.
A source CI pass and the old EFI-repair pass do not substitute for these gates.
