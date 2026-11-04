# Private experimental compositor package input

This is an opt-in build/install contract, not AS-02 security acceptance. Never
commit a private package, patch, contract, build profile, ISO or acceptance log.
All resulting private images and installed test systems must remain private.

## External inputs

Normal builds leave both variables unset and retain repository Hyprland.
Private builds require both `WILSOF_PRIVATE_EXPERIMENTAL=1` and
`WILSOF_PRIVATE_HYPRLAND_CONTRACT` naming an absolute local JSON file outside the
exported source and disjoint from work/profile/output. Supplying only one input,
an unsupported opt-in value or invalid contract fails before wrapper output is
created. Pass these two variables explicitly through the authorized isolated
builder environment; existing archive/marker, Hypridle and build inputs remain
required. Do not pass checksums on the command line.

The external JSON object has exactly these fields; obtain actual values from
the retained private provenance, not the synthetic public tests:

| Field | Required value |
| --- | --- |
| `schema` | integer `1` |
| `package` | absolute local regular package file, no symlink ancestors |
| `name` | `hyprland-as02-private` |
| `version` | exact reviewed package version, including package release |
| `architecture` | `x86_64` |
| `sha256` | lowercase 64-character SHA256 of the entire archive |
| `binary_sha256` | lowercase SHA256 of packaged `usr/bin/Hyprland` (64 chars) |

Keep the file and artifacts in a private owner-controlled directory, with mode
0700 for directories and 0600 for the contract. No real pin or package is part
of this repository. `bsdtar` reads only the package metadata and executable;
package members are not extracted into the build host. Duplicate/mismatched
name, version or architecture, wrong archive/executable digest, missing input,
symlink or malformed policy is rejected. Failures do not fall back to upstream.

## Image and installed-target flow

The actual package dependency names are added to the normal signed repository
transaction. Repository `hyprland` is removed from the private image and desktop
manifests; the image dependency closure is rejected before download if it would
select repository Hyprland. Full dependency/version/ABI constraints from the
private archive must already be satisfied (`pacman -T`) before local installation.
If the current signed repositories cannot satisfy them, stop: do not downgrade,
disable checks or replace the private package without a separate decision.

Profile preparation copies the exact archive and a normalized policy into the
private image package directory. A separate required-mode marker binds the
policy bytes by SHA256; embedded policy does not retain the external input path.
Missing/damaged policy, marker or package cannot silently select public mode.
All three files are mode 0600. Input records and frozen profile inventory retain
package/executable identity; they are private build evidence, not public uploads.

Archiso customization installs this local package after the existing Hypridle
step. Live provisioning verifies its installed name/version, executable package
ownership and executable SHA256. The installer loads and validates the same
embedded input before disk selection/formatting; its plan digest binds private
identity as well as package selection and execution revalidates the policy.
Target provisioning copies the same archive/policy/marker and installs with
standard `pacman -U`, then verifies the target package and executable. Unexpected
repository Hyprland in an installed transaction causes refusal, not automatic
removal or a successful fallback. Such a failed installation can already have
changed its disposable target; no rollback is promised.

Local package signature policy is not overridden. Repository Required/trusted
signatures, complete dependency verification, fresh DB/cache, frozen input
records, Hypridle pins and prepared `arch-chroot -r` boundaries remain intact.
A signature-policy refusal is a prerequisite failure, not permission to add
`SigLevel=Never`, `--nodeps` or an unsigned repository. No parallel package
manager, private repository, package rebuild or production release mode is added.

## Acceptance limits

Public tests use synthetic archives and substituted Arch tools. They establish
input rejection, orchestration, package selection and post-install identity
checks, not an actual signed Arch transaction, native dependency compatibility,
package hook behavior, installed executable/runtime identity or final ISO.

Before a build: independently review this exact diff and privately exercise the
retained artifact against the supported isolated Arch environment, signatures
and dependency ABI. ISO build, disposable boot/install, actual running-process
identity, lock/unlock/input isolation, DMS persistent-client reconnect, abnormal
locker behavior and physical hardware acceptance remain separate authorized
gates. The private patch is not independently reviewed or upstream accepted.
