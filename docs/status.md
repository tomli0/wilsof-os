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

## Grafisk evidens

Følgende er ekte DMS-skjermbilder fra VM 113, hentet via DMS sin støttede screenshot-funksjon:

- `evidence/desktop-wilsof-clean.png`: PASS visuelt — godkjent WS-bakgrunn, tomt skrivebord, charcoal/isblå og redusert topplinje.
- `evidence/launcher-firefox-query.png`: PASS visuelt — Spotlight viser søk øverst og Firefox som programtreff.

`launcher-empty.png` ble tatt i et toggletilstand uten synlig panel og er ikke brukt som positivt visuelt bevis.

## Kjente begrensninger

DMS Spotlight viser programmer og et lokalt Files-filter visuelt. Det er ikke etablert bevis for komplette vindus-, innstillings- og systemhandlingsleverandører, norsk/engelsk aliasering eller sikker lokal filavgrensning. Dette er derfor ikke markert implementert.

`pipewire-pulse.service` er socket-aktivert og var inaktiv ved kontroll; PipeWire og WirePlumber kjørte. Ingen lydavspilling eller skjermdeling ble prøvd. Hypridle-konfigurasjon og én instans er kontrollert, men faktisk låsflate/autentisering/opplåsing er ikke testet fordi det krever lokal passordinntasting.
