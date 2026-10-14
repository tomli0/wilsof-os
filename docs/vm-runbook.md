# VM-runbook (utføres bare på autorisert isolert infrastruktur)

## Forhåndskontroll

1. Kartlegg vertens ledige CPU, RAM og datastore. Ikke endre eksisterende VM-er, nettverk eller lagring.
2. Opprett en ny dedikert VM kun dersom kapasiteten dekker den. Start med 4 vCPU, 6 GiB RAM og 40 GiB virtuell disk; reduser etter målt kapasitet, ikke overalloker.
3. Bruk en offisiell aktuell Fedora Workstation ISO med kontrollert checksum. Ingen fysisk disk-passthrough.

## Desktop-spike

1. Installer Fedora i VM, oppdater innen VM-en og behold SELinux enforcing.
2. Kontroller offisielle pakkekilder/versjoner og DMS-lisens før installasjon. Dokumenter eksakte NEVRA-er og repoer.
3. Installer Hyprland, XDG-desktop-portaler, PipeWire/WirePlumber, polkit-agent og standardprogrammene. Installer DMS etter dens aktuelle Fedora-instruks.
4. Kjør `dms setup` bare på den nye testbrukeren. Kopier deretter `config/hypr/wilsof.conf` som bevisst overstyring, uten å la to paneler eller to launchere autostarte.
5. Installer `wilsof-session.target` og `wilsof-wallpaper.service` som user units; plasser godkjente assets i `/usr/share/wilsof-os/assets/`.
6. Implementer og test `wilsof-search` som DMS-utvidelse mot en eksplisitt provider-tabell. Først etter at provider-API-er er verifisert i den aktuelle DMS-versjonen.

## Bevis

Test fra grafisk konsoll, ikke SSH alene. Logg versjoner, `systemctl --user --failed`, portalstatus, `getenforce`, oppstartstid og RAM/CPU. Ta faktiske skjermbilder av tomt skrivebord, samlet søk og innstillinger. Fyll testplanen med PASS/FAIL/IKKE TESTET.
