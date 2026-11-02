# Installer Safety Remediation 1/5 — IS-01 and IS-02

Status: **Both confirmed source findings corrected and regression-tested; draft review requested, not merged or deployed.**
Work began 2026-11-01 23:53 UTC; final source/ISO verification crossed midnight to 2026-11-02 00:02:57 UTC. Branch names retain their creation date.
Authoritative baseline: `review/installer-safety-20261101` at `149f7b9449a4c20c10cb6cd22fd217da3c7165de`, [review report](2026-11-01-installer-safety-review-1.md).
Remediation branch: `fix/installer-safety-20261101`, based directly on that review commit. Integration2 remains `0abf4a51af2338f14c691c2d325d6abfa2c8a410`.

## 1. Completed changes

Only IS-01 and IS-02 were addressed. Changes:

- `installer/accounts.py`: one shared `validate_username` policy, preserving the existing syntax/length rules and rejecting reserved base/desktop service identities, including `greeter`, `daemon`, and the `systemd-` namespace. The list also covers identities observed read-only in preserved Arch sysusers configuration. It does not enumerate this host's user database or depend on host UID allocation.
- `installer/wilsof_installer.py`, `validate_plan`: calls the shared policy and translates its ValueError to Refusal. Existing interactive ordering validates before password/ERASE confirmation and all filesystem operations; execution revalidates the plan too.
- `runtime/provision-target`, `validate_target`: uses the same policy instead of its separate regex. Existing UID >=1000, dedicated `/home/USERNAME`, root/live, symlink and initialized-Arch checks remain. Source-tree execution loads the sibling shared policy; the copied helper loads the fixed `/usr/share/wilsof/source/installer/accounts.py` payload. Missing policy fails closed.
- `runtime/image-files.txt`: includes the shared policy in the explicit payload manifest. No existing ISO is updated.
- `installer/wilsof_installer.py`, `check_target_mount`: strictly resolves the destination, requires an absolute canonical empty directory, refuses leaf/ancestor symlinks, resolves mount-table entries, and compares canonical equality/descendancy. OSError and RuntimeError during resolution/inspection become Refusal. The existing last pre-format recheck remains in place.
- `tests/test_installer_safety.py`: reserved/ordinary usernames at both boundaries, early interactive refusal, retained UID/home checks, ancestor symlinks, target/nested mounts, canonical mount-table aliases, resolution failures, safe empty targets, actual scratch payload materialization and copied-helper policy lookup.

No unrelated runtime, password, partition layout, cleanup, firmware, greeter, desktop, build or scheduler behavior was changed.

## 2. RED → GREEN evidence

One independent read-only pre-commit reviewer examined the five scoped change paths and returned `passed=true`, with empty security, logic-error and suggestion lists. It ran no tests or writes; this is remediation verification, not Review 2. Direct TDD execution:

| Stage | Actual result | Reason |
| --- | --- | --- |
| A RED, original production code | 23 failed / 8 passed | Reserved names accepted at one/both boundaries; greeter/daemon reached password prompt instead of refusing |
| A GREEN + B RED | 7 failed / 32 passed | Account slice green; mount alias and resolution-error tests failed because no refusal occurred |
| Final dedicated safety tests | 47 passed, 0.26s | Both findings plus payload/valid-input/error checks green |

A was implemented only after its observed RED. B was implemented only after its observed RED. Further cases cover additional observed reserved identities and payload delivery. No real device, mount or archinstall backend is used by these regressions.

## 3. Verification commands and results

