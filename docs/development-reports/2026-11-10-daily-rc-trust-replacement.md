# Wilsof OS daily-driver RC — trust, replacement and recovery continuation

Status: **PARTIAL DELIVERY — FINAL VIRTUAL ACCEPTANCE BLOCKED; OMARCHY NO-GO.**
Date: 10 November 2026. Existing branch `integration/private3-20261107`,
issues #16/#60 and draft PR #61 only. Implementation/source archive:
`fc0f60ee21c15fe8fca4f19cde9a4c42f666fa20`. A later documentation delivery hash is
recorded in the private handoff and read-back-verified GitHub comments.
No new privileged ISO build, physical disk write, Omarchy deletion, main merge
or public release was performed.

## 1. Delivered engineering milestones

- Portal trust correction: external owner-approved primary-fingerprint pin,
  mandatory detached signature, actual full-validity GnuPG preverification against
  the target's existing pacman keyring, then unchanged pacman verification. Root
  is required before target writes; no key import/retrieval or public fallback.
- Real offline OpenPGP fixtures and actual native synthetic libalpm installation/
  rejection controls. No test identity signs the retained production portal.
- New complete native existing-ext4 replacement, valid GPT/ESP/ext4, disk-only
  UEFI boot, real password/PAM login and ordinary-user shutdown. A writable
  unselected sentinel remains unchanged, strengthening the earlier read-only test.
- Controlled native interruption after actual ext4/GPT signature erasure and before
  backend formatting: installer 130, no false completion/retry, partial target
  preserved, writable sentinel unchanged. No rollback or secure erasure claim.
- Actual abruptly interrupted signed two-package libalpm fixture, consistent but
  incomplete package set, preserved stale lock/database and explicit complete-set
  recovery. This is not a future Wilsof OS upgrade.
- Owner-controlled signing/rotation/revocation procedure, one coherent future
  update-transition plan, universal-PC evidence matrix and updated recovery scope.
- New blank-GPT full replacement also passes: installer 0/five prompts/400.664
  seconds, valid GPT/ESP/ext4, separate disk-only boot, actual password/PAM login
  and ordinary-user shutdown. Its writable unselected sentinel is unchanged.

## 2. Evidence and independent-assessment boundary

Private evidence group: `wilsof-daily-rc-20261110T0757Z`. Raw journals, VM disks,
QA credentials and private infrastructure paths remain outside public source.
Exact separate read-only AI assessment passes source diff SHA256
`b46843c5a9def87e2903d51444652dcbabff1e98a60ed1aeadd6c1b434a6719a`,
with no security/logic blockers. It traced prepare-iso, fresh-target provisioning,
repository policy and the pinned-package command boundary. This is a scoped AI
source assessment, not professional independent security approval.

The external approval JSON is deliberately **not self-authenticating**. A later
reviewed authenticated build handoff must freeze it and the public certificate,
package and signature against the independent owner decision. No such owner
identity or production trust enrollment exists yet.

## 3. Source quality, provenance and security

- Full local regression: **863 PASS / 3 explicit native opt-in SKIP**, exit 0.
- Actual source CI: **859 PASS / 7 SKIP**, a different environment. Skips are not
  passes; the local total is not substituted for CI.
- Python AST: 111 inputs; JSON: 21; installation-plan schema: 1; image payload:
  72 required files. ShellCheck in the prescribed sh/bash dialects and Git
  whitespace checks pass. New documentation uses pinned Markdownlint with the
  existing long-line MD013 exception disclosed.
- Tests reproduce missing approval, another trusted signer reaching a substituted
  package-mutation boundary, unprivileged target writes and orphaned approval fallback before
  correction. Real GnuPG fixtures cover valid signing subkeys, modified bytes,
  missing/corrupt signatures, incorrect/unknown/untrusted signers and expiry.
- Source consumers execute actual GnuPG with only chroot/keyring-location and
  pacman boundaries substituted. A separate native libalpm fixture installs the
  signed harmless package and refuses five bad trust controls. Its local-file
  policy is explicitly Required, not the production Optional policy.
