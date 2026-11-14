# Source provenance and independent implementation

Status: **bounded evidence review; complete origin certification is pending**.
Wilsof must not copy, port, adapt, translate or repackage Omarchy code, scripts
or configuration, or use it as a build, installation or runtime dependency.
Shared components must come directly from their original upstream projects.
This is a development requirement, not an unsupported claim about all past code.

## Reviewed identity and method

The review covers source commit
`357b0b09d0333c8875a3d4d4ca8db417343d032e`: 379 tracked paths, 336 UTF-8 text
files, and 165 reachable commits in a non-shallow Git history. Each of the 111
tracked paths under the runtime/build directories was mapped to its first recorded
Git introduction. Tests, documentation and assets were also included in the
tracked-content scan; private untracked handoffs were excluded from the audit.

The accepted RC4 image remains pinned to
`5699844ebb805a0553e991ac6e6e5506ee6de122`. The later presentation commit does not
change its runtime source. Image identity and acceptance are recorded in
[Getting started](getting-started.md); this review is not new ISO acceptance.

The review used existing Git objects, input recipes, dependency manifests,
provenance records, direct upstream commit/tag metadata and license-file hashes.
No comparison-distribution source was cloned, vendored or incorporated into
Wilsof. The retained comparison evidence contains public path/hash trees and
commit metadata only; no reference implementation was used as project input.

## Findings

### No confirmed prohibited import in the inspected project source

No Omarchy/related distribution download URL, Git import, package dependency or
build/runtime source endpoint was found in the inspected tracked inputs. The only
name reference under the runtime/build directories is an existing installer
whole-disk data-loss warning in
[`installer/wilsof_installer.py`](../installer/wilsof_installer.py). It is not an
import or dependency. Three test references and historical planning references
must not be confused with evidence of code copying.

The runtime/build history search identifies that warning's introduction, not a
recorded distribution-code import. The repository has no tracked Git submodules.
These observations do not establish the origin of every line.

The original development conversation was recovered. Its recorded generation
requests for the initial Hyprland configuration and two session units match the
root commit byte-for-byte. The HTML prototype's generation event and 7,089-byte
size were confirmed; its historical request was inspected but not independently
extracted for a full byte comparison. These are actual drafting records, not an
inference from a Git author name, and still not an absolute originality proof.

### Exact-blob comparison: no project matches in the checked snapshots

All 895 distinct reachable local Git blobs were compared with the complete blob
identifiers from two reference trees: the observed default snapshot and the latest
snapshot at or before Wilsof's first commit on October 14, 2026. No exact local
blob identifier matched either reference tree.[1] [2]

This detects only complete byte-identical files in those two snapshots. It does
not rule out modified copies, copied fragments, generated derivatives, other
reference versions or unrecorded inputs. It is not a similarity audit or proof
that no prohibited code has ever been used.

### Direct upstream inputs have checkable records

- Dux shell: the declared `2.0.0` source commit and shared-QML Git link resolve
  directly to their upstream repositories. All five retained supplemental notice
  files match their declared direct upstream bytes, including the independently
  pinned shared-QML notice.[3] [7] [21]
  The retained IPP, Plasma and VSIX notices were also checked separately against
  that exact shell commit.[8] [9] [10]
- Hypridle: the recorded `v0.1.8` tag resolves to the pinned commit. Local recipe
  and patch digests match their retained provenance record.[4]
- Hyprland portal: `v1.4.1` resolves to the pinned base commit; the teardown fix
  resolves to the separately recorded upstream fix. Local retained patch/harness/
  license hashes match their provenance record.[5] [6]
- Externally supplied compositor: the original native-build custody records were
  recovered. All 1,341 files in the retained pristine archive match the pinned
  direct Hyprland Git tree. Source archive, local patch, recipe and package hashes
  match those records, and the package embeds the recorded patch. The follow-up
  below also binds that retained package, patch and executable to exact RC4.[22]