All tests used `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, and distinct newly created scratch `--basetemp` directories. Native chroot/wallpaper opt-in variables were unset; no privileged test was opted in.

    python3 -m pytest tests/test_installer_safety.py -q -p no:cacheprovider --basetemp=FRESH_SCRATCH_GREEN

Result: **47 passed in 0.26s**.

    python3 -m pytest -q -p no:cacheprovider --basetemp=FRESH_SCRATCH_RELEVANT \
      tests/test_installer_safety.py tests/test_installer_runtime.py \
      tests/test_installation_plan_validation.py tests/test_installer_architecture.py \
      tests/test_desktop_runtime.py tests/test_chroot_contract.py \
      tests/test_arch_installer.py tests/test_iso_materialization.py \
      tests/test_image_payload_contract.py tests/test_live_environment.py \
      tests/test_live_recovery.py tests/test_arch_chroot_integration.py

Result: **182 passed, 1 skipped in 1.32s**. Skip: explicit opt-in native chroot test.

    python3 -m pytest -q -p no:cacheprovider --basetemp=FRESH_SCRATCH_FULL

Result: **422 passed, 2 skipped in 19.02s**, exit 0. Native chroot and wallpaper lifecycle opt-ins not run.

    shellcheck --exclude=SC1091 --shell=sh \
      bin/wilsof-session bin/wilsof-doctor bin/wilsof-help bin/wilsof-lock \
      bin/wilsof-search bin/wilsof-vm-test-binds scripts/bootstrap-desktop.sh \
      scripts/build-iso.sh scripts/install-user-config.sh \
      scripts/preflight-arch.sh scripts/preflight-fedora.sh
    shellcheck --shell=bash automation/wilsof-github-worker.sh \
      scripts/install-arch-test-vm.sh iso/profiledef.sh

Both ShellCheck commands: exit 0, no diagnostics. They analyze text only; scripts were not executed. AST parsing of changed Python/runtime code and `bin/wilsof-profile`, three existing JSON configuration parses, and `git diff --check` passed. An added-line security-pattern scan passed; all 32 distinct system-user identities observed in preserved Arch sysusers files were rejected by the shared policy. Self-review confirmed unchanged destructive-call ordering, retained post-probe target recheck, shared policy payload inclusion and no credential logging.

## 4. Commit and CI status

Tested bytes: review baseline plus the five code/manifest/test paths listed in section 1. A final commit additionally contains only this report; publication SHA, draft PR identity and exact remote-blob read-back are supplied in the terminal receipt. No self-referential commit hash is fabricated here.

The existing Validate workflow filters do not include this remediation push branch or review-base branch. Local suite success must not be described as GitHub CI success. Remote checks, if any, are reported separately after publication. Neither Integration2 nor the original review branch is modified.

## 5. Existing ISO preservation

Before implementation, recursively discovered `wilsof*.iso` under the local user home and recorded path, byte size and SHA256. After all source tests, repeated discovery and all hashes: **18/18 paths unchanged**, representing **8 distinct content hashes**. Paths may be duplicate copies/links; these are not claimed to be 18 unique images. Local baseline is retained privately as `installer-remediation-iso-before-20261101.json` in scratch; no private artifact paths are published.

Integration2 ISO: **2,549,536,768 bytes**, SHA256 `cfe0571664b69b94bb8f2aebe0121704aa3e8feb063b11270fee227debc95eec`, unchanged in every discovered copy. Verification finished **2026-11-02T00:02:57.436275+00:00**. No ISO was built, mounted or modified. Discovery is scoped to accessible matching paths under the local user home, not remote storage or all possible image filenames.

## 6. Installation results

Not run: no QEMU, physical storage operation, formatting, mount, chroot, full installation, bootloader execution, or Proxmox change. Synthetic inventories/mount tables and ordinary temporary files only. Payload materialization copied source files into a temporary profile; it was not an ISO build. Existing installed disks/firmware were not modified or claimed re-certified.

## 7. Boot and password login

Not performed. Prior Integration2 acceptance remains historical; no new physical-client, authentication, graphical-session or reboot acceptance is inferred from these source tests.

## 8. Remaining limitations

- Reserved-name policy is shared, explicit and maintained with package changes; it is not a promise to predict arbitrary future third-party package accounts. New target packages introducing service identities must extend this one policy and its regression coverage.
- Provisioning still verifies actual target UID/home; the pre-format policy cannot inspect the user database of a not-yet-created root filesystem.
- Mount/path checks are fail-closed snapshots, not atomic protection against privileged concurrent path or storage mutation. No hotplug/concurrency fix was in scope.
- Real backend cleanup, interrupted formatting, firmware-variable side effects and physical media behavior remain untested under the existing review's limitations. No unrelated risk was silently declared fixed.

**Disposition:** IS-01 and IS-02 are remediated in source and deterministic tests. Ready for draft code review; not release/installation certification.

## 9. Workflow

Isolated remediation worktree based on the authoritative review commit. Stage only the five change paths plus this report. Draft PR base is `review/installer-safety-20261101`, not Integration2 or main. No merge, release, force-push, dependency installation, unrelated feature or automatic follow-on review. Follow `CONTRIBUTING.md` and report-only publication controls. Original review report retained unedited.

## 10. Model/API cost

One active implementer, gpt-6.1-sol/openai-codex, plus one small delegated read-only pre-commit reviewer. Actual billed cost/token totals unavailable; no provider probe or cost-zero claim. Parent work bounded to twelve agent iterations; the reviewer was not authorized to modify anything or begin Review 2.

## 11. Processes, controls and storage

Only synchronous source checks, fixture tests, read-only ISO hashing and Git publication. No background process, project worker, scheduler, builder, VM or privileged installer started. No scheduler/worker control file changed. No protected process lock acquired/released on another session's behalf. Existing artifact files preserved; scratch fixtures are new. Final timestamped free-byte reading is provided with the publication receipt.

## 12. Next action and stop boundary

Owner reviews the draft remediation PR and the deterministic tests. Any merge, new ISO or disposable runtime acceptance requires separate approval. No physical test is performed by this task. **Stop after this remediation report; Review 2 is not started.**
