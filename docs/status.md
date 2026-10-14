# Status — Wilsof OS første prototype

Oppdatert: 2026-10-14 UTC

## Faktisk implementert

- Godkjente WS-assets ligger i `assets/`; bakgrunn 1672×941, mockup 1672×941 og logo 2172×724 RGBA.
- `config/hypr/wilsof.conf` definerer tomt skrivebord uten dock/ikoner, godkjente visuelle verdier og alle arbeidsområdebindinger `Super+1…9` / `Super+Shift+1…9`.
- `bin/wilsof-search` er en minimal og testet bro: bare `wilsof-search toggle` godtas og den kaller den dokumenterte DMS-kommandoen `dms ipc call spotlight toggle`. Den har ikke egen gruppering, filindeks, vindussøk eller systemhandlinger.
- `scripts/preflight-fedora.sh` er en read-only kontroll som avviser ikke-Fedora og kontrollerer kommandoer, user-systemd og SELinux.
- `scripts/install-user-config.sh` krever eksplisitt `WILSOF_TARGET_VM=1`, kjører preflight og installerer bare i den valgte brukerens hjemmekatalog på test-VM-en. Den endrer ikke Hermes-VM og ber brukeren legge til én `source`-linje selv for å unngå å endre eller duplisere aktiv Hyprland-konfigurasjon.
- Systemd-enheten bruker sitert bakgrunnsfil med mellomrom og `ExecCondition` for DMS. DMS er en hard avhengighet; den starter ikke wallpaper dersom `dms` mangler.

## Testresultater

| Kontroll | Status | Evidens |
|---|---|---|
| Python-tester for konfigurasjon, assets, wrapper og sikkerhetsvakt | PASS | `pytest -q`: 10 passed (2026-10-14) |
| Shell-syntaks | PASS | `sh -n bin/wilsof-search scripts/preflight-fedora.sh scripts/install-user-config.sh` |
| Wrapper mot DMS-argumenter | PASS | Test med falsk `dms`; eksakt kall `ipc call spotlight toggle` |
| Preflight på Hermes-VM | PASS (for avvisning) | Avviser korrekt ikke-Fedora uten endringer |
| Systemd-parser med målplattformens enheter | IKKE TESTET | Lokal vert mangler både `dms` og `graphical-session.target` |
| DMS/Hyprland/portal/SELinux GUI | IKKE TESTET | Ingen autorisert dedikert VM |
| Låseskjerm/autentisering | IKKE TESTET | `loginctl lock-session` er binding, ikke bevis på locker |
| Reboot/shutdown/logout-bekreftelse | IKKE TESTET | Krever Wilsof/DMS-provider eller egen godkjent utvidelse |

## Pakkekilder og versjoner

- Fedora Workstation 44 er aktuell offisiell nedlasting ved kontroll. ISO skal hentes fra https://fedoraproject.org/workstation/download/ og verifiseres med Fedora-prosjektets publiserte SHA-256 og OpenPGP-instruks derfra før VM-opprettelse.
- DMS-dokumentasjonen angir COPR-pakker for Fedora 43/44 og kommandoen `sudo dnf install dms`: https://danklinux.com/docs/dankmaterialshell/installation
- Hyprland-versjon, DMS-versjon, COPR-navn, portals og alle RPM/Flatpak-versjoner er IKKE LÅST før de leses fra den faktiske Fedora-VM-en. De skal registreres med `rpm -qa`, `dnf repolist --enabled` og `flatpak remotes --show-details`.

## Blokkeringer og neste handling

Lesekontroll lokalt fant ikke `qm`, `pvesh`, `virsh` eller `/dev/kvm`. Forsøk på den ene dokumenterte SSH-verten `hermes-vm` stoppet ved host-key-verifisering; ingen nøkkel ble akseptert eller endret. Det finnes dermed ingen bekreftet legitim Proxmox-tilgang i denne sesjonen.

Nødvendig brukerinput: gi navnet/IP-en og SSH-host-key/tilgangsvei til en autorisert Proxmox-vert, eller opprett en isolert Fedora Workstation 44 test-VM. Bruk UEFI, q35, 4 vCPU, 6 GiB RAM (reduser ved dokumentert mangel), 40 GiB qcow2 virtio-disk, virtio-nett på privat/NAT-segment og standard virtio-grafikk/SPICE eller annen godkjent grafisk konsoll. Ikke bruk passthrough. Installer med standard diskvalg i VM-en; opprett separat testbruker og SSH-tilgang fra Hermes-VM. Deretter: kopier repoet, kjør `WILSOF_TARGET_VM=1 ./scripts/install-user-config.sh`, følg DMS sin dokumenterte Fedora-repoinstruks, og test grafisk.
