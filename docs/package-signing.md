# Owner-controlled Wilsof package signing and trust

Status: **no production signing identity has been approved**. RC4 used explicitly
isolated TEST ONLY signatures and passed its bounded native consumers/update/
recovery checks. The test identity is not a production signer and is not promoted
by these results. See [Getting started](getting-started.md) for exact image scope.

No production key is created, imported, certified or trusted automatically. An
approval JSON file is an input to a separately reviewed build, not evidence that
the owner actually approved an identity.

## Current release responsibilities

These are unresolved production gates, not tasks already completed:

- Name the release/security maintainer and backup contact; define advisory triage,
  release cadence and response expectations. No service-level promise is approved.
- Independently approve the production primary identity, key custodian, signing
  subkey policy, expiry/renewal, revocation channel and exact enrollment scope.
- Select and review one compatible complete future package closure, including
  compositor, shell, portals, kernel/headers and required external drivers.
- Approve and exercise production-signed image and fresh-target consumers. Existing
  TEST ONLY passes do not establish those production identities or policies.
- Define authenticated release/advisory delivery and how supported installations
  learn revocation/current release status. The helper has no automatic update
  feed or manifest-expiry service; forward-date and baseline checks are not a
  complete freshness, anti-rollback or incident-response system.
- Resolve [source-origin gaps](source-provenance.md#open-evidence-gaps), project
  licensing and binary-redistribution obligations before claiming a public release.

The existing controls verify exact pinned signatures, source/baseline/closure
identity and usable boot artifacts. They refuse missing trust, inconsistent
plans and incomplete recovery. They do not assign a maintainer, deliver future
security fixes, provide Secure Boot trust or implement atomic rollback.

No new signing infrastructure, production-key generation, enrollment, native transaction,
image build or physical change is performed by this review.

## Gate and custody

The retained backport is `xdg-desktop-portal-hyprland` version `1.4.1-2.1`,
architecture `x86_64`. Preserve the existing archive; do not rebuild it to sign it.
Its SHA256 is
`d3d2dba441324ed467574ea27f5d2432f7f10cf851e1cc46aaf73bed2d8e7fd0`;
its packaged executable SHA256 is
`03ee10c6df912184461f5c516bd54a5b81e111804b9c41aaaf25387c40d3393f`.
The source/patch/build provenance is in
[portal teardown](portal-teardown.md) and
[the pinned recipe](../packaging/xdg-desktop-portal-hyprland/provenance.json).
Detached signing does not change either archive or executable bytes.

The existing repository policy remains `Required TrustedOnly DatabaseOptional`
with the separately inherited `LocalFileSigLevel = Optional`. The local exception
is not sufficient to enforce signature presence. The portal consumer therefore
requires an adjacent signature and owner signer pin, verifies OpenPGP validity and
full trust against the target's already-enrolled pacman keyring, and only then
calls pacman under its unchanged policy. Neither check replaces the other.
The production consumer never imports a key or falls back to the public portal
on failure. The separately opted-in nonproduction path below can enroll only a
hash/fingerprint-bound public certificate in its isolated test root.

## Explicit isolated TEST ONLY candidates (not production approval)

An authorized disposable candidate may use a dedicated test signer while
production identity approval remains pending. This is a separate schema and
mode, **never** an automatically generated `owner-approved` record. It does not
authorize production enrollment, a build, or installation on an owner disk.

Keep signing secrets outside the exported source/profile/image. Detached-sign
the existing portal, pinned Hypridle and private compositor archives without
changing their bytes; all existing package/ELF pins remain enforced. Supply:

- Portal archive plus its bounded binary `.sig`.
- Adjacent `<portal-package>.test-only.asc`: ASCII-armored **public** certificate.
- Adjacent `<portal-package>.test-only.json`, with exactly these fields:

      {
        "schema": 1,
        "mode": "test-only",
        "production_trust": "pending",
        "build_version": "candidate-test-only",
        "package_sha256": "d3d2dba441324ed467574ea27f5d2432f7f10cf851e1cc46aaf73bed2d8e7fd0",
        "primary_fingerprint": "<40 uppercase hex characters; intentionally invalid placeholder>",
        "certificate_sha256": "<64 lowercase hex characters; intentionally invalid placeholder>"
      }

- Hypridle and private compositor archives each retain an adjacent `.sig` through
  both image and fresh-target staging. Missing signatures in test mode fail closed.
  The independent private-compositor opt-in/contract is still required.

Set **both** `WILSOF_PORTAL_TEST_ONLY=1` and
`WILSOF_ISO_VERSION=candidate-test-only` on the normal authorized build wrapper.
The version must match the manifest exactly and end in `-test-only`. The opt-in
is independent of the compositor experiment. Other opt-in values, production
versions, mixed approval/test inputs, missing manifests/markers, certificate hash
or primary-fingerprint mismatches are refusals, not production fallbacks.
The equivalent materializer parameters are `--portal-test-only --build-version
candidate-test-only` in addition to its normal inputs; they do not start a build.

The materializer persists the public certificate, manifest and separate
`/usr/share/wilsof/portal-test-only.json` candidate marker. It pins the ISO name
to `wilsof-test-only`, its version to the manifest, sets root-owned public-input
permissions and labels the installer launcher, `/etc/issue` and `/etc/motd`
**TEST ONLY — production signing trust pending**. Fresh installed targets inherit
the marker/certificate and console warnings, not production approval.

Before **any** of these three private-package installations, image customization
and fresh-target provisioning call `prepare_test_trust`. This validates the
unchanged repository policy and complete portal input, then uses only
`target_command` to run target-local `pacman-key --gpgdir /etc/pacman.d/gnupg`
with `--init`, `--populate archlinux`, `--add` the persisted certificate and
`--lsign-key` the exact primary fingerprint. Official Arch trust and all signature
policy settings remain unchanged. Portal installation still requires the same
fully trusted GnuPG status, pinned primary and libalpm verification as production.

A fresh target must be mounted and canonical. Native `/` operation requires the
matching prebuilt root-owned, non-group/world-writable marker **at the built-in
path** and uses only that root's persisted inputs, never an external staging
folder. These checks bound a cooperating isolated build/live workflow; a marker
is not proof of namespace isolation against hostile root. The authenticated
builder must still establish isolation. Host keyrings are never enrollment targets.

At the end of test image customization, `seal_test_image` stops only the image
pacman GPG agent and removes its generated local master secret/revocation files;
public trust and the candidate certificate persist. No signer secret is ever
staged. The live overlay and fresh target independently initialize their own
local pacman master when enrolling. This sealing hook is image-only, not an
installed-system/update cleanup operation.

`tests/test_portal_test_only.py` exercises real validation, staging, materializer,
wrapper and fresh-target entrypoint logic with synthetic inputs and substituted
native archive/GPG/chroot/package boundaries. It generates no keys and establishes
orchestration/refusal behavior, not native cryptographic or ISO acceptance.

## One owner decision

Approve one primary OpenPGP fingerprint, its independently authenticated public
key and private-key custodian, and the narrow scope: sign this exact portal
archive; enroll that public identity only in isolated candidate/live/fresh-target
pacman keyrings. This does not authorize host trust changes, signing other inputs,
Secure Boot enrollment, an ISO build or physical installation.

If an existing identity is proposed, verify its full primary fingerprint directly
with its established custodian through an independent authenticated channel.
A matching UID, keyserver search result, short key ID, package signature or
self-authored approval file is not that verification.

If no suitable identity exists, the owner establishes a dedicated one on their
trusted signing workstation, not in the builder, source tree or image. Recommended
custody is an offline certification primary and a separately protected signing
subkey or hardware token. Protect it with owner-entered authentication and an
independent encrypted backup. Generate and store its revocation certificate
separately. Do not send private keys, passphrases or recovery material to an agent.
Record algorithm, expiry, primary and signing fingerprints and intended scope.
Only after independent fingerprint verification can the owner approve it.

## Signing and consumer sequence after approval

1. On the owner-controlled signer, verify the retained archive hash and metadata
   against the identities above. Use GnuPG detached binary signing, SHA256 or
   stronger, selecting the exact approved signing subkey explicitly. Sign the
   existing archive, not a re-compressed copy. Authentication stays in the owner's
   normal pinentry/token interface. Signing is repeatable; signature timestamps
   and randomized algorithms need not produce identical signature bytes.
2. Return the unchanged archive, adjacent `.sig`, authenticated public certificate,
   primary/subkey fingerprints and public-certificate SHA256. Record actual
   signature SHA256 separately. Publish no secret signing material.
3. The owner supplies `<exact-package-filename>.approval.json` adjacent to it:

       {
         "schema": 1,
         "approval": "owner-approved",
         "package_sha256": "d3d2dba441324ed467574ea27f5d2432f7f10cf851e1cc46aaf73bed2d8e7fd0",
         "primary_fingerprint": "<the owner's exact 40-character uppercase primary fingerprint>"
       }

   The placeholder is intentionally invalid. No usable approval is shipped in Git.
   Duplicate fields, short/lowercase/incorrect fingerprints, mismatched package
   hashes, links, unknown fields and non-approved state are refused.
4. A new reviewed authenticated handoff freezes source, package, signature,
   approval JSON and public-certificate hashes after the owner decision. It must
   compare them with that independent decision; never derive authority merely
   from the files themselves. Reuse no consumed old-image build helper.
5. In separately authorized disposable roots only, verify the public certificate's
   exact primary/subkey identities before explicit enrollment. Certify the
   approved identity using the root's own pacman trust model, preserving official
   Arch trust. Do not copy a signer's secret key or builder pacman master secret
   into the ISO. Fresh-target trust setup must independently establish the same
   public identity; a live keyring is not automatically target enrollment.
6. Run the actual live and fresh-target consumers as root inside their isolated
   environments. Both use the same `portal-package.py` install gate. GnuPG uses
   `/etc/pacman.d/gnupg`, no key auto-import/retrieval, the PGP validity model, one
   valid binary signature, the exact approved primary fingerprint and full/ultimate
   validity. A signing subkey is allowed only under that primary. Unknown,
   incorrect, expired/revoked or damaged signatures stop before pacman mutation.
   Pacman must independently accept the same package. Query installed version,
   executable package ownership and executable SHA256 afterwards.
7. Before ISO approval, prove modified-package, wrong-but-trusted signer,
   unknown/untrusted signer, missing/corrupt signature, changed approval and
   unprivileged-consumer refusals, plus five real authenticated portal cycles.
   Preserve journals and trust receipts. Offline fixture keys and substituted
   package commands do not satisfy production native acceptance.

## Rotation and revocation

Set an explicit expiry and renewal window. Freeze each release's approved primary,
allowed signing subkey, public certificate and package signature identities.
A signing-subkey rotation requires owner authentication of the updated certificate
and fresh consumer/rejection tests; a new primary needs a new independent approval.
Do not silently accept another already-trusted Arch or Wilsof signing identity.

On suspected compromise, stop new signing/build/update publication. Authenticate
and distribute the revocation through the owner's established channel; update the
isolated candidate and installed-system trust policy only through an approved
recovery/update action. Reject revoked/expired certificates and affected inputs,
retain forensic evidence, and re-sign reviewed bytes with a newly approved
identity. Existing offline media cannot learn a later revocation automatically:
recovery must use authenticated current revocation data and an independent digest
manifest. Package trust is not anti-rollback or automatic OS rollback.

## Executed test boundary

`tests/test_portal_trust.py` creates explicitly labelled one-day TEST ONLY keys in
fresh private temporary keyrings and removes them after stopping their agents.
Actual GnuPG checks cover valid signing subkeys, altered bytes, untrusted/unknown
keys, another trusted signer, missing/corrupt signatures and expiry. Consumer
orchestration also executes real GnuPG with only chroot/keyring location and pacman
boundaries substituted. Approval, privilege, refusal ordering and orphaned-state
controls are source tests. No fixture identity is installed in a production
keyring or used to sign the retained real portal archive.

The separate disposable native libalpm lab also installed a signed synthetic
package and rejected altered bytes, an untrusted signer, missing/corrupt signatures
and an unknown signer. Each refusal left its own target package database/payload
unchanged. The fixture explicitly required local-file signatures; this is stronger
than the retained production `LocalFileSigLevel = Optional`, not proof that the
production consumers passed. Its mapped-root namespace had no block nodes or
network, and the builder's actual database/configuration hashes were unchanged.
Test keys were deleted and no namespace mounts remained after exit.

GnuPG status interpretation follows the release-tagged
[2.4.9 status contract](https://github.com/gpg/gnupg/blob/gnupg-2.4.9/doc/DETAILS).
`VALIDSIG` alone is deliberately insufficient. Production-approved package/image
and physical acceptance remain separate gates; RC4's TEST ONLY native results do
not approve those production identities or policies.
