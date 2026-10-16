# Status — Wilsof Arch-prototype

Oppdatert: 2026-10-16 UTC

## Faktisk mål

- VM 113 `wilsof-arch-test`, Arch Linux på installert Btrfs-root (`@`) og `/home` (`@home`), ikke live-medie.
- DMS 1.6.3-2, Hyprland 0.56.2-4, Hyprlock 0.9.6-3, Hypridle 0.1.8-2 og xdg-desktop-portal-hyprland 1.4.1-2.
- DMS-generert `~/.config/hypr/hyprland.lua` eies av DMS. Wilsof lastes separat sist med `require("wilsof")` og endrer ikke DMS-fragmentene.

## Rettet i denne økten

Den tidligere installasjonen skrev `wilsof-session.target` og aktiverte wallpaper-enheten, men DMS sin faktiske Lua-entrypoint startet `hyprland-session.target`, ikke Wilsof-målet. Wallpaper-enheten ble derfor aldri kjørt. DMS manglet også en fast custom-theme-konfigurasjon og brukte standardpaletten.

Rettelsen:

- `wilsof.lua` starter Wilsof-targetet ved `hyprland.start`.
- `wilsof-wallpaper.service` bruker dokumentert DMS-IPC med én eier av bakgrunnen.
- En komplett statisk DMS custom theme-fil setter charcoal/isblå palett; `DMS_DISABLE_MATUGEN=1` hindrer wallpaper-avledet palette.
- Førstegangsinnstillinger lager en minimal DMS-linje: workspace-switcher, klokke, tray/batteri/kontrollsenter. Eksisterende personlige `settings.json` overskrives ikke.
- Wilsof fjerner bare kolliderende genererte DMS-binds via dokumentert `hl.unbind`, før de avtalte bindingene registreres.
- Hypridle bruker `$HOME/.local/bin/wilsof-lock`; den kjørende user-tjenesten manglet ellers `~/.local/bin` i PATH.

## Lokal retting 2026-10-16 (venter på VM-utplassering)

- Snarveihjelpen brukte tidligere bare DMS sin generiske keybind-dialog. Den ga ingen Wilsof-spesifikk forklaring, kunne ikke vise opt-in VM-bindingene separat, og `SUPER + F1` ble ikke eksplisitt fjernet fra mulige DMS-kollisjoner. `wilsof-help` åpner nå en lokal Ghostty-visning fra `config/wilsof-shortcuts.json`; den forklarer Super som Command/Windows, viser bare Wilsof-bindingene og viser VM-testlaget kun når markerfilen er aktiv. `SUPER + F1` er lagt til i den eksplisitte `hl.unbind`-listen.
- `wilsof-lock` søker nå bare etter Hyprlock for gjeldende UID og melder tydelig ved allerede aktiv lås, slik at en annen brukers prosess ikke kan undertrykke nytt låseforsøk og gjentatte forsøk ikke konkurrerer.
- Installereren sikkerhetskopierer eksisterende Wilsof-administrerte filer under `~/.local/state/wilsof-os/backups/<UTC-tid>/` før erstatning. Den bevarer fortsatt DMS `settings.json`.
- Dette er lokalt testet (30 pytest bestått, shell/JSON-validering), men IKKE utplassert eller GUI-observert fordi SSH-autentisering til VM 113 avvises selv om hostnøkkelen matcher den pinnede ED25519-fingeravtrykket.

## Grafisk evidens

Følgende er ekte DMS-skjermbilder fra VM 113, hentet via DMS sin støttede screenshot-funksjon:

- `evidence/desktop-wilsof-clean.png`: PASS visuelt — godkjent WS-bakgrunn, tomt skrivebord, charcoal/isblå og redusert topplinje.
- `evidence/launcher-firefox-query.png`: PASS visuelt — Spotlight viser søk øverst og Firefox som programtreff.

`launcher-empty.png` ble tatt i et toggletilstand uten synlig panel og er ikke brukt som positivt visuelt bevis.

## Valgfritt VM-testoppsett

For klienter som fanger Super før Proxmox-nettkonsollen kan `wilsof-vm-test-binds enable` aktiveres av `wilsofdev`. Det legger kun til fire Ctrl+Alt-bind: Space (launcher), L (lås), I (innstillinger) og F1 (hjelp). IPC-kontroll på VM 113 etter aktivering viste én forekomst av hver Ctrl+Alt-bind og fortsatt én tilsvarende Super-bind. `wilsof-vm-test-binds disable` fjerner oppsettet og reloader Hyprland. Fysisk klienttest fra Omarchy/MacBook er IKKE TESTET av agenten.

## Kjente begrensninger

DMS Spotlight viser programmer og et lokalt Files-filter visuelt. Det er ikke etablert bevis for komplette vindus-, innstillings- og systemhandlingsleverandører, norsk/engelsk aliasering eller sikker lokal filavgrensning. Dette er derfor ikke markert implementert.

`pipewire-pulse.service` er socket-aktivert og var inaktiv ved kontroll; PipeWire og WirePlumber kjørte. Ingen lydavspilling eller skjermdeling ble prøvd. Hypridle-konfigurasjon og én instans er kontrollert, men faktisk låsflate/autentisering/opplåsing er ikke testet fordi det krever lokal passordinntasting.