- Current exact retained real archive SHA256 remains
  `d3d2dba441324ed467574ea27f5d2432f7f10cf851e1cc46aaf73bed2d8e7fd0`.
  Real-input preflight refuses missing owner approval before archive inspection
  or installation; signature is absent too. No repeated blocked signing attempt.
- Existing portal source/patch/recipe/ELF provenance remains applicable and
  unchanged. No new third-party driver/code or production key is introduced.
  Supplemental notices remain in source consumers. Complete transitive licensing,
  project-license decision and Broadcom redistribution clearance are not claimed.

## 4. Commits and exact-head CI

| Commit | Role | Evidence |
| --- | --- | --- |
| `b293b2c3595099789d3479f1462f01913a0f20e8` | Reconciled starting delivery | Local/remote match; clean tracked tree; latest issues/handoff inspected |
| `fc0f60ee21c15fe8fca4f19cde9a4c42f666fa20` | Portal signer/privilege contract, tests and signing runbook | Pushed; all five delivered blobs independently byte-read back; local source gates and scoped AI assessment pass |

[Exact implementation CI run 42781302925](https://github.com/tomli0/wilsof-os/actions/runs/42781302925)
checks the exact implementation SHA and succeeds. Documentation-only close-out
gets its own exact-head read-back; this run is not represented as that later
commit's CI. PR #61 remains open/draft against retained Private2, unmerged.

## 5. Artifact and ISO-build preparation

| Item | Actual identity/status |
| --- | --- |
| New ISO | **NOT BUILT**; no new path, bytes or SHA256 |
| Historical ISO | `wilsof-internal-2026.11.09-private3-sprint2-wl1-x86_64.iso` |
| Historical bytes / SHA256 | 2813849600 / `111c06b70cf6d909b3e815975f69bfa18f299af9dcfe9bbbfd5e197992c53a59` |
| Historical frozen image source | `7c3771b3c2c4b2ef05477f09bab8f0f3baa10261` |
| Preserved source archive | Exact fc0f60e, 345 regular source files; not an ISO |
| Source archive SHA256 | `248b368024e77e151ef3c50ff9600893ff5b3245e26029c92d711299559d82fc` |
| Source epoch | 1794298566 |
| Builder tools observed | archiso 92-1; arch-install-scripts 32-1; gnupg 2.4.9-4; pacman 7.1.0.r9.g54d9411-3 |
| New build action | PREPARATION ONLY / NOT EXECUTABLE / NOT AUTHORIZED |

The historical local bundle's ISO bytes were independently rehashed unchanged.
New native installer tests use an explicitly identified source overlay on that
historical ISO; they do not repair its portal or constitute a new image.

Private `RC-BUILD-GATES.json` pins the source export and retained portal while
leaving missing approval/signature/public-certificate identities explicitly null.
It requires complete signed official/private inputs, current storage reconciliation,
new root-controlled/disjoint leaves, persistent one-attempt marker, project/QA/build
locks, finite service limits and actual rootful namespace/device-deny smoke before
any mkarchiso call. Mapped-root fixture isolation is not rootful build acceptance.
The consumed old-image helper is not reused. No honest complete build command is
provided before the missing inputs and separate exact build authorization exist.

## 6. Replacement matrix and exact-new-image gates

| Replacement case | Direct result and boundary |
| --- | --- |
| Blank GPT | PASS: actual PTY replacement 0/five prompts/400.664 seconds, valid GPT/ESP/ext4 and disk-only password/PAM login; strict blank mode separately refuses GPT metadata |
| Existing ext4 | PASS: actual PTY install 0, five prompts, 406.404 seconds; valid new GPT/1 GiB ESP/ext4; disk-only password/PAM login |
| Existing Btrfs | Source safeguards and prior real EFI/Btrfs installation apply; standalone no-ESP full native installation is not newly claimed |
| Existing EFI/Btrfs | Prior direct source-overlay installation PASS, preserved and not repeated; not new ISO acceptance |
| Incorrect destructive confirmation | Native refusal and unchanged reviewed inventory on ext4/GPT; source regression coverage retained |
| Changed identity | Source revalidation/refusal tests PASS; no physical hotplug or new native identity-substitution installation claimed |
| Mounted target | Actual synthetic ext4 mount refused; earlier native Btrfs refusal preserved |
| Live installation device | Actual attached live USB refused; copy-to-RAM protection remains separately source-tested |
| Multiple disks | Live USB + selected new target + writable unselected sentinel attached; only selected target modified |
| Writable unselected sentinel | PASS unchanged through both full installs/boots and the interrupted replacement; both were attached writable, not protected by a read-only QEMU flag |
| Interrupted replacement | Actual post-erasure trace-injected KeyboardInterrupt: 130, no completion/retry, no new partition layout, unchanged sentinel; not random power-loss coverage |
| Disk-only UEFI | PASS separately after ext4 and blank-GPT replacement, actual normal greeter password/PAM login and owning menu readiness |

The interruption removes recognizable partition/filesystem signatures but does
not restore the old OS. Raw old data may remain; this is not secure erasure.
After preserving that failure, the next synthetic blank GPT was explicitly
recreated and a fresh digest-bound confirmation was required. No automatic retry.

All **18 exact-new-ISO tests remain NOT RUN**: UEFI USB, live desktop, cowspace,
blank install, installer success, disk-only boot, PAM login, branding, menu, native
Hyprlock, wrong password, correct unlock, post-unlock menu, repeated locking,
Terminal/Firefox/Files, workspaces, reboot and clean shutdown. No historical pass
or source-overlay result is transferred into that column.

## 7. Authentication and portal lifecycle

Both new tests use a rendered normal greeter password prompt, exact active greetd
state and actual `pam_unix(greetd:session)` evidence, followed by operational owning
menu IPC. Root/runuser access does not count as password authentication. The disk
boots `/dev/vda2` ext4 with no attached installation ISO. Ordinary-user shutdown
is followed by actual QEMU exit 0 and an offline image check.

The installed portal in both remains **1.4.1-2**, intentionally reported. This is
installer testing, not acceptance of the new signed portal. Earlier five corrected
source-ELF and five packaged-ELF cycles are preserved. Production signed-package
installation, file chooser/backend gates and five fresh signed installed-package
login/logout cycles remain blocked by the owner signing/trust decision.

## 8. Update and recovery results

The [coherent update transition](../update-transition.md) selects one complete
2026-11-08 target investigation, not a partial library upgrade. Native earlier
planning refuses aquamarine 0.16.0-1 / hyprgraphics 0.6.0-1 against private
`libaquamarine.so=14-64` / `libhyprgraphics.so=4-64` requirements. Installed policy
and database were unchanged; there is no accepted future closure or OS progression.
A compatible signed private compositor, Dux/portal lifecycle and matching kernel/
headers/Broadcom DKMS closure must be verified together before a real transition.

New real libalpm fault evidence: two signed harmless packages begin at 1.0-1.
After exact owned-group SIGKILL during A's post_upgrade, inventory is A 2.0-1,
B 1.0-1 and database check 0. The incomplete set and stale lock are preserved.
Explicit fixture recovery only after process exit restores the complete exact
signed set to 2.0-1/2.0-1; payload hashes and database check pass. Host database,
config, public keyring and trustdb remain unchanged; fixture keys/mounts are gone.
Two earlier lab shell/loader setup failures are retained, not product passes.

This is not kernel/DKMS progression, an interrupted complete OS upgrade or recovery
reboot. Prior manual missing-EFI-loader repair, actual disk-only password boot,
data/settings persistence and configuration migration/recovery evidence remain
applicable without repetition. There is no automatic or atomic OS rollback.
See [precise recovery scope](../recovery.md).

## 9. General PC compatibility, physical and license gates

[Hardware matrix](../hardware-compatibility.md) separates intended Intel/AMD CPU
and graphics paths, NVIDIA, wired/common wireless, USB input, audio/Bluetooth,
laptop power and multi-display configurations from actual virtual evidence.
No physical combination is upgraded to supported by a package inventory. Broadcom
wl remains additional owner-hardware integration, not a generic networking
requirement. No new proprietary GPU package or MacBook-specific installer logic.

[Owner MacBook checklist](../omarchy-transition.md) remains live-first and
non-destructive: i915 2560x1600/scaling, keyboard/trackpad, BCM4360 14e4:43a0/wl
binding/scan/WPA/Internet/reconnect, btusb pairing, HDA/PipeWire audio, microphone,
brightness/battery, suspend/resume and reboot/shutdown are all physical NOT RUN.
Independent backup copies, tested restoration, working recovery media, physical
acceptance, target verification and separate owner approval precede any Omarchy
replacement. Required notices/security and redistribution gates remain open.

## 10. Model, quota and harness deviations

The one separate AI assessment uses the inherited included Codex route. No paid
fallback/provider, automatic worker or scheduler was launched. No quota failure
was observed; remaining quota and billed actuals are unknown, not zero.

Retained lab deviations: initial synthetic transaction root lacked executable
loader/native scriptlet-shell prerequisites; actual native shell proof precedes
attempt 3. One concurrent QGA diagnostic times out while the single agent channel
is owned by the running installer; the existing install is not restarted. A
nested-SSH diagnostic quoting failure ran read-only commands locally instead of
the guest; no shutdown/write occurred, and a transferred compiled script replaced
that harness path. Missing Pillow conversion used existing ffmpeg instead, without
repeating the already-entered login prompts. None of these are product passes.

## 11. Preservation, processes, locks and resources

All four new QEMU lifetimes exit 0. Both offline QCOW2 checks pass; both writable
sentinels retain their independent pre-install hash. Twenty ext4 and twenty-five
blank-GPT evidence files are transferred and match independent remote SHA256
values. Historical disks, firmware, ISOs, failed lab attempts and raw evidence are
retained. QA disks/passwords are not shipped with source or any candidate bundle.

At 08:59:50 UTC the builder has **12906995712 free bytes**, 4 CPUs and
MemAvailable 7334772 KiB. No QEMU/owned native process, fixture test-key directory
or leaked fixture namespace mount remains; QA lock is independently available.
Actual host package DB/config/public keyring/trustdb hashes are unchanged. Current
free storage is below the documented 25 GiB build floor: preserve evidence and
obtain a separate capacity decision rather than deleting old ISOs/backups.

The project lock is retained only for synchronous final publication; actual
release and independent probe are recorded in the final handoff/GitHub receipt.
Automation remains paused. No protected Proxmox or physical-storage change.

## 12. Result classification and one next owner action

| Classification for complete new RC | Actual status |
| --- | --- |
| SOURCE READY | Complete RC not declared; scoped source trust milestone verified and delivered |
| SIGNED PACKAGE ACCEPTED | BLOCKED: no owner-approved production identity/signature/native consumer proof |
| ISO BUILT | NO new ISO |
| ISO VERIFIED | NOT RUN on new bytes |
| VIRTUAL ACCEPTED | NOT ACHIEVED |
| READY FOR PHYSICAL TEST | NO |
| PHYSICAL ACCEPTED | NOT RUN |
| READY TO REPLACE OMARCHY | NO / preserve Omarchy |

One consolidated owner decision: authenticate and approve the exact Wilsof primary
OpenPGP fingerprint, private-key custodian and narrow public-key enrollment scope
for the retained hash-pinned portal, following [package signing](../package-signing.md).
If no suitable identity exists, establish it under owner control on the trusted
signing workstation first. Never send private keys/passphrases to an agent.
Only public certificate/signature/approval inputs return for freezing and both
native consumers. Other production private inputs keep their independent trust
requirements. A new exact privileged build authorization comes later, not from
this daily-driver mission or a self-authored approval file.