- Archiso: all ten retained v91/v92 fixture files were fetched directly from the
  recorded upstream URLs and matched both recorded and local SHA-256 values.
  They are test fixtures, not a new image build. The v91 KMS, kernel-entry and
  speech-entry inputs match their direct sources.[11] [12] [13]
  Its memtest and package-list inputs match as well.[14] [15]
  The corresponding v92 KMS, kernel-entry and speech-entry checks match.
  [16] [17] [18]
  Its memtest and package-list inputs also match.[19] [20]
- Branding: existing local provenance records describe transformations of the
  supplied Wilsof assets. These records are not independent ownership evidence.

The pinned Dux tree was additionally compared by metadata. Its sole exact
intersection with the reference trees was a zero-byte test fixture with Git's
canonical empty-blob identifier. An empty file is not code content and does not
establish a copying direction. No reference-distribution name appeared in its
pinned tree paths. This is not a full transitive dependency-source audit.

See the retained [Dux notices](../assets/notices/dux-shell-2.0.0/PROVENANCE.json),
[Hypridle provenance](../packaging/hypridle/provenance.json),
[portal provenance](../packaging/xdg-desktop-portal-hyprland/provenance.json) and
[Archiso fixture provenance](../tests/fixtures/archiso-provenance.json).

## Exact RC4 compositor binding

A read-only follow-up on November 14, 2026 closed the component-level
package-to-image gap. The earlier search of 109 retained JSON receipts was
inconclusive; it was not evidence that the underlying inputs were missing.
The follow-up read selected members directly from the original accepted ISO:

1. The full ISO SHA-256 matched the accepted RC4 identity in
   [Getting started](getting-started.md). Its descriptor-bound identity, size,
   ownership, mode and modification/change timestamps were unchanged throughout.
2. The embedded private-package manifest matched its marker digest and the
   retained native-build package/executable identities. The actual embedded
   package archive hash matched the independently rehashed retained archive.
3. The archive's package name, version and architecture matched the manifest.
   Its actual compositor executable and the live rootfs `/usr/bin/Hyprland`
   matched the same retained binary digest. The archive's embedded local patch
   matched the original patch digest as well.
4. The retained source archive, patch and build recipe were rehashed against
   their custody record, reusing the earlier direct-upstream tree comparison.
   The image's runtime source marker still named the accepted RC4 source commit.

Inspection used a read-only regular-file descriptor, the ISO-recorded SquashFS
byte offset and selected standard-tool stdout. It created no mount, extracted
rootfs, package copy on disk, guest, package transaction or new ISO. Private
package pins, custody locators and patch contents remain outside this document.

This binds the retained build records and compositor bytes to the exact live
image. It is not an independently reproduced build, an originality certificate,
a fresh installed-target test or professional security approval. Broader source
and licensing coverage remains open below; the existing virtual results are
unchanged and no physical PASS is inferred.

## Open evidence gaps

1. **Initial originality.** The recovered generation records strengthen the
   initial-file provenance, but do not certify that no adapted fragment or other
   unrecorded input influenced the code. The prototype has no independent full
   historical-payload byte comparison in this review. Do not turn generation
   records into an absolute authorship certificate.
2. **Transitive inputs and licensing.** Commit/pin/notice checks are not a review
   of every dependency's source history or a complete redistribution assessment.
   No project-wide license file is present in the reviewed tree. Do not invent a
   blanket license grant or treat upstream notices as licensing Wilsof's own code.

No confirmed prohibited copy was established by this review. The open gaps mean
that **complete independence is not certified**. Do not erase references or
rename files merely to obtain a clean keyword scan. Any confirmed prohibited
implementation must be excluded from future builds and independently replaced,
with normal tests and fresh exact-image acceptance where runtime inputs change.
The ISO currently under physical evaluation is not modified by this review.

## Continuing rule

Record a direct source URL and immutable revision for imported upstream material,
its local modifications and applicable notices. Preserve original attribution.
Treat unknown provenance as unresolved, not as approval. Functional tests, AI
review and absence of search hits cannot substitute for origin evidence.

## Sources

