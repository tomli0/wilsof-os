# VM-runbook — Arch testmål

Dette dokumentet gjelder bare autorisert, dedikert Wilsof-infrastruktur. VM 112/Fedora endres ikke.

## Trygg tilgang

1. Bekreft target-OS, VM-navn og installert disk via lesekontroller.
2. Sammenlign presentert ED25519-nøkkel mot registrert fingeravtrykk før den pins; bruk `StrictHostKeyChecking=yes` etterpå.
3. Ta snapshot før skrivebordsarbeid når plattformen tilbyr det. Ikke reinstaller, formater eller endre VM-maskinvare som del av konfigurasjonstesting.

## Installere Wilsof-brukerprofil

1. Kontroller DMS, Hyprland, Hyprlock, Hypridle, portal og brukerens systemd-/D-Bus-sesjon med `scripts/preflight-arch.sh`.
2. Kjør DMS sin headless setup som målbruker hvis `~/.config/hypr/hyprland.lua` mangler.
3. Kopier prosjektet til VM-en og kjør:

       WILSOF_TARGET_VM=1 /opt/wilsof-os/scripts/install-user-config.sh

4. Installererens eneste DMS-Lua-endring er én markert `require("wilsof")`. Den må finnes én gang og stå etter `require("dms.binds-user")`.
5. Start/reload bare avgrensede komponenter under aktiv sesjon: `hyprctl reload`, `systemctl --user restart dms.service`, `systemctl --user restart hypridle.service`, og start `wilsof-session.target`. Ikke logg ut/reboot mens arbeid pågår.

## Valgfri VM-test for Super-fangende klienter

På klienter som Omarchy der Super blir fanget før Proxmox-konsollen, aktiver alternativene fra en grafisk Wilsof-terminal:

    wilsof-vm-test-binds enable

Test `Ctrl+Alt+Space`, `Ctrl+Alt+L`, `Ctrl+Alt+I` og `Ctrl+Alt+F1` fysisk gjennom klienten. Dette er et testlag og endrer ikke Wilsof-standardbindingene. Slå det av med:

    wilsof-vm-test-binds disable

Begge kommandoer reloader Hyprland når de kjøres i den grafiske sesjonen.

## Tilbakestilling

- Konfigurasjonsbackup ligger under `~/.local/state/wilsof-os/backups/`.
- For å velge nye personlige DMS-verdier, bruk DMS Settings. Reinstallasjon av Wilsof overskriver ikke eksisterende `settings.json` etter førsteinstallasjon.
- For eksplisitt Wilsof-reset: sikkerhetskopier `~/.config/DankMaterialShell/settings.json`, slett `~/.local/state/wilsof-os/dms-defaults-v1` og ønsket settings-fil, og kjør installasjonsskriptet på nytt.
- Ved skrivebordsfeil: velg lokal fallback-sesjon ved greetd/tuigreet, gjenopprett backupen og kontroller `journalctl --user -u dms -b` samt Hyprland-loggen før nye endringer.

## Boot-recovery (uten formatering)

1. Start et autorisert recovery-miljø, monter ESP på `/boot` og Btrfs `@`/`@home` på riktige steder.
2. Kontroller `/boot/loader/entries/arch.conf`, kernel/initramfs, root UUID og `rootflags=subvol=@`.
3. Kjør `bootctl --esp-path=/boot install` og kontroller både NVRAM-entry og `EFI/BOOT/BOOTX64.EFI`.
4. Ikke påstå full reboot-PASS før én faktisk kontrollert reboot er observert.

## Bevis

Ta faktiske skjermbilder av tomt skrivebord, Spotlight og innstillinger. Skill IPC/bind-last fra fysisk Proxmox-tastetrykk og fra visuelt bevis. Fyll `docs/testplan.md` med PASS/FAIL/IKKE TESTET.