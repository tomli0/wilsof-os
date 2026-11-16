# Wilsof OS — daily-driver sprint 2, 9 November 2026

Status: **source milestone delivered; substantial native source-COW evidence;
Private3 NOT ACCEPTED; stopped at the privileged new-image boundary.**

Development began 15:03 UTC. Native guest lifetime: **15:07:37–15:44:46 UTC**.
Close-out/resource/CI rechecks: **15:53–15:54 UTC**, with publication receipts in
issues [#60](https://github.com/tomli0/wilsof-os/issues/60) and
[#16](https://github.com/tomli0/wilsof-os/issues/16).
Branch: `integration/private3-20261107`.
Implementation: `7c3771b3c2c4b2ef05477f09bab8f0f3baa10261`.

## Evidence basis and scope

- Historical: [first daily-driver sprint](2026-11-09-daily-driver-sprint.md),
  reporting source `fe755e1`, 747 source passes / 3 opt-in skips and native desktop
  overlay `488070e`. Its results remain historical, not passes on a new image.
- Newly verified: starting local/remote HEAD matched the requested `fe755e1`;
  Broadcom implementation, 756-source-test checkpoint, actual native driver /
  update/configuration/session tests and prepared owner handoff described below.
- The owner's Omarchy diagnostic identifies `14e4:43a0` and working `wl`. That is
  owner-provided hardware evidence, not agent-observed Wilsof hardware acceptance.
- Private evidence root is labelled `wilsof-sprint2-20261109T1503Z`; native logs,
  QA credentials, disks, helper infrastructure locators and original failures
  stay private. **56 transferred evidence files** were independently hash-matched.
- No new ISO, fresh installation, physical disk/USB operation, Proxmox change,
  host package installation, merge, release or public binary publication occurred.

## 1. Completed milestones

**A — Broadcom source integration and native compatibility investigation.**
Added matching headers and official Broadcom DKMS package to the shared live /
installed package closure; a fail-closed target-aware module gate; narrow
same-basename policy override instead of a vendor-wide blacklist; early wl
initramfs inclusion; image-only exclusion of default generated signing material.
[Detailed compatibility/license analysis](../broadcom-wl.md).

The actual frozen kernel is **7.2.11-arch1-1**, package/header version
**7.2.11.arch1-1**. Signed official `broadcom-wl-dkms 6.30.223.271-50` and
`dkms 3.4.4-1` built/installed successfully twice in a new disposable COW guest.
`modprobe wl` succeeded, with correct module path/vermagic/cfg80211 dependency.
A real unsupported-kernel/missing-header build refused with exit 21.

Native mkinitcpio and inspection found wl, cfg80211 and the effective override.
Normal reboot loaded wl without manual intervention. The virtual Ethernet
connection survived. **No BCM4360 was emulated; scans/WPA/reconnect are pending.**
The native helper prototype differs from the final image-sealing helper; the
[checkpoint records both hashes and exact acceptance limits](../checkpoints/2026-11-09-daily-driver-sprint2.md).

**B — Actual update/configuration lifecycle evidence, without a rewrite.**
Real ordinary-user sudo/PAM full `pacman -Syu` exited 0 and correctly reported
**no-op**. Ctrl+C at its sudo prompt exited 130. Unknown argument/source and
existing-lock refusals were exercised; normal signed same-version `patch`
reinstallation succeeded, damaged supplied signature was rejected by real
Pacman, and installed inventories/signature policy remained unchanged as expected.

Seven native configuration cases checked legacy schema migration, exact source
provenance, personal preference preservation, idempotence, manual file recovery,
future-schema refusal and partial failure with unchanged completion marker /
explicit repair. This is not atomic rollback. Detailed results and test limits
are in the checkpoint, including six rejection/signature checks and two PTY cases.

**C — Essential desktop lifecycle after deployment.**
Unmodified Hypridle policy acquired native lock after **181.445 seconds** with
no keyboard activity during the interval. Rendered idle/password surfaces were
inspected. Genuine idle unlock, immediate Super+L relock, exact-PID wrong-password
PAM failure, correct unlock and actual keyboard menu recovery passed. Same
resident shell, **NRestarts=0**, no synthetic unlock or shell restart. Terminal
shortcut/workspace preservation passed. Normal user reboot preserved observed
file hashes and returned to greeter; a new normal password login succeeded.

**D — Conditional build preparation.**
Pinned clean source archive/epoch, unique output and complete metadata-resolved
814-package official closure; prepared one hash-locked interactive owner entry
with bounded resources, locks and retained isolation/preservation gates. Actual
read-only native checks and 24 private orchestration tests passed. **Rootful
execution and all new-image acceptance remain NOT RUN.**

## 2. Claude QA findings and remediation

No Claude or paid alternate-model review was requested. Two bounded independent
read-only AI contexts on the inherited route completed:

| Review | Exact identity | Result / scope |
| --- | --- | --- |
| Broadcom source | Patch `e9d29e39ca231b7cd5d868fac102d04fb618c5c2b13e71229366c23db52c4925` | PASS, no concrete blockers; producer/consumer and target/module/policy chain inspected. |
| Prepared owner handoff | Helper `b99f7241fa0b292565348958ff56e5f7a92ab27f2a209b85b95f30d3efe1611e` | PASS, no blockers in deltas; not actual rootful or image acceptance. |

Nonblocking suggestions concern additional consumer-failure, signing-file,
QA-lock and closure-field negative coverage, plus stale inherited helper labels.
No required finding was hidden or left unresolved. Independent human security
and qualified proprietary-driver redistribution review remain **PENDING**.

## 3. Code quality and security status

- Full source command: `python3 -m pytest -q` — **756 passed / 3 explicit opt-in
  skips**, exit 0, 31.91 seconds, source `7c3771b`. Focused Broadcom/chroot/installer
  run: 100 passes before the final signing-file test; overlapping, not additive.
- Changed Python AST, both CONTRIBUTING ShellCheck command sets, three prescribed
  JSON inputs and `git diff --check` passed. JSON was rechecked during close-out;
  no full suite was rerun merely for reporting. Source unchanged after `7c3771b`.
- RED/GREEN evidence covers missing driver gate, shared package/policy inclusion,
  target ordering and image-key exclusion. Initial full run exposed two test
  harnesses dispatching every helper to the pinned-package API; path-specific
  test dispatch was corrected, without a production bypass.
- No weakened Pacman signatures, rolling-mirror switch, partial Arch upgrade,
  Omarchy binary/module copy, arbitrary blacklist, authentication bypass or
  system-wide host boot change. Module loading in the disposable guest used its
  pre-existing lockdown-none/non-enforcing policy and produced normal proprietary
  and untrusted-key taints; Secure Boot is not accepted.
- Default DKMS build signing keys must not be shared through an image. Final
  image-only cleanup is source-tested and absent from installed/update paths;
  exact immutable-image secret/inclusion audit is still required.
- License inspected directly from the exact Arch package. Its conditional binary
  redistribution terms are not a general open-source grant. **Public combined
  module/ISO redistribution NOT CLEARED.** No legal clearance is claimed.
- First signature harness stopped on Pacman's cache `file://` URL; corrected
  repository/filename resolution passed. Reboot RPC loss was reconciled using
  changed boot ID and shutdown journal; no reboot retry. Failures are retained.

## 4. Commits and CI status

| Commit | Purpose | Verified status |
| --- | --- | --- |
| `fe755e103497c20eb464b2b6b7adc1caadd287aa` | Actual starting checkpoint | Local/remote matched before changes; untouched prior work preserved. |
| `7c3771b3c2c4b2ef05477f09bab8f0f3baa10261` | Broadcom implementation/docs/tests | Pushed; exact remote head and all nine changed files byte-read back. |
| Reporting commit containing this file | Native checkpoint and full close-out | Exact resulting SHA/content read-back is recorded in final issue comments/private handoff, without a self-referential commit loop. |

At 15:53:33 UTC exact implementation-head checks: **0 check runs, 0 status
contexts, 0 workflow runs**. Combined status says pending with no contexts:
**CI MISSING/NOT REPORTED, not green or a running test**. Existing branch filters
were not altered; no manual CI dispatched. No new PR, merge, ready transition,
issue closure, release or protection change. Final reporting-head CI is checked
and recorded in the publication receipt.

## 5. ISO filename, size, SHA256 and location

**No Private3 ISO has been built.**

| Field | Actual status |
| --- | --- |
| Proposed unique internal filename | `wilsof-internal-2026.11.09-private3-sprint2-wl1-x86_64.iso` |
| Frozen build source | `7c3771b3c2c4b2ef05477f09bab8f0f3baa10261` |
| Source timestamp epoch | `1794237834` — distinct from repository snapshot 2026-11-01 |
| Source archive SHA256 | `5e40387c8c3d7b750b418701adb5007bf61bbcb5ca00b357cae17d1dbac68e41` |
| Candidate package closure | 814 unique official packages, metadata-only native resolution; complete signed freeze still mandatory before mkarchiso |
| Actual ISO size / SHA256 / download | **Not available: no produced ISO** |
| Historical artifacts | Preserved; no historical ISO overwritten/deleted; four historical backing/firmware hashes newly matched |

Package metadata sums: **1,705,441,788 compressed bytes**, **5,200,437,061
installed bytes**. These are not an ISO-size or peak-space measurement.
Read-only builder tools/private-input/source-entry/storage checks passed;
`owner-private3-build.py --check` executed successfully on the real builder.
The prepared helper keeps actual trusted signature verification, expected whole
closure comparison and fresh in-service isolation smoke ahead of mkarchiso.
No rootful phase was executed: one initial noninteractive sudo probe reported
that owner authentication is required; it was not bypassed or repeatedly retried.

## 6. Full installation results

| Gate | New Private3 ISO result | Separate evidence |
| --- | --- | --- |
| UEFI emulated-USB boot / live desktop | NOT RUN | No new ISO exists. |
| New blank-disk installation / installer exit 0 | NOT RUN | No fresh installation in this sprint. |
| Disk-only boot / normal login / branding | NOT RUN on new image | Retained disk plus new source-COW boot/login checked separately. |
| Menu / native lock / wrong-password / correct unlock / repeated cycle | NOT RUN on new image | New source-COW lifecycle results in sections 1 and 7. |
| Terminal/Firefox/Files / workspace / reboot / shutdown | NOT RUN on new image | New Terminal/workspace/reboot/shutdown source-COW evidence; earlier broader application passes remain historical. |
| Broadcom image inclusion / exact-image update gates | NOT RUN | Native package/initramfs evidence is not SquashFS/ISO acceptance. |

All **18 mandatory exact-new-image gates remain unrun**, not inherited from
Private2 or this source-overlay cycle. Physical MacBook acceptance remains open.

Resource snapshots: local available **20,397,264,896 bytes at 15:54:21 UTC**;
builder available **60,965,679,104 bytes**, available RAM **7,463,612,416 bytes**,
4 allowed CPUs at **15:53:35 UTC**. The read-only build storage floor is
26,843,545,600 bytes. No storage cleanup/growth was performed. Future root phase
must recheck live capacity, device/namespace isolation and actual cgroup limits;
helper fixtures are not proof that those properties have executed.

## 7. Boot and password authentication

Immutable installed source remains **Private2 `063b7f0`**; user configuration and
exported bundle are **`7c3771b`**. Real normal greetd username/password input after
update/configuration opened the qauser PAM session. After ordinary user reboot,
changed boot ID, exact unchanged hashes for preference/config marker/CLI/module /
initramfs, wl residency and second normal password login were verified.

Idle and immediate relock used authoritative compositor state plus actual locker
and rendered input surfaces; wrong-password failure was attributed to the exact
Hyprlock executable/PID. Same resident menu recovered after correct authentication.
No all-client security certification is claimed. Post-reboot NRestarts=0,
Hypridle/PipeWire/WirePlumber active, captured failed-unit lists and current-boot
systemd-coredump journal empty. Bluetooth enablement persisted, but an absent
virtual adapter does not prove physical pairing or power control.

## 8. Remaining defects, limits and daily-driver blockers

1. New Private3 ISO/rootful safety checks, immutable inclusion/key audit and all
   18 installation/boot/session gates, plus Broadcom and update gates.
2. Physical `14e4:43a0` binding, wireless scan/WPA/reconnect/reboot; firmware,
   Secure Boot/signing policy, i915 scaling 2.0, audio/BT and suspend/wake.
3. Frozen snapshot maintenance does not supply future OS/security updates.
   Reviewed snapshot progression needs full signed compatibility manifests,
   coherent whole-system upgrade, native DKMS/private-package compatibility,
   boot/recovery and fresh authenticated-session acceptance before adoption.
4. No changed-version updater acceptance, mid-writing transaction interruption /
   power-loss recovery, complete rollback path or config-migration concurrency
   acceptance. Current per-file recovery is deliberately non-transactional.
5. Final Broadcom helper/image-only sealing runtime, fresh installer consumer and
   physical probe are not accepted by prototype/native package evidence alone.
6. New `wilsof doctor` native invocation was not added to this cycle; historical
   diagnostic evidence is not a fresh physical or final-image pass.
7. CI missing; independent human security and proprietary redistribution review
   pending. Public STA-enabled image release remains prohibited by this scope.

## 9. Engineering Standards and documentation delivery

Followed CONTRIBUTING, Engineering Standards, reporting template and scoped
risk/privilege boundaries. Kept the existing authorized integration branch,
shared locks and historical artifacts; private handoff remains untracked and
was not staged. No report-only branch or unrelated development was created.
The new checkpoint separates implemented/source-tested/native-tested/new-image /
physical evidence. Changed-document link, sensitive-content and whitespace
checks accompany final publication; exact remote files are byte-read back.
No merge or feature-completion state follows merely from publication.

## 10. API/model usage where documented

Session-provided model identity: `gpt-6.1-sol`, provider `openai-codex`. Two
independent delegated contexts inherited the configured route. Delivered review
summaries report 7 and 8 API calls respectively; these are self-reported work
metadata, not independently reconciled token totals or invoices. Exact child
runtime-model telemetry, full token/cache totals and actual billed costs are
**unknown**. No alternate paid model or fallback was requested; existing budget
and automation controls were not changed or probed through paid endpoints.
No additional review was started solely to write this report.

## 11. Processes and project locks

Owned QEMU/source supervisor exited **0** after ordinary user poweroff at
15:44:46 UTC. No forced-stop marker. Offline qcow2 check: **0 errors**. Historical
backing identity checks passed, evidence transferred/hashed and scoped synthetic
credential scans completed. QA lock independently available; no QEMU found in
final builder process inspection.

Project lock holder exited **0** and its lock was independently acquired by a
separate probe at **15:54:21 UTC**. Existing worker control remains paused;
queue job remains disabled/paused. Both read-only reviews have completed.
No owned VM/build/test/review workload remains, and nothing automatically resumes.
The prepared owner command itself has not run its privileged phase.

## 12. Next recommended action

Owner review and explicit interactive authorization of the prepared **single
hash-locked private build command**, delivered privately in the terminal. It
reuses retained verified dependencies, requests ordinary sudo authentication,
rechecks root-only prerequisites/isolation/resources, holds both build and QA
locks, limits the service to 2400 seconds and never overwrites historical outputs
or automatically retries. Rootful smoke and actual package signature freeze must
pass inside that phase before the unique candidate is built.

Then independently inspect the produced ISO/source/hash and run all 18 new-image
acceptance gates plus Broadcom/update gates. Physical testing remains a distinct
owner action afterward. No build, VM, worker, merge, release or physical operation
starts automatically from this report.

## Publication receipt

Final exact report/checkpoint commit, verified GitHub URLs, final CI absence and
read-back issue-comment IDs are stored in the private handoff and posted to
#60/#16. This file intentionally does not predict its own containing commit.
