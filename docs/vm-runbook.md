# VM-runbook (utføres bare på autorisert isolert infrastruktur)

## Forhåndskontroll

1. Kartlegg vertens ledige CPU, RAM og datastore via lesekontroller. Ikke endre eksisterende VM-er, nettverk eller lagring.
2. Opprett en ny dedikert VM bare når tilgang og kapasitet er uttrykkelig dekket. Bruk UEFI, q35, 4 vCPU, 6 GiB RAM og 40 GiB qcow2/virtio-disk som utgangspunkt; reduser kun etter målt kapasitet. Ingen passthrough.
3. Last ned Fedora Workstation 44 fra https://fedoraproject.org/workstation/download/. Verifiser ISO mot den tilhørende, offisielle SHA-256- og OpenPGP-instruksen før den monteres.
4. Bruk privat/NAT-nett eller annen godkjent intern nettprofil, virtio-nett og virtio-grafikk/SPICE (eller autorisert grafisk konsoll). Ikke eksponer nye tjenester mot internett.

## Installasjon og tilgang

1. Installer bare på VM-ens 40 GiB virtuelle disk. Behold standard SELinux enforcing og opprett en vanlig testbruker.
2. Aktiver SSH bare på VM-ens godkjente interne nett og registrer vertsnøkkelen via normal administrasjonskanal. Fra Hermes-VM brukes `ssh testbruker@vm-ip`; ikke deaktiver host-key-kontroll som snarvei.
3. Ta snapshot før egne desktopendringer dersom plattformen støtter det.

## Desktop-spike

1. Oppdater Fedora i VM-en. Logg `cat /etc/os-release`, `rpm -qa`, `dnf repolist --enabled` og `getenforce`.
2. Kontroller DMS-lisens og den gjeldende Fedora/COPR-kilden i DMS-dokumentasjonen før installasjon. Installer DMS med dokumentert repo og `dnf install dms`; installer Hyprland fra dokumentert aktiv kilde, nødvendige XDG-portals, PipeWire/WirePlumber, polkit-agent og de syv standardprogrammene.
3. Kjør DMS sin aktuelle `dms setup` bare for testbrukeren. La DMS eie topplinje/varsler/lås; ikke start ekstra panel eller launcher.
4. Kopier repoet til VM-en. Kjør `WILSOF_TARGET_VM=1 ./scripts/install-user-config.sh`. Legg manuelt til `source = ~/.config/hypr/wilsof.conf` én gang i testbrukerens aktive Hyprland-konfigurasjon etter at DMS-oppsettet er inspisert.
5. Aktiver `wilsof-wallpaper.service` først etter at `dms --version`, brukerens D-Bus og user-systemd virker. Kontroller `systemctl --user --failed` før og etter.
6. `wilsof-search toggle` åpner foreløpig DMS Spotlight. Den oppfyller ikke ennå kravene om Wilsof-gruppering, aliaser eller systemhandlingsbekreftelse; ikke marker disse som levert.

## Bevis

Test fra grafisk konsoll, ikke SSH alene. Logg portals, lyd, `loginctl`, `systemctl --user`, oppstartstid og RAM/CPU. Ta faktiske skjermbilder av tomt skrivebord, Spotlight og en eksisterende innstillingsflate. Fyll testplanen med PASS/FAIL/IKKE TESTET.