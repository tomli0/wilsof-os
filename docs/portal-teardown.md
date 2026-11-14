# Portal logout correction — native backport, not ISO acceptance

The frozen Private3 package is xdg-desktop-portal-hyprland 1.4.1-2 with
Wayland 1.26.0-1. Ordinary logout reproduced SIGSEGV on a new copy-on-write
installed guest on 9 November 2026 at 23:00:56 UTC. Historical disks and the
Private3 ISO were not modified.

## Proven cause and scoped correction

GDB, using the matching Wayland build's debug information, identifies the
faulting proxy as `zxdg_output_v1`. Its display object's client map has
`data = 0x4`; destruction occurs in libc's normal exit handlers after the
portal's explicit `wl_display_disconnect`. The tagged 1.4.1 source retains
output proxies until global manager destruction after that disconnect.
This is an upstream resource-lifetime defect, not evidence of an ABI mismatch
or a Dux-caused compositor crash.

The supported correction is upstream commit
`0121b2e3f85c7ebf6280173f1054f7e5606262d1`, merged through upstream PR 443.
It applies without fuzz to tag v1.4.1 at
`cc8e5ef8fb2acef3db488b9a33b0c48c2a4ee204`. It releases proxy owners before
disconnecting and clears the display pointer. No package snapshot upgrade,
exit-status override, coredump suppression or disabled portal was used.

## Executed gates

- The original packaged binary reproduces SIGSEGV at ordinary user logout.
- A socketpair reproduction using the actual generated protocol wrappers and
  manager fails with SIGSEGV before the correction and exits 0 afterwards.
- Complete native CMake build passes on the frozen dependency environment.
- The committed makepkg entry point builds a complete package, runs 20 real
  teardown iterations, and includes the upstream BSD-3-Clause license.
- Five normal password login / functioning screenshot-backend / ordinary menu
  logout cycles pass with the development ELF. All portal exits are success,
  with no new portal core. A fresh password login follows the fifth logout.
- A further five cycles pass with the actual stripped ELF extracted from the
  package, not merely the earlier development ELF. Each cycle produces a real
  PNG through the portal's D-Bus Screenshot backend and verifies its bytes.
- The development-ELF session passes native wrong-password rejection, correct
  PAM unlock and keyboard menu recovery in the same Dux process, NRestarts=0.
- Dux, GTK portal and Hypridle still report nonzero exits when the compositor
  disappears; the portal fix does not conceal or claim to fix those separate
  lifecycle results. Fresh sessions are operational. These results are not a
  clean-all-services teardown claim.

Detailed private evidence group: `wilsof-stabilization-20261109T2232Z`.
Native package SHA256:
`d3d2dba441324ed467574ea27f5d2432f7f10cf851e1cc46aaf73bed2d8e7fd0`.
Extracted portal ELF SHA256:
`03ee10c6df912184461f5c516bd54a5b81e111804b9c41aaaf25387c40d3393f`.

## Rebuild and trust boundary

Generate `upstream-pristine.tar` in the packaging directory with:

    git archive --format=tar --prefix=portal/ cc8e5ef8fb2acef3db488b9a33b0c48c2a4ee204 > upstream-pristine.tar

Run `makepkg` in that directory on the coherent frozen build environment.
All source and patch inputs are checksum-pinned. Build warnings and initial
makepkg input-path failures remain preserved; the final entry point succeeds.

The test package is unsigned. It was not installed through pacman or represented
as trusted. Runtime testing used a disclosed systemd user-unit ExecStart override
to its extracted ELF in the disposable guest; package database identity remains
1.4.1-2. Signature trust and independent image/fresh-target integration must be
completed before a new candidate build. Source commit
`91606297fc8a1a7a61c6271f734872bc47920271` now carries the independently pinned
archive plus mandatory detached signature into both consumers, preserves the
existing trusted-signature policy, and checks installed package/ELF identity.
Synthetic transaction tests and a bounded separate AI source assessment pass;
the retained real archive fails preflight because its signature is absent.
Valid/untrusted production signature acceptance through the real consumers is NOT RUN.
The subsequent [owner-controlled signing gate](package-signing.md) additionally
requires an external approved primary-fingerprint pin and real GnuPG verification
before pacman. Its isolated test-only keys and native synthetic libalpm package
controls do not approve an identity or accept this retained real portal package.
Never disable signature verification to consume this development artifact.

The immutable Private3 ISO remains byte-identical and still contains the crash.
There is no new ISO or final virtual acceptance. A new privileged ISO build needs
separate owner approval after the remaining installer, trust and notice gates.
