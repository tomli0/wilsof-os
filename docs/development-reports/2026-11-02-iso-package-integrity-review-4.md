# Independent Review 4/5 — ISO Build, Package Integrity and System Updates

Date: 2026-11-02. Verdict: **NEEDS REMEDIATION**. Read-only source/fixture review; only this report is committed.

## 1. Exact scope and baseline

Live GitHub reads confirmed PR #47 OPEN at `0abf4a51af2338f14c691c2d325d6abfa2c8a410`, #48 OPEN at `26cf38457efb170d587bd6e1f0b6f353c92fab5c`, and #49 OPEN at `a28d4678bbbaa091337fdab2b331a1b9e56b7e4d`; all unmerged. Inspected their descriptions/comments/reviews and relevant source differences. Dedicated report branch: `review/iso-package-integrity-20261102`, based on Review 3 commit `e977993523b904bf315138d1aefc78ad58b57140` (implementation identical to #49). Build scripts, ISO configuration, pinned-package helper and Hypridle packaging inputs are byte-identical to #47. #48/#49 add account/lock payload files and previously reviewed corrections, not a new package trust/update mechanism.

Read completed Reviews 1, 2 and 3 for context. IS-01/02, AS-01/02/03 and DI-01–04 were not reimplemented or re-reviewed. Their unresolved limitations remain; especially #49's AS-02 deployment blocker is not lifted by this review. This is not a vulnerability/advisory inventory or final-artifact runtime acceptance.

## 2. Findings and required corrections

**Critical: none demonstrated. High: none demonstrated. Medium: two. Low: two.**

### PI-01 — Medium: cache preflight does not establish the promised full-manifest verification

Source: `scripts/build-iso.sh:46–73`; claim repeated in `docs/iso.md:60–68`.

The preflight runs host `pacman -Sw --needed` without the generated profile's configuration. `--needed` omits targets already current in the build host; a new image still needs them. It then scans a hard-coded host cache rather than an explicit resolved transaction/package list. A configured alternative CacheDir can be missed, while an unrelated old corrupt package in the default cache can reject an otherwise valid build. Host signature/repository policy also need not equal the profile policy. These are preflight coverage/false-rejection defects, **not proof that mkarchiso accepts unsigned packages**; mkarchiso performs its own package transaction.

Reproduction: extract and execute only the real Python block at lines 53–74 with a substituted downloader returning 0 and empty cache; it prints “cache preflight passed” after verifying zero cached files. Recorded argv includes `--needed` and lacks `--config`. A second fixture supplies one unrelated cache entry and a failing substituted zstd: the same block refuses the build although the entry is outside its one-package manifest. No real pacman was executed. The empty-cache fixture demonstrates absence of coverage enforcement; actual `--needed` semantics are independently documented by the official pacman manual, not inferred from that substitute.

Correction: resolve/download the image's complete package transaction under the intended profile repository/signature configuration, independent of host-installed status; use an explicit dedicated cache and validate the transaction's exact files rather than all historical cache entries. Add installed-on-host, alternative-cache/config and unrelated-corrupt-cache tests. Do not weaken signatures or indiscriminately clear preserved caches.

### PI-02 — Medium: the source revision is not a reproducible build-input identity

Source: `scripts/build-iso.sh:10–18,36–38,61,78`; `scripts/prepare-iso.py:17–24,63–65`; `iso/profiledef.sh:5–8`.

The wrapper validates a source-marker string but consumes the build machine's current releng profile, tools, repository databases/mirrors and unversioned package names. It neither enforces documented Archiso 91 nor freezes these external inputs. `FILES.sha256.json` describes the embedded Wilsof source payload, not the whole build environment or resolved package closure. Even with fixed `SOURCE_DATE_EPOCH` and `WILSOF_ISO_VERSION`, `iso_label` still depends on wall-clock month.

