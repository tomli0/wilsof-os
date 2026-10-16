# Testplan og evidens

| Område | Kriterium | Status | Evidens |
|---|---|---|---|
| Assets | Alle tre leverte filer finnes i prosjektet | PASS | pytest |
| Konfigurasjon | Wilsof Lua lastes etter DMS-modulene; Super+Space og Super+L overstyres | PASS | pytest og `Hyprland --verify-config` på VM |
| Design | Aktiv/inaktiv kant, avrunding og mellomrom følger designretning | PASS | pytest og validert Lua-konfigurasjon |
| DMS-bro | Kun `toggle` aksepteres og delegeres til DMS Spotlight | PASS | isolert test med falsk `dms` |
| Låsebro | Kun argumentfri låsing godtas; Hyprlock startes maksimalt én gang | PASS | isolert test med falsk `hyprlock` |
| Målmaskinvakt | Installasjon krever `WILSOF_TARGET_VM=1` | PASS | isolert test |
| Installer | DMS/Hyrland Lua-integrasjon og user-unit enablement er idempotent | PASS | to VM-kjøringer; én `require("wilsof")` |
| Systemd | Wilsof-enheter parses | PASS | `systemd-analyze --user verify` på VM |
| Plattform | Fedora 44, installert disk, pakker og SELinux Enforcing | PASS | VM-kontroll via SSH |
| GUI | Godkjent bakgrunn, tomt skrivebord og DMS-topplinje | IKKE TESTET | krever Hyprland-innlogging ved grafisk konsoll |
| GUI | Super+Space åpner DMS Spotlight; Esc lukker den | IKKE TESTET | krever aktiv DMS i Hyprland-økten |
| GUI | Fokus, flislegging, flytting og arbeidsområder | IKKE TESTET | krever Hyprland-økt |
| Sikkerhet | Super+L og idle-lock starter Hyprlock; autentisering låser opp | IKKE TESTET | må observeres lokalt uten å dele passord |
| Plattform | Portal, lyd og skjermdeling | IKKE TESTET | krever Hyprland-økt |
| Robusthet | DMS, Hypridle og wallpaper starter igjen etter ut-/innlogging | IKKE TESTET | krever grafisk omstart |

## Kort GUI-sjekkliste

1. I GDM, velg **Hyprland** for `wilsofdev` og logg inn. GNOME skal fortsatt vises som alternativ.
2. Bekreft tomt skrivebord, godkjent mørk WS-bakgrunn og DMS-topplinje.
3. Trykk `Super+Space`; verifiser at DMS Spotlight åpnes. Lukk med `Esc`.
4. Trykk `Super+L`; bekreft at Hyprlock vises og at lokal autentisering låser opp igjen.
5. Vent fem minutter eller test Hypridle etter ønsket lokal metode; bekreft at skjermen låses uten duplikat locker.
6. Logg ut og inn i Hyprland én gang; gjenta punkt 2–4.

Ingen GUI-rad skal merkes PASS uten at den er observert i den grafiske økten.