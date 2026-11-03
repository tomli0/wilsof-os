# AS-02 native package build and acceptance checkpoint — 2026-11-03

## 1. Milestone and decision
**Native package build PASS; package inspection PASS; native security acceptance BLOCKED / NO-GO.** Resumed the exact private checkpoint on `fix/as02-native-20261103`; no architecture redesign. Existing AS-02 patch was hash-verified before use and remains unchanged. No integration into other PR branches.

## 2. Exact source and package provenance
Hyprland source `0aa6745f705f2c4b0a5004eb019ef76e5bbdb426`; source archive SHA256 `93b1fc24caca857e31d52717f4879c6f6132644d7b25365e947065dbe99ed125`. Pinned udis86 gitlink `5336633af70f3917760a6d441ff02d93477b0c86`. Result: `hyprland-as02-private 0.57.0-1.1`, 53701518 bytes. Package SHA256 `b81531b9cf70b9f372238539cd64ae7d2ad66b41f1fc429dec6e998c41873a1f`; packaged Hyprland ELF SHA256 `8a4a88e1cfebe165f37b50a9a83cacb2632adce6a3bd66fef44b2365b0c0e096`; ELF Build ID `3e028756ffffaae966ced21992c5bdf2e995d4d5`. Exact recipe, source/patch hashes, dependency list, `.BUILDINFO`, compile commands and full log are retained privately. This is an explicitly private, unsigned local candidate, not an official upstream package.

## 3. Build, flags and quality
Full upstream native CMake/Ninja build and makepkg packaging completed with exit **0**, as UID 1000 in the existing isolated Arch root. Release build, prefix `/usr`, libdir `lib`, skip RPATH, `NO_HYPRPM=ON`, parallelism 2. Explicit generic x86-64 C/C++ flags avoid host-specific ISA requirements; upstream additionally sets optimization/no-LTO options. No AS-02 source change and no compiler correction was needed. Existing package-signature policy was not weakened. Missing build-only hyprland-protocols/meson dependencies were installed using normal signature checks in the isolated root. Package generation warned that two inherited dependency entries were unnecessary; this was not a build failure. Host packages were not replaced.

## 4. Binary inspection and source tests
The actual packaged executable, not just a build-tree binary, passed `--version`, `--help`, ELF Build ID inspection and library resolution with no missing libraries; inspection exit **0**. Four changed native source files matched the preserved candidate byte-for-byte. Earlier 1,025-check extracted-guard RED/GREEN results remain source-seam evidence only and were not presented as native acceptance.

## 5. Fresh QEMU baseline and exact blocker
A new disposable COW guest was booted from the preserved baseline, with copied firmware. Fresh QGA package readback: Hyprland 0.57.0-1; Hyprlock 0.9.6-3; Hypridle 0.1.8-2.1; Quickshell 0.3.2-1; dux-shell 2.0.0-1. Baseline Hyprland ELF SHA256 `1004b8b34c79a473c781b440c4befccc4f427a9b1c833bbd19063156f2644f90`.

The harness falsely accepted `inactive` as `active` via a substring check and began synthetic greeter input prematurely. The authenticated desktop never reached readiness. The test driver then stopped with `boot phase not complete`. This is a **harness failure / inconclusive QA blocker**, not a compositor input-isolation failure, successful reproduction or wrong-password test. The exact false-positive was reproduced from the actual source expression; an exact-state correction passed inactive/active/activating/nonzero-exit source controls. No native retest is claimed. A timed status tool wait also reached the gateway timeout; the existing build was reconciled and allowed to complete, not duplicated.

## 6. Candidate security acceptance and authentication
The candidate supervisor correctly refused to boot a patched guest without a successful fresh baseline. All twelve required native candidate cases are **NOT RUN**: lock acquisition, ordinary-client isolation, Command Center IPC, independent client, wrong/correct password, focus recovery, immediate relock, DMS restart, IPC disconnect, repeated cycles and locker crash. No password was sent into a known-compromised locked session. Synthetic fixture input at a prematurely detected greeter is not successful password login. Historical AS-02 evidence is not substituted for a new baseline.

## 7. Security review and disclosure
A bounded source self-review inventoried direct focus callers and keyboard endpoint/alternative routing context. This is not independent review, exhaustive alternate-protocol acceptance or proof of pointer/touch safety. **Independent review PENDING.** A private upstream report draft was updated but not submitted. Sensitive patch, package, raw QA logs and detailed reproduction remain private. No production security acceptance.

## 8. ISO and artifact preservation
No ISO build or change. Preserved Integration2 `wilsof-internal-2026.11.01-integration2-x86_64.iso`, 2,549,536,768 bytes, SHA256 `cfe0571664b69b94bb8f2aebe0121704aa3e8feb063b11270fee227debc95eec`. ISO, original backing disk, original overlay and firmware hashes were verified unchanged before and after this session. No original QA disk write, historical artifact overwrite, physical installation or Proxmox change.

## 9. Processes, shutdown and storage
The owned baseline guest was shut down through QGA; its recorded process identity was verified exited. Session-owned build/bootstrap/test/supervisor processes were checked exited. Disposable overlay non-repairing offline qcow2 check: **0**. Project lock release/readback occurs after report publication and is recorded in the private checkpoint; no release is inferred from intent. Worker remains paused; Wilsof scheduler remains disabled/paused. Free bytes at 2026-11-03T09:32:34.506715+00:00: 51950972928 (48.383 GiB).

## 10. Git, report and CI
Only this sanitized report is committed/pushed on the isolated remediation branch. Existing PR branches, main, releases and historical reports remain unchanged. No force-push, merge, public package release or detailed security patch publication. Exact remote head/report blob and status issue #16 update are read back. CI is queried separately; no CI-green claim is made.

## 11. Model cost and durable checkpoint
One main agent on the supplied gpt-6.1-sol/openai-codex route; no additional paid agents, reviewer dispatch, worker or scheduler activation. Actual billing remains unavailable. Durable private checkpoint: owner state `wilsof-qa/as02-native-20261103/checkpoint.json`; this run's logs, package, manifest, harness regression, disposable disk and process ownership evidence are in `acceptance-20261103/`. Generated candidate-driver code is explicitly unexecuted WIP, not acceptance evidence. Physical keyboard/GPU and physical-client checks were not performed.

## 12. Next bounded gate
**NO-GO for integration.** Reuse the already built/inspected package without rebuilding unchanged inputs. Validate actual greeter/password readiness using the corrected harness and a native negative control; then perform a fresh baseline reproduction and one corrected-candidate security acceptance cycle, followed by independent review. Start nothing automatically after this checkpoint.
