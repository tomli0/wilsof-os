# README imagery

The desktop, launcher, terminal, and settings images are authentic **1280 × 800**
QEMU framebuffer captures from a separate, diskless Live boot of Wilsof RC4.
The ISO was attached read-only; the accepted installation disk and QA artifacts
were not attached. Opening settings did not change any values.

- Image version: `2026.11.13-rc4-recovery-test-only`
- Image source commit: `5699844ebb805a0553e991ac6e6e5506ee6de122`
- ISO SHA-256:

  ```text
  9b89565570b05dff6ccb5b15a40784e0829eca1c18531e8cba388ecda2443fcf
  ```

All four screenshots are lossless WebP conversions of the original PNG captures.
Their decoded RGB pixels are identical: no cropping, retouching, replaced text,
fabricated interface, or added window chrome. The terminal runs Fastfetch with
only software modules; its generic `live` account belongs to the test image, not
to private infrastructure. The settings capture shows the existing appearance
page, not a new settings implementation.

`header.png` is presentation artwork derived from the repository's supplied
Wilsof wordmark, using charcoal `#14181E` and ice blue `#86B9CE`. It is not a
screenshot and does not alter the desktop or the original branding assets.

These images illustrate the product. They are not additional acceptance tests,
proof of physical compatibility, or production approval. Wilsof remains **TEST
ONLY**.
