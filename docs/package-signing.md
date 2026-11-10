# Owner-controlled Wilsof package signing and trust

Status: no production signing identity has been approved. No production key is
created, imported, certified or trusted by this workflow automatically. The portal
archive remains unsigned. An approval JSON file is an input to a separately
reviewed build, not evidence that the owner approved an identity.

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
It never imports a key or falls back to the public portal on failure.

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
`VALIDSIG` alone is deliberately insufficient. Real approved-package installation,
new-image and physical acceptance remain separate pending gates.
