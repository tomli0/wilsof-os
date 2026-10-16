# Avvik og begrensninger

## Avsluttede avvik

- Standard lilla DMS og standardbakgrunn: årsak var at Wilsof-session.target aldri ble startet av den faktiske DMS-genererte Lua-entrypointen. I tillegg manglet fast custom-theme. Rettet og visuelt kontrollert på VM 113.
- Genererte DMS-binds dupliserte Wilsof-binds. Rettet med dokumentert, case-sensitiv `hl.unbind` før Wilsof-bindene registreres; kontrollert via Hyprland IPC.
- Hypridle fant ikke `wilsof-lock` fordi user-tjenestens PATH ikke inneholder `~/.local/bin`. Rettet med `$HOME/.local/bin/wilsof-lock`; den avvikende DPMS-regelen ble fjernet fordi Hyprland 0.56.2 avviste den gamle dispatch-syntaksen.

## Gjenstående avvik

- SSH-tilgang er gjenopprettet og utplassering er gjennomført. Årsaken var manglende `/home/wilsofdev/.ssh/authorized_keys`, ikke feil hostnøkkel eller låst konto. Tilgangen er gjenopprettet med kun den eksisterende offentlige nøkkelen; passordinnlogging og sudo-policy er ikke endret.
- DMS Launcher i Apps-modus er Wilsofs felles programinngang. DMS viser fortsatt engelske kategori-/metadata-tekster og mangler norsk placeholder. Prosjektet gjør ingen stor DMS-fork bare for oversettelse. Filer, vinduer og systemhandlinger blir ikke lovet som launcherfunksjoner.
- DMS-systemmenyen har hold-bekreftelse på 500 ms, men det er ikke gjennomført fysisk tastaturtest av avbrytelse med Esc eller hver destruktive dialog.
- Ghostty-hjelpens aktive GUI-vindu er ikke godkjent: en SSH-syntetisk start ga Ghostty `PostForkError`. Renderer, manifest og kommandoform er testet lokalt; reell Hyprland-tastaturvei må testes i VM-konsollen.
- PipeWire har RTKit-varsel fordi RTKit ikke er tilgjengelig. Dette er ikke tolket som lydfeil; avspilling er ikke testet.
- Hyprlock/PAM, fysisk tastatur via Proxmox, logout/login og reboot-persistens krever manuell kontroll.

## Bootfeil

Nåværende disk er korrekt: EFI System-partisjon på `/dev/sda1`, ESP på `/boot`, systemd-boot NVRAM-entry og fallback `EFI/BOOT/BOOTX64.EFI`, samt korrekt Btrfs root-UUID/subvolum. Tidligere oppstartslogg fra den mislykkede første diskstarten er ikke bevart, så den eksakte årsaken kan ikke fastslås uten spekulasjon. Installasjonsoppskriften er korrigert for den observerte ESP/XBOOTLDR-forvirringen og verifiserer alle boot-artefakter statisk.
