# Testmatrise — Arch-prototype

Status er skilt mellom statisk kontroll, IPC og observert GUI. PASS betyr bare den angitte kontrollen.

| Område | Kontroll | Status | Evidens |
|---|---|---|---|
| Oppstart | Installert root, ikke live-ISO | PASS | `/` og `/home` på Btrfs `/dev/sda2`, ingen live/squashfs-mount |
| Oppstart | greetd, SSH, qemu-guest-agent, NetworkManager | PASS | alle aktive ved SSH-kontroll |
| Oppstart | EFI, systemd-boot, fallback og boot-entry | PASS | `bootctl status`: NVRAM-entry og `EFI/BOOT/BOOTX64.EFI`; `arch.conf` peker på korrekt UUID/subvolum |
| Konfigurasjon | Wilsof lastes én gang etter DMS | PASS | én `require("wilsof")` og aktiv Hyprland-bindliste |
| Konfigurasjon | DMS-binds uten Wilsof-duplikater | PASS | `hyprctl -j binds`: én forekomst av Super+Space/L/I, piler, 1, Q og F etter `hl.unbind` |
| Konfigurasjon | Norsk grafisk tastatur | PASS | `hyprctl getoption input:kb_layout` → `no` |
| Design | Godkjent bakgrunn, tom flate, palette og linje | PASS | visuelt inspisert `evidence/desktop-wilsof-clean.png` |
| Launcher | Spotlight åpnes via Wilsof-wrapper | PASS (IPC) | `wilsof-search toggle` → `SPOTLIGHT_TOGGLE_SUCCESS` |
| Launcher | Programtreff | PASS (GUI) | `evidence/launcher-firefox-query.png` viser Firefox |
| Launcher | Piltaster/Enter/Esc via fysisk tastatur | IKKE TESTET | ingen Proxmox-konsollinput-observasjon |
| Launcher | Vinduer, innstillinger, systemhandlinger, norsk/engelsk alias | IKKE TESTET | DMS-funksjonsomfang ikke verifisert ende-til-ende |
| Bindinger | Lastet og entydig | PASS | Hyprland IPC-bindliste etter reload |
| Bindinger | Fysisk tastetrykk observert | IKKE TESTET | krever Proxmox-konsoll |
| Innstillinger | Super+I åpner DMS settings | PASS (IPC/bind lastet) | registrert entydig bind til `dms ipc call settings open` |
| Hjelp | Super+F1 åpner DMS keybind-visning | PASS (IPC/bind lastet) | wrapper testet isolert; bind lastet |
| Programmer | Pakker installert | PASS | Firefox, Ghostty, Nautilus, GNOME Text Editor, Papers, Loupe, VLC kontrollert med `pacman -Q` |
| Programmer | Firefox synlig i launcher | PASS (GUI) | visuelt Firefox-treff |
| Programmer | Faktisk oppstart av representative apper | IKKE TESTET | ikke kjørt i denne sluttrunden |
| Standardvalg | nettleser og filbehandler | PASS | `dms-open.desktop`, `org.gnome.Nautilus.desktop` |
| Portal | Hyprland backend aktiv | PASS | portalens logg: PipeWire tilkoblet og screencopy init ok |
| Lyd | PipeWire/WirePlumber aktiv | PASS (tjeneste) | begge aktive; PipeWire Pulse socket-aktivert |
| Lyd/skjermdeling | reell avspilling/deling | IKKE TESTET | ingen brukerflyt utført |
| Lås/idle | én Hypridle-instans og fem-minutters regel | PASS | én PID, `found 1 rules`, timeout 300 |
| Lås | låseflate og PAM-opplåsing | IKKE TESTET | lokal autentisering må utføres av bruker |
| Persistens | observert etter ny grafisk innlogging/full omstart | IKKE TESTET | ikke logget ut eller rebootet aktiv økt |
| Ytelse | måling | DELVIS PASS | DMS ca. 370 MiB RSS før siste reload; Hypridle ca. 1 MiB; VM-ytelse er ikke maskinvaregaranti |

## Manuell sluttkontroll

1. I Proxmox-konsollen: trykk hver Wilsof-bind, spesielt Super+Space, Super+I og Super+F1.
2. I Spotlight: test piltaster, Enter, Esc, åpne vindu/søk/innstillinger og systemhandlingers bekreftelsesdialoger uten å utføre dem.
3. Trykk Super+L og test den viste Hyprlock-flaten og lokal PAM-opplåsing; vent fem minutter for idle-lås.
4. Logg ut/inn og reboot én gang når den aktive arbeidsøkten kan avsluttes; observer bakgrunn, tema og launcher på nytt.
