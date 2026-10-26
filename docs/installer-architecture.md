# Wilsof installer and hardware-support architecture

Status: design and non-destructive scaffolding only. This document does not authorize an ISO build, boot, disk write, installation, release, or hardware claim.

## Decision record: reuse `archinstall` behind a Wilsof planner

Wilsof will retain the versioned Archiso `releng` overlay described in `docs/iso.md`, and will use the maintained `archinstall` backend through a narrow adapter for a future dedicated-disk, GPT/UEFI install. The Wilsof UI is a keyboard-operable, thin presentation layer; it produces a validated installation plan and never builds shell strings from UI input. The privileged adapter accepts only a schema-validated plan after an immediate disk re-probe.

The choice is conditional on a future pinned `archinstall` release passing the VM test matrix. `archinstall` has a guided installer, documented JSON configuration and disk/bootloader configuration interfaces. It avoids writing a partitioner while keeping the backend replaceable if its versioned interface cannot satisfy the safety contract.

Alternatives considered:

- Custom Bash/Python partitioner: rejected; it duplicates high-risk storage, bootloader and package-install logic. The existing `scripts/install-arch-test-vm.sh` is explicitly a VM-113 single-use prototype and must not be generalized or invoked by the live UI.
- Expose the stock `archinstall` guided UI: rejected; Wilsof cannot ensure its own hardware summary, consent language, plan/revalidation boundary or consistent UX.
- Calamares: not selected now; it is a larger integration surface and would need equivalent backend, packaging and safety evaluation. Re-evaluate only if the adapter route fails its VM contract.

Sources consulted 2026-10-16: Archiso documentation states `releng` is the intended customizable profile; Arch `archinstall(1)` documents guided installation and JSON disk/bootloader configuration. See `docs/iso.md` and the upstream links in issue #11 for the source URLs. These sources are design inputs, not compatibility guarantees.

## Boundaries and traceability

The image/build manifest records: Wilsof source revision, source date, archiso/archinstall versions, package repository snapshot or resolved package versions, generated ISO filename/checksum, and build tool versions. This gives traceability, not a claim of bit-for-bit reproducibility.

No distributable image or plan may contain personal credentials, enrolled keys, fixed passwords, SSH keys, hostnames, serial numbers, machine IDs or automatic upload endpoints. The live environment does not mount internal Windows filesystems read-write automatically. The probe is read-only; previewing the UI is non-destructive.

## Staged flow and authority boundary

```
Archiso releng + Wilsof manifest
  -> read-only probe -> versioned compatibility resolver -> UI review
  -> validated installation plan -> fresh disk identity revalidation
  -> privileged archinstall adapter -> target finalization -> validation report
```

1. Boot USB: Try Wilsof or Install Wilsof. Installation first collects language, keyboard and connectivity state.
2. The probe produces a local report. The resolver reports tested, expected, known limitation, or unknown; unknown never becomes a fabricated supported profile.
3. The UI shows the hardware summary, target disk, account/encryption choices, optional driver and separate codec recommendations, then a final immutable summary.
4. The executor re-probes the selected disk immediately before any future destructive operation. Any path, capacity, model/serial-derived stable identifier mismatch, new partition/signature, or mounted target aborts before invoking the backend.
5. The backend creates only the reviewed dedicated-disk GPT/UEFI layout. The target is finalized with selected firmware/packages, initramfs, boot settings, desktop and network settings; then it is validated before success is displayed.

The executor uses structured arguments/API calls only; device descriptions and UI labels never become shell code. Stages are `validated`, `partitioned`, `base-installed`, `configured`, `boot-configured`, and `validated-target`. It records an append-only local stage log. Before formatting, cancellation stops safely. After formatting, no rollback promise is made; recovery is to stop, preserve the log, identify the exact stage, and provide a reinstall/support path rather than continuing blindly.

## Read-only hardware report schema and example

```json
{
  "$schema": "wilsof.hardware-report/v1",
  "collected_at": "2026-10-16T00:00:00Z",
  "cpu_arch": "x86_64",
  "firmware": {"uefi": true, "secure_boot": "enabled"},
  "graphics": [{"pci_id": "8086:46a6", "class": "0300"}],
  "network": [{"pci_id": "8086:51f0", "class": "0280"}],
  "storage": [{"path": "/dev/nvme0n1", "size_bytes": 512110190592, "partition_table": "gpt", "mounted": false}],
  "usb_ids": ["0bda:8153"],
  "privacy": {"serial_numbers_collected": false, "uploaded": false}
}
```

Required fields are schema version, collection time, architecture, firmware state, arrays for graphics/network/storage and the privacy assertion. IDs are PCI/USB vendor:device IDs only. No serial number is collected. Secure Boot is `enabled`, `disabled`, or `unknown`.

## Compatibility rules

Rules are versioned data, reviewed separately from probing. Each rule contains `id`, `version`, match criteria (PCI/USB ID and platform constraints), package source, package list, kernel/module pairing, firmware requirement, licensing/redistribution note, conflicts, evidence reference, status, and limitation. Status is exactly `tested`, `expected`, or `known-limitation`; lack of a matching rule is `unknown`.

```json
{
  "schema": "wilsof.compatibility-rule/v1",
  "id": "intel-graphics-base",
  "version": 1,
  "match": {"pci_ids": ["8086:46a6"], "arch": "x86_64"},
  "source": "Arch official repositories",
  "packages": ["mesa", "linux-firmware"],
  "kernel_module": {"kernel": "linux", "module": "i915"},
  "firmware": "linux-firmware",
  "licensing": "Verify package redistribution terms at ISO build pin time.",
  "conflicts": [],
  "evidence": "hardware-matrix: intel-graphics-pending",
  "status": "expected"
}
```

Base kernel support and redistributable firmware needed for normal operation belong in the base image. The resolver never silently adds repositories, runs vendor installers, or treats a proprietary package as an external repository merely because it is proprietary. Secure Boot and external module signing are explicit rule constraints; Wilsof does not disable Secure Boot and does not claim unsigned external modules boot universally.

## Installation plan schema and example

```json
{
  "schema": "wilsof.install-plan/v1",
  "plan_id": "uuid",
  "target": {"path": "/dev/nvme0n1", "size_bytes": 512110190592, "identity": "stable-hash", "expected_empty": true},
  "layout": {"mode": "whole-disk", "table": "gpt", "firmware": "uefi", "partitions": ["ESP", "root"]},
  "bootloader": "systemd-boot",
  "account": {"username": "chosen-at-execution", "password_in_plan": false},
  "encryption": {"enabled": false},
  "optional_packages": ["intel-media-driver"],
  "codecs": {"selected": false},
  "review_digest": "sha256-of-canonical-plan",
  "executor": {"adapter": "archinstall", "adapter_version": "pinned-before-release"}
}
```

This schema is non-destructive scaffolding, not authorization to execute an installation. `layout.partitions` is exactly the two symbolic entries `["ESP", "root"]`, in that order; nulls, objects, other names and additional partitions are rejected. These are reviewed layout roles, not arbitrary backend partition parameters. A future pinned adapter must define and test their concrete sizes, filesystems and mount options before disk operations are enabled.

`encryption` contains only the required boolean `enabled`. Both choices are valid plan data, but passwords, passphrases, key-file paths, nested credentials and all other properties are rejected regardless of that choice. A future executor must obtain secrets through a separate transient input channel, never from the canonical plan or its logs; this schema does not implement encryption.

Schema validation checks the represented GPT/UEFI, whole-disk and expected-empty constants, required target identity, and object/field constraints. It cannot inspect disk state or prove identity freshness. The future read-only probe, compatibility resolver and executor must additionally reject mounted/non-empty targets, unsupported architecture, arbitrary repositories and unsupported rule status, and revalidate the target immediately before execution. The UI and executor must render the same canonical plan and check its review digest. No executor is enabled here.

Run the non-destructive contract tests with `python3 -m pip install -r requirements-dev.txt` and `python3 -m pytest -q`. Tests validate the documented example and malformed plans with a Draft 2020-12 validator; they do not probe or modify a disk.

## Recommended-driver and codec UI

Primary choice:

    Install recommended drivers
    Adapts Wilsof to your detected graphics and Wi-Fi hardware. Some drivers have separate license terms.

Only actual additional recommendations appear, each with purpose, source, network requirement, license note and tested/expected status. If none apply: `No additional drivers are recommended for detected hardware.` Declining shows specific limitations from the rule; it does not promise functionality. Codecs are a separate, unchecked option with source/license and network requirements. Offline behavior is bounded: packages present and verified on the image may be selected; missing optional packages are marked unavailable and do not block base installation. Online fallback requires an explicit connected state and confirmed official package source.

Unsupported state: `Wilsof has no verified recommendation for <device ID>. Continue with base support only, review the limitation, or cancel. No driver will be downloaded automatically.`

## Dedicated-disk safety and Windows handling

First alpha accepts only a dedicated target disk with GPT/UEFI on x86-64 Intel/AMD systems. It refuses Windows ARM, Apple Silicon, legacy BIOS, dual-boot resizing, pre-existing partitions/signatures, RAID/RST/AHCI changes, and automatic Secure Boot/BitLocker changes. Existing Windows and encrypted/unsupported storage are detected conservatively and explained. The final summary explicitly states: `Whole-disk installation erases all data, including Windows, on the selected disk.` The selected disk's identity/state are revalidated immediately before execution.

## Hardware matrix and verification plan

| Profile | Live + installed checks | Status |
| --- | --- | --- |
| UEFI VM, empty dedicated disk | boot, install flow, lock/unlock, networking, storage, suspend/resume, kernel update | required before alpha; untested |
| Intel graphics PC | graphics, scale/brightness, Wi-Fi/Ethernet, audio, keyboard/touchpad | required; untested |
| AMD graphics PC | same as Intel | required; untested |
| Nvidia/hybrid | rule resolution and boot/module/Secure Boot constraints | separate track; unknown |
| Owner 2014 Intel MacBook | obtain exact model and read-only PCI/USB inventory before rules; Wi-Fi/camera/input/audio | separate track; blocked on physical inventory |

Each test records image manifest, device IDs, rule versions, live/installed result and limitation. Only physically exercised combinations become `tested`; all others stay `expected` or `unknown`.

## Existing mapping and follow-ups

`iso/profiledef.sh`, `iso/packages.x86_64` and `scripts/build-iso.sh` are the live-image/build layer. `scripts/install-arch-test-vm.sh` is a destructive, VM-113-specific prototype and is out of scope for the production adapter. `bin/wilsof-doctor` is the candidate installed diagnostics entry point and should consume compatibility/report data without network upload.

Bounded follow-ups requiring separate approval: (1) implement and unit-test the read-only probe using fixture inventory, (2) implement resolver/plan validation with mock executor only, (3) pin and test an archinstall adapter in a disposable UEFI VM, (4) physical Intel/AMD and owner-MacBook validation. None authorizes hardware installation, ISO publication, VM creation, disk changes, or deployment.
