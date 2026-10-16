# Avvik og begrensninger

## Avsluttede avvik

- Standard lilla DMS og standardbakgrunn: årsak var at Wilsof-session.target aldri ble startet av den faktiske DMS-genererte Lua-entrypointen. I tillegg manglet fast custom-theme. Rettet og visuelt kontrollert på VM 113.
- Genererte DMS-binds dupliserte Wilsof-binds. Rettet med dokumentert, case-sensitiv `hl.unbind` før Wilsof-bindene registreres; kontrollert via Hyprland IPC.
- Hypridle fant ikke `wilsof-lock` fordi user-tjenestens PATH ikke inneholder `~/.local/bin`. Rettet med `$HOME/.local/bin/wilsof-lock`; den avvikende DPMS-regelen ble fjernet fordi Hyprland 0.56.2 avviste den gamle dispatch-syntaksen.

## Gjenstående avvik

- SSH til VM 113 har korrekt pinnet ED25519-fingeravtrykk (`SHA256:0IOuFZDTGymRZzoa5kSAO1x8FCo+ZO1khL3q/xqNAqw`), men `wilsofdev@192.168.10.250` avviser tilgjengelig ED25519-nøkkel med `Permission denied (publickey)`. Ingen hostnøkkel er endret eller akseptert på nytt. Dette blokkerer utplassering, aktiv sesjonsinspeksjon, IPC/syntetisk input, skjermbilder og reboot/låsetest i denne økten.

- Spotlight har visuelt verifiserte programtreff og Files-filter, men ikke full akseptanse for vinduer, systemhandlinger med bekreftelse, aliaser eller privat filindeks. Disse skal ikke markedsføres som fullført.
- PipeWire har RTKit-varsel fordi RTKit ikke er tilgjengelig. Dette er ikke tolket som lydfeil; avspilling er ikke testet.
- DMS viser enkelte statusikoner fra tilgjengelige komponenter; den planlagte bar-konfigurasjonen fjerner vær og ressursmålere.
- Hyprlock/PAM, fysisk tastatur via Proxmox, logout/login og reboot-persistens krever manuell kontroll.

## Bootfeil

Nåværende disk er korrekt: EFI System-partisjon på `/dev/sda1`, ESP på `/boot`, systemd-boot NVRAM-entry og fallback `EFI/BOOT/BOOTX64.EFI`, samt korrekt Btrfs root-UUID/subvolum. Tidligere oppstartslogg fra den mislykkede første diskstarten er ikke bevart, så den eksakte årsaken kan ikke fastslås uten spekulasjon. Installasjonsoppskriften er korrigert for den observerte ESP/XBOOTLDR-forvirringen og verifiserer alle boot-artefakter statisk.
