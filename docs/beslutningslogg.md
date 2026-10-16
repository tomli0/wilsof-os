# Decisions

## D-001 — Arch is the active prototype platform

Status: accepted. Arch VM 113 is the active test target. Fedora material is retained only as historical reference and is not the active installation path.

## D-002 — Keep DMS; Wilsof is an override layer

Status: accepted. DMS owns the shell, supported IPC and generated configuration. Wilsof loads separately after DMS so regeneration does not erase project changes.

## D-003 — Use a fixed Wilsof palette

Status: accepted. Charcoal `#14181E` and ice-blue `#86B9CE` are fixed Wilsof values. Matugen is disabled for DMS, the custom theme is a first-install default, and later personal DMS choices are preserved.

## D-004 — One application-first launcher entry

Status: accepted with scope limit. `Super+Space` opens DMS Launcher in application mode. This gives a predictable program list and avoids unrelated provider matches. Files, windows, settings aliases and power actions are not claimed as launcher features until a supported path has been tested.

## D-005 — Local help is a DMS Notepad page

Status: accepted. Ghostty command-mode startup in the active Arch session produced `PostForkError` and a broken terminal. Wilsof now renders its shared shortcut manifest locally and opens it with supported DMS Notepad IPC. This retains an offline, visible help route without creating another shell component.

## D-006 — ESP is `/boot`, not XBOOTLDR

Status: accepted. Install systemd-boot with `--esp-path=/boot` and verify the fallback file explicitly.

## D-007 — Hyprlock owns authentication; Wilsof owns presentation

Status: accepted. Wilsof supplies the lock surface and calls Hyprlock through an idempotent wrapper. PAM remains system-owned, and the agent does not handle account passwords.
