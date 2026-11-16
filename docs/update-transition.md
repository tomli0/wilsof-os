# Coherent update transition and recovery gates

Status: **production maintenance approval remains pending**. RC4's exact TEST ONLY
image passed a bounded native 2026-11-01 to 2026-11-02 transition with 22 changed
packages, fresh boot and interruption/recovery checks. Its initial repository
policy is still 2026-11-01; later policy promotion requires an explicit reviewed
signed plan. See [Getting started](getting-started.md) and
[the current release gates](package-signing.md#current-release-responsibilities).

A frozen snapshot receives no later security fixes automatically. Successful
`pacman -Syu` maintenance on an unchanged snapshot may be a no-op. The historical
2026-11-08 compatibility investigation below is not an approved next release or
proof of ongoing update delivery. Do not partially upgrade individual libraries.

## Historical measured dependency boundary

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

## Future transition contract, no mixed-version workaround

The earlier complete 2026-11-08 snapshot proposal was not an approved release and
is not the current next-build instruction. RC4's accepted test transition was to
2026-11-02. No later compatible complete baseline has been accepted by this record.
Before choosing a future target, retain the required session-lock integration,
review source/ABI compatibility and authenticate one complete signed closure.
If compatibility cannot be established, stop; do not accumulate cherry-picked
provider downgrades or silently switch mirrors. The sequence below is a contract
for separately authorized future work, not a request to build while RC4 is tested.

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

A complete package inventory and `pacman -Dk` are not sufficient recovery proof.
Before normal execution or explicit recovery promotes policy/completion, the
standard `linux` layout requires safe, nonempty boot kernel/initramfs files, an
exact boot-kernel match to the installed package, native initramfs analysis bound
to that package's kernel release, and a native main-archive traversal. Missing,
invalid or stale boot artifacts refuse promotion. Repair/rebuild remains an
explicit operator action, never a hidden retry; a fresh encrypted-root boot and
normal login are still separate acceptance gates.

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