- [1] Hash-only reference tree observed_default
- [2] Hash-only reference tree at_Wilsof_initial_commit
- [3] duxlabs-dev/dux-shell pinned source
- [4] hyprwm/hypridle pinned source
- [5] hyprwm/xdg-desktop-portal-hyprland pinned source
- [6] hyprwm/xdg-desktop-portal-hyprland pinned source
- [7] Exact upstream notice LICENSE
- [8] Exact upstream notice ipp-Apache-2.0.txt
- [9] Exact upstream notice plasma-GPL-2.0.txt
- [10] Exact upstream notice vsix-MIT.txt
- [11] Tagged Archiso fixture
- [12] Tagged Archiso fixture
- [13] Tagged Archiso fixture
- [14] Tagged Archiso fixture
- [15] Tagged Archiso fixture
- [16] Tagged Archiso fixture
- [17] Tagged Archiso fixture
- [18] Tagged Archiso fixture
- [19] Tagged Archiso fixture
- [20] Tagged Archiso fixture
- [21] Exact shared-QML notice
- [22] Retained compositor direct upstream source

[1]: https://github.com/omacom/omarchy/tree/d81c2e28b84b70175155bddbd742bd2a21bcb999
[2]: https://github.com/omacom/omarchy/tree/84cfb93959f4fe0bbb71de71593b36647d2ba78d
[3]: https://github.com/duxlabs-dev/dux-shell/commit/9b413296b16721f7679fb62e624cb1ed2433fa58
[4]: https://github.com/hyprwm/hypridle/commit/e5c01af0842bd66617f7004568df9406111d6e80
[5]: https://github.com/hyprwm/xdg-desktop-portal-hyprland/commit/cc8e5ef8fb2acef3db488b9a33b0c48c2a4ee204
[6]: https://github.com/hyprwm/xdg-desktop-portal-hyprland/commit/0121b2e3f85c7ebf6280173f1054f7e5606262d1
[7]: https://github.com/duxlabs-dev/dux-shell/blob/9b413296b16721f7679fb62e624cb1ed2433fa58/LICENSE
[8]: https://github.com/duxlabs-dev/dux-shell/blob/9b413296b16721f7679fb62e624cb1ed2433fa58/core/pkg/ipp/LICENSE
[9]: https://github.com/duxlabs-dev/dux-shell/blob/9b413296b16721f7679fb62e624cb1ed2433fa58/quickshell/assets/sounds/plasma/LICENSE
[10]: https://github.com/duxlabs-dev/dux-shell/blob/9b413296b16721f7679fb62e624cb1ed2433fa58/quickshell/matugen/vsix-build/LICENSE
[11]: https://raw.githubusercontent.com/archlinux/archiso/v91/configs/releng/airootfs/etc/mkinitcpio.conf.d/archiso.conf
[12]: https://raw.githubusercontent.com/archlinux/archiso/v91/configs/releng/efiboot/loader/entries/01-archiso-linux.conf
[13]: https://raw.githubusercontent.com/archlinux/archiso/v91/configs/releng/efiboot/loader/entries/02-archiso-speech-linux.conf
[14]: https://raw.githubusercontent.com/archlinux/archiso/v91/configs/releng/efiboot/loader/entries/03-archiso-memtest86+x64.conf
[15]: https://raw.githubusercontent.com/archlinux/archiso/v91/configs/releng/packages.x86_64
[16]: https://raw.githubusercontent.com/archlinux/archiso/v92/configs/releng/airootfs/etc/mkinitcpio.conf.d/archiso.conf
[17]: https://raw.githubusercontent.com/archlinux/archiso/v92/configs/releng/efiboot/loader/entries/01-archiso-linux.conf
[18]: https://raw.githubusercontent.com/archlinux/archiso/v92/configs/releng/efiboot/loader/entries/02-archiso-speech-linux.conf
[19]: https://raw.githubusercontent.com/archlinux/archiso/v92/configs/releng/efiboot/loader/entries/03-archiso-memtest86+x64.conf
[20]: https://raw.githubusercontent.com/archlinux/archiso/v92/configs/releng/packages.x86_64
[21]: https://github.com/duxlabs-dev/dux-qml-common/blob/ebf5e6c002da1bdaa4aaa2f319fea7b8507abc42/LICENSE
[22]: https://github.com/hyprwm/Hyprland/commit/0aa6745f705f2c4b0a5004eb019ef76e5bbdb426