Verified source-level counterexamples: materialize two profiles with the same source/commit marker but different fixture releng manifests; the effective package manifests differ. Evaluate the real profile with mkarchiso's associative-array precondition, identical fixed epoch/version and two substituted current months: labels are `WILSOF_202601` and `WILSOF_202602`. No ISO was built; no claim of observed differing ISO hashes is made. This is a confirmed missing reproducibility contract, not evidence of malicious packages or a previously promised bit-for-bit guarantee.

Correction: capture/enforce supported tool/profile versions, immutable repository snapshot or equivalent package closure with versions/hashes/signature provenance, build environment/keyring identity and deterministic clock-derived profile metadata. Distinguish “traceable reviewed source” from “reproducible ISO”. Test repeat materialization before separately authorized repeat builds.

### PI-03 — Low: the build instructions' displayed command fails required-input preflight

Source: `docs/iso.md:43–58` versus `scripts/build-iso.sh:11–18`; correct fuller example exists at `docs/internal-test-runbook.md:15–35`.

The displayed sudo command supplies only work/output paths; it neither supplies `WILSOF_SOURCE_COMMIT`/`WILSOF_HYPRIDLE_PACKAGE` nor creates the required archive marker. A preceding `WILSOF_APPROVED_COMMIT` check is not equivalent. In a sanitized fixture environment, the exact two-variable invocation with substituted root-id/mkarchiso exits 2 at missing `WILSOF_SOURCE_COMMIT`, before package/build execution. Safe refusal limits severity; a previously configured environment is not a self-contained instruction.

Correction: replace the obsolete checkout invocation with the existing reviewed archive/marker/package procedure, explicitly pass required variables through sudo, and test the example's actual contract rather than only substrings. Also reconcile stale no-installer/no-autologin/path statements in that document with the current runbook.

### PI-04 — Low: output/profile directory collision is accepted by the path guard

Source: `scripts/build-iso.sh:25–38`; downstream refusal `scripts/prepare-iso.py:15–17`.

For new work `/scratch/work` and output `/scratch/work-profile`, existing validation passes. `mkdir -p OUTDIR` then creates precisely the profile directory that prepare requires to be absent, causing guaranteed early failure. Reproduced with the real wrapper and scratch-only root-id/materializer/mkarchiso substitutes: exit 1, “Output profile must be a new dedicated directory”, no mkarchiso invocation. This is avoidable startup failure, not demonstrated artifact overwrite.

Correction: validate all three canonical directories together (work, derived profile and output), rejecting equality/nesting before any mkdir. Add this boundary regression and retain the no-overwrite rules.

## 3. Existing protective mechanisms and trust trace

- Build invocation requires explicit `--build`, root, mkarchiso, a 40-hex reviewed marker, supplied internal package, new work/profile and empty disjoint work/output. It retains work/profile and omits destructive `mkarchiso -r` (`build-iso.sh:5–38,75–78`). Isolation is a documented prerequisite, not a sandbox established by this wrapper; authorization must establish it externally.
- Materialization uses an explicit image allowlist, rejects traversal/source symlinks/missing files, and records embedded source hashes (`prepare-iso.py:47–65`). It removes remote-access/cloud components and does not copy a whole developer checkout/home. These hashes detect byte differences relative to their manifest; they do not independently authenticate their own origin or the claimed Git commit.
- Exact upstream Archiso **v91** releng configuration retrieved for context uses `SigLevel = Required DatabaseOptional` and `LocalFileSigLevel = Optional`. Wilsof inherits the supplied profile's pacman configuration rather than disabling signatures. DatabaseOptional is not mandatory database-signature verification; Optional for local files is not proof of official signing. A deliberately weakened fixture config was copied unchanged: this establishes lack of policy validation, not weakened policy in the historical ISO. Effective build/target configuration and keyring still need explicit acceptance.
- Internal Hypridle is a separate trust exception: exact package SHA256 and installed-executable SHA256, filename and non-symlink paths are enforced before/after local `pacman -U`; failures propagate (`runtime/pinned-package.py:36–59`). It is not falsely presented as an officially Arch-signed custom build. Current PKGBUILD and patch hashes match `packaging/hypridle/provenance.json`; local source inputs have checksums, not moving network downloads (`PKGBUILD:12–16`). No custom package was built, installed or signature-verified here.
- The verified internal package is copied into the live image and applied during customization, then copied/applied to the installed target (`prepare-iso.py:68–78`, `runtime/provision-target:65–73`). Chroot capability is gated, API filesystems/resolver handling delegated to supported arch-chroot, and nonzero installation/binary-verification failures are not treated as success.
- Live manifest combines upstream releng, ISO overlay and the shared desktop manifest (`prepare-iso.py:19–24`). Installed packages combine base/kernel/firmware/boot/microcode with that desktop list; a digest binds the reviewed names before execution (`installer/wilsof_installer.py:170–195,221–242`). This digest does **not** bind resolved versions/bytes; the later internal package overlay also sits outside that name-list digest.

