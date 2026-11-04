# Security boundaries and release gates

## Scope and threat model

Wilsof is an early Arch desktop prototype, not a security-certified product. This document records the repository-level design boundary as reviewed at commit `d4cb093` (2026-10-16) and the controls that must be rechecked for every image or installer revision.

Assets include user files and credentials, disk contents, package/update integrity, authentication state, GitHub/Hermes tokens, and the integrity of the build and installation path. The relevant trust boundaries are:

- an installed user OS, a disposable live ISO, a development VM, and Hermes automation are separate environments;
- an unprivileged desktop user and its user services must not silently become root;
- package repositories, third-party COPRs and GitHub issue/comment text are untrusted input until authenticated or validated by their intended control;
- physical/offline disk access is outside desktop-session protections;
- automation approval is limited to the verified GitHub owner marker described in `docs/github-workflow.md`, not prose in an issue, PR or comment.

Realistic threats include local unprivileged users, malicious filenames or device metadata, compromised dependencies, stolen offline disks, accidental privileged commands, and untrusted public GitHub content. Wilsof does not claim to prevent an already-privileged attacker, a compromised firmware chain, or physical extraction of an unencrypted disk.

## Current design and audit findings

Confirmed and remediated in this revision:

1. **High — tracked privileged remote-access key.** `scripts/install-arch-test-vm.sh` embedded an owner public key, installed it for root, installed OpenSSH and enabled `sshd`. That made a development access path part of every invocation and contradicted the no-shipped-remote-administration default. The script now neither installs OpenSSH nor configures an authorized key or SSH daemon. This changes only future uses of the script; it does not alter VM 113 or any live SSH/network/firewall configuration.
2. **Medium — unclear release-security contract.** The project had ISO safety limits but no consolidated trust boundaries, reporting policy or release gates. This document and the README link provide that contract.

Confirmed controls in current tracked content:

- The live ISO package list excludes OpenSSH, and `docs/iso.md` specifies no daemon, keys, host identity or automatic disk action.
- The test installer refuses an absent, non-40-GiB, partitioned or signature-bearing target before its destructive commands. It is still a single-purpose prototype, not a general installer.
- `wilsof-lock` is a current-user-only idempotent wrapper around PAM-backed Hyprlock; session authentication remains system-owned PAM policy.
- Wilsof desktop, search, idle and screensaver integrations are user-level configuration. Search is local IPC only; the repository has no configured clipboard, search or log upload.
- The GitHub workflow has read-only token permissions in Actions and its local worker verifies a label plus an owner-authored exact marker before selecting a candidate; it does not start a model.

Plausible concerns not resolved by this repository review:

- No supported full-disk-encryption or recovery UX exists. Encryption would protect offline storage, not an unlocked running session, firmware compromise or remotely exposed services. It must be designed and tested separately; do not repartition an existing VM for it.
- Secure Boot is not supported or claimed. Current custom image/kernel/module signing and trust enrollment have not been validated. Do not disable Secure Boot, enroll keys, or make compatibility claims automatically.
- Arch/COPR package trust, current advisories, kernel/module compatibility and update recovery require a dated build-time review using current official upstream sources. Do not permanently bypass signatures or downgrade packages to work around a build failure.
- The prototype installer and live ISO have not been built or booted in this review. Their runtime listener inventory, portal behavior, PAM unlock, idle-lock ordering and failure behavior need isolated VM verification.

## Verification performed

Repository tests cover the absence of desktop passwords and now assert that the prototype installer contains no authorized-key, SSH root-login, SSH daemon or OpenSSH setup. Static review covered installer disk guards, ISO package/configuration, user-service configuration, lock wrapper and automation approval handling. These checks do not demonstrate a physical-client login, lock/unlock, suspend ordering, boot, installation, firewall state or running-service inventory.

## Security reporting

Do not publish credentials or weaponized details of a serious unresolved issue in a public Issue. Report it privately through the existing owner channel with affected revision, severity, minimal evidence and remediation status. Do not rotate credentials or rewrite history without a coordinated plan. Public reports should distinguish confirmed vulnerabilities, plausible concerns and unavailable tests.

## Proposed release gates

These are required evidence gates for a future internal alpha and public ISO; they do not assert that any gate has passed.

| Gate | Internal alpha | Public ISO |
| --- | --- | --- |
| Known high/critical findings | Explicit owner decision required for any unresolved Wilsof-controlled finding | None unresolved without explicit documented owner decision |
| Credentials and access | No embedded credentials, fixed passwords or owner keys; remote services inventoried | Same, plus fresh per-install machine/SSH identity where applicable |
| Package/artifact trust | Package sources, signatures and build provenance recorded | Reproducible or independently reviewed provenance and integrity record |
| Install/upgrade/recovery | Disposable support-matrix VM tested | Stated hardware/support matrix, install, upgrade, recovery and failure paths tested |
| Authentication | PAM lock/unlock and duplicate/failure behavior manually observed | Same across supported desktop paths |
| Encryption and Secure Boot | Limitations disclosed | Supported design tested, or limitations prominently disclosed |
| Human review | Owner review of findings and evidence | Independent human security review still required before public distribution |

## Required physical-client checks

An authorized operator must perform and record: live-ISO boot; graphical login; real PAM password unlock after `Super+L` and idle lock; duplicate-lock and locker-failure behavior; suspend/resume ordering; post-login service persistence; listener/enabled-service inventory; firewall policy; and installer behavior only on a disposable disk. None of these actions are performed by repository CI or this review.
