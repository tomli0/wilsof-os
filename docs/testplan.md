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
| Launcher | Programmodus åpnes via installert Wilsof-wrapper | PASS (IPC) | `wilsof-search toggle` → `LAUNCHER_TOGGLE_SUCCESS: apps` på VM 113 |
| Launcher | Tom programliste og Firefox-treff | PASS (GUI) | `evidence/vm113-2026-10-16-launcher-apps.png` og `evidence/vm113-2026-10-16-launcher-firefox.png` |
| Launcher | Piltaster/Enter/Esc via fysisk tastatur | IKKE TESTET | ingen Proxmox-konsollinput-observasjon |
| Launcher | Vinduer, filer, systemhandlinger, norsk/engelsk alias | IKKE TESTET / IKKE IMPLEMENTERT | Wilsof åpner programmodus; DMS-kategorier er oppstrøms og andre leverandører er ikke lovet |
| Bindinger | Lastet og entydig | PASS | Hyprland IPC-bindliste etter reload |
| Bindinger | Fysisk tastetrykk observert | IKKE TESTET | krever Proxmox-konsoll |
| Innstillinger | Super+I/DMS Settings åpnes | PASS (IPC/GUI) | `SETTINGS_OPEN_SUCCESS`; visuelt inspisert `evidence/vm113-2026-10-16-settings.png` |
| Systemhandlinger | Meny og hold-bekreftelse | PASS (IPC/GUI) | visuelt inspisert `evidence/vm113-2026-10-16-powermenu.png`; ingen handling utført |
| Hjelp | Lokal Wilsof-visning med faktiske standardbindinger, Super-forklaring og separat VM-lag | PASS (lokal wrapper/renderer) | 30 pytest; manifest-parser, Ghostty-kall, aktiv/inaktiv VM-seksjon og feilstatus testet |
| Hjelp | Faktisk vindu, fokus, lesbarhet og Enter-lukking i aktiv VM-sesjon | IKKE TESTET | SSH-syntetisk Ghostty-start ga `PostForkError`; reell Hyprland-binding er ikke testet |
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

## Valgfritt VM-testoppsett for klienter som fanger Super

Aktiveres bare i gjesten med `wilsof-vm-test-binds enable`. Dette lager en brukerfil under `~/.config/hypr/`, laster Hyprland på nytt og beholder alle Wilsof-standardbindingene. Kontrollert via Hyprland IPC: hver Ctrl+Alt-bind og den tilsvarende Super-binden forekommer nøyaktig én gang.

Prøv fysisk fra Proxmox-konsollen:

1. `Ctrl+Alt+Space` — launcher.
2. `Ctrl+Alt+L` — lås.
3. `Ctrl+Alt+I` — innstillinger.
4. `Ctrl+Alt+F1` — snarveihjelp.

Slå av med `wilsof-vm-test-binds disable` fra en grafisk Wilsof-terminal. Kommandoen fjerner bare den opt-in-filen og reloader Hyprland. Klientkonflikten fra Omarchy kan bare markeres fysisk kontrollert etter at disse fire tastetrykkene er observert i MacBook → Proxmox-konsoll → gjest-kjeden.

## Manuell sluttkontroll

1. I Proxmox-konsollen: trykk hver Wilsof-bind, spesielt Super+Space, Super+I og Super+F1.
2. I Spotlight: test piltaster, Enter, Esc, åpne vindu/søk/innstillinger og systemhandlingers bekreftelsesdialoger uten å utføre dem.
3. Trykk Super+L og test den viste Hyprlock-flaten og lokal PAM-opplåsing; vent fem minutter for idle-lås.
4. Logg ut/inn og reboot én gang når den aktive arbeidsøkten kan avsluttes; observer bakgrunn, tema og launcher på nytt.