## 4. Firmware, drivers and third-party boundaries

Live explicitly requests `linux-firmware`; installed base requests it plus Intel/AMD microcode (`iso/packages.x86_64:4–5`, installer `176–179`). Shared desktop includes `sof-firmware` (`runtime/desktop-packages.txt:23–24`); existing contract tests passed. These are provisioning intentions, not proof that firmware loaded on any physical GPU/audio/Wi-Fi adapter. Proprietary NVIDIA modules, Secure Boot, DKMS/kernel compatibility, unusual adapters and initramfs recovery need separate hardware/runtime evidence.

No new third-party Arch repository or AUR helper is added by the reviewed ISO/installed path. The older Fedora bootstrap enables COPRs; that is a different platform path, not implicit permission to trust them for this Arch ISO. The build host and supplied releng/mirror/keyring remain trusted external inputs. Do not extrapolate a safe inherited default to an arbitrary modified host/profile.

## 5. Update process, approval and configuration preservation

Implemented documented system update is explicit `sudo pacman -Syu`, with Arch-news review and no selective post-`-Sy` upgrade (`docs/internal-test-runbook.md:108–120`). It is separate from unprivileged `wilsof-config-update`, which executes reviewed local user-file provisioning, not a package updater (`bin/wilsof-config-update:4–13`). No new unattended upgrade service or approval bypass was found in this scoped path. Existing Review 3 preservation defects are not duplicated here.

DMS's contextual v2.0.0 pacman backend constructs full `pacman -Syu --needed`; Wilsof's product architecture describes curated update UI as future work, and its settings template does not add a system-update widget. This review does not certify actual upstream UI authorization, privilege prompts, background checks or running-package behavior.

The custom Hypridle hash is an **installation-time** pin, not an enduring update policy. A later higher official package version may replace it during full upgrade; no coordinated patched-package publication/update policy is supplied here. This is an unresolved maintenance risk, not proof the current repository offers a higher vulnerable version. Do not “fix” it with indiscriminate IgnorePkg/partial upgrades. Require patch-upstream status, supported dependency versions and coordinated full-upgrade testing.

## 6. Interrupted operations and unverified runtime risks

Build `set -eu` and subprocess checking stop on errors; retained work/profile and nonempty-output refusal protect evidence but do not provide automatic resume/cleanup. Preserve partial output/logs and verify no mounts/owners remain before separately authorized cleanup. PI-04 concerns validation, not permission to delete or retry in place.

Neither per-file configuration backups nor ordinary pacman installation provide transactional OS/boot rollback. Interrupted package extraction/hooks, stale database lock ownership, full ESP/filesystem, power loss, keyring expiry/rotation, mirror/database drift, ABI changes and post-kernel reboot require disposable integration tests and a recovery procedure. Never remove a lock without proving its owner is gone, disable signature checks, or describe rerunning an interrupted upgrade as universally safe. No such failure was induced on a real system.

## 7. Executed evidence

At implementation #49 / report base Review 3:

    PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -rs -p no:cacheprovider --basetemp=FRESH_SCRATCH       tests/test_pinned_package.py tests/test_iso_materialization.py       tests/test_iso_cleanup_contract.py tests/test_image_payload_contract.py       tests/test_boot_experience.py tests/test_hardware_diagnostics.py       tests/test_chroot_contract.py tests/test_iso_build_documentation.py

**53 passed in 0.82s**, exit 0. All package/build commands in relevant fixtures are substituted; no actual package install/update, ISO build, mount or boot. Focused ShellCheck of build wrapper/profile and diff whitespace checks passed. Private scratch evidence: `wilsof-review4-20261102-probes.py`, fixture `results.json`, and supplemental results. New fixture code is not committed.

A retrieval helper failed because this session's extraction backend is search-only; primary pages were retrieved read-only via HTTP instead. Initial clock fixture lacked mkarchiso's associative-array declaration and failed; the corrected clock fixture is the evidence above. Neither orchestration failure is a production-source defect or an excuse to fabricate native results.

Primary references retrieved 2026-11-02: [pacman command contract](https://man.archlinux.org/man/pacman.8.en), [pacman signature/configuration contract](https://man.archlinux.org/man/pacman.conf.5.en), [Archiso v91 releng](https://github.com/archlinux/archiso/blob/v91/configs/releng/pacman.conf), [mkarchiso v91](https://github.com/archlinux/archiso/blob/v91/archiso/mkarchiso), [DMS v2 pacman backend](https://github.com/duxlabs-dev/dux-shell/blob/v2.0.0/core/internal/server/sysupdate/backend_pacman.go). No current vulnerability/CVE clearance is implied.

## 8. ISO provenance and preservation

Historical Integration2 source is `b755bfabf82ece67eea3d666ea94330ff95f738e`, not the later review/remediation heads. Existing ISO size **2549536768 bytes**, SHA256 **`cfe0571664b69b94bb8f2aebe0121704aa3e8feb063b11270fee227debc95eec`**, independently read and matched during this review. A checksum establishes content identity relative to the recorded trusted reference, not a publisher signature/reproducible-build attestation. This report does not create a new signed release manifest.

All 51 discovered paths under the preserved artifact root were inventoried before review work for device/inode/mode/size/mtime/ctime comparison. Additional QA-root metadata is inventoried before publication. Final read-back must recheck these inventories and the ISO hash; totals/results are in the publication receipt. This is not a fresh content-hash audit of every QA artifact, nor an inventory of all possible external locations. No artifact was opened writable or attached to a guest.

## 9. Publication/source preservation

Only this report is committed/pushed on `review/iso-package-integrity-20261102`. Verify exact remote branch/report bytes and every captured pre-existing remote head after push; require a clean tree and report-only diff from Review 3. Existing worktrees/branches are retained. Publication is not CI-green, merge, release or acceptance. No PR or scheduler/worker activation is requested.

## 10. Actual execution and budget

One review agent, no delegation or auxiliary AI CLI; at most twelve main tool rounds including publication/read-back. Actual model billing unavailable. No new dependencies, QEMU, ISO builds, system updates or installation. All processes are synchronous review/fixture commands; no VM/build execution lock was acquired or released and automation controls were untouched, not re-certified.

## 11. Storage/checkpoint

Scratch available at 2026-11-02T10:31:39.379170+00:00: **63957901312 bytes**. Private evidence and final preservation/publication receipt are retained beside the isolated clone. Original source worktree/QA paths were not edited; the report branch is the sole repository write deliverable.

## 12. Verdict and stop

**NEEDS REMEDIATION:** correct the preflight contract and freeze/document reproducibility inputs; repair the documented invocation and three-directory validation, with focused regressions. Separately authorize package/runtime/hardware recovery acceptance and retain previous review blockers. **Stop after Review 4/5. Do not begin Review 5 or implement fixes automatically.**
