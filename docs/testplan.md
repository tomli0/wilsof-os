# Testplan og evidens

| Område | Kriterium | Status | Evidens |
|---|---|---|---|
| Assets | Alle tre leverte filer finnes i prosjektet | PASS | statisk pytest-kontroll |
| Konfigurasjon | Én Super+Space-inngang og vindu-/arbeidsområdebindinger 1–9 | PASS | statisk pytest-kontroll |
| Konfigurasjon | Aktiv/inaktiv kant, avrunding og mellomrom følger designretning | PASS | statisk pytest-kontroll |
| DMS-bro | Kun `toggle` aksepteres og delegeres til DMS Spotlight | PASS | isolert test med falsk `dms` |
| Målmaskinvakt | Installasjon krever `WILSOF_TARGET_VM=1` | PASS | isolert test |
| Script-syntaks | Alle shellskript parses av `/bin/sh` | PASS | `sh -n` |
| Wallpaper | Filsti med mellomrom er sitert; DMS sjekkes før kjøring | PASS | statisk pytest-kontroll |
| Browserprototype | Samlet lokalt søk, grupper og bekreftelsesdialog vises | IKKE TESTET | Ikke del av aktiv OS-konfigurasjon |
| GUI | Tomt skrivebord og topplinje | IKKE TESTET | Krever autorisert VM + grafisk konsoll |
| GUI | Syv standardprogrammer åpner og desktop-id-er er riktige | IKKE TESTET | Krever autorisert VM |
| GUI | Super+Space, filter, piler, Enter og Esc | IKKE TESTET | Krever autorisert VM |
| GUI | Fokus, flislegging, flytting og arbeidsområder | IKKE TESTET | Krever autorisert VM |
| Sikkerhet | Lås autentiserer; reboot/shutdown/logout bekreftes | IKKE TESTET | Krever autorisert VM og faktisk DMS/provider-integrasjon |
| Plattform | D-Bus, polkit, SELinux, lyd og portals | IKKE TESTET | Krever autorisert VM |
| Robusthet | Overlever restart; ingen duplisert autostart | IKKE TESTET | Krever autorisert VM |
| Fysisk | GPU, Wi-Fi, suspend og Secure Boot | IKKE TESTET | Ikke verifisert i VM |
| Installer/bootc | Bygg, installasjon og rollback | IKKE TESTET | Utenfor dette spiket |

Alle PASS-markeringer over er statiske eller isolerte scriptkontroller der dette er eksplisitt oppgitt. Ingen GUI-status blir PASS uten grafisk kjøring.