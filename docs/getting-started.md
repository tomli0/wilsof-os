# Getting started

Wilsof OS is **TEST ONLY**. RC4 has passed virtual acceptance, not physical or
production approval. Preserve your current operating system and data.

## The accepted test image

The virtual acceptance result applies only to this image:

- Version: `2026.11.13-rc4-recovery-test-only`
- Architecture: x86_64; boot mode: UEFI
- Image source commit: `5699844ebb805a0553e991ac6e6e5506ee6de122`
- Result: **66 PASS / 0 FAIL / 0 NOT RUN**

Filename:

```text
wilsof-test-only-2026.11.13-rc4-recovery-test-only-x86_64.iso
```

SHA-256:

```text
9b89565570b05dff6ccb5b15a40784e0829eca1c18531e8cba388ecda2443fcf
```

There is currently **no public ISO download**. Obtain the exact candidate through
an approved test-image handoff. A different image, rebuild, or later source commit
does not inherit RC4's acceptance. Documentation commits do not change its image
source identity.

## Evaluate the Live desktop

1. Use an isolated x86_64 UEFI VM. Do not pass through physical disks, USB storage,
   your home directory, or credentials.
2. Verify the image before booting:

   ```sh
   sha256sum wilsof-test-only-2026.11.13-rc4-recovery-test-only-x86_64.iso
   ```

   The digest must exactly match the value above.
3. Attach the ISO as read-only boot media. A diskless VM is sufficient to explore
   the desktop; no installation is needed for the screenshots' workflow.
4. Boot the normal Live entry and explore the desktop, menu, applications, and
   settings. Live-session changes are not a replacement for an installed system.

### Essential shortcuts

- `Super+Space` — open Wilsof Menu.
- `Super+Enter` — open Ghostty.
- `Super+B` — open Firefox.
- `Super+E` — open Files.
- `Super+I` — open the Configure category.
- `Super+1–9` — switch workspaces.
- `Super+Shift+1–9` — move a window to a workspace.
- `Super+Q` — close the active window.
- `Super+F1` — show shortcut help.

`Super` is normally the Windows or Command key. Host shortcuts may intercept keys
when the VM viewer has not captured the keyboard.

## Installation is for disposable virtual disks only

Installation erases the selected target. It is not a supported production setup,
a dual-boot guide, or authorization to replace an existing system.

Use a newly created, blank virtual disk and verify its identity and capacity.
Before selecting a target, inspect the actual installer interface in the Live
session:

```sh
sudo /usr/local/bin/wilsof-install --help
```

Follow its explicit target-selection and confirmation prompts. Do not substitute
an existing physical device for a virtual target. Existing-system replacement is
a separate, explicitly confirmed mode—not permission to bypass blank-disk checks.

Normal installation requires a separate disk-unlock passphrase and uses a
**LUKS2-encrypted ext4 root** with a separate **unencrypted FAT32 EFI System
Partition**. Root encryption does not authenticate the boot partition or establish
Secure Boot trust. After installation, detach the ISO and verify cold boot,
disk unlock, and normal user login in that same disposable VM.

## Before replacing an existing system

Virtual acceptance alone does not clear these remaining gates:

- Physical Live evaluation of graphics, input, connectivity, audio, and power.
- An independent full backup and a demonstrated restore and boot.
- Approved production signing/trust and a defined security-update responsibility.
- Separate approval for the exact image, physical target, and destructive install.

Until then, keep Omarchy or your current OS unchanged. Follow
[project status #16](https://github.com/tomli0/wilsof-os/issues/16) for the current
release decision and [the update/recovery design](update-transition.md) for the
maintenance model. Earlier engineering documents and screenshots may describe
older candidates; their results are not transferable to RC4.
