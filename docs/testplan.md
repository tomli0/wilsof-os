# Testplan og evidens

| Område | Kriterium | Status | Evidens |
|---|---|---|---|
| Assets | Alle tre leverte filer finnes i prosjektet | PASS | `tests/test_hypr_config.py` |
| Konfigurasjon | Én Super+Space-inngang og nødvendige vindu-/arbeidsområdebindings | PASS | pytest lokalt |
| Konfigurasjon | Aktiv/inaktiv kant, avrunding og mellomrom følger designretning | PASS | pytest lokalt |
| Browserprototype | Samlet lokalt søk, grupper og bekreftelsesdialog vises | IKKE TESTET | Krever nettleserinteraksjon i denne revisjonen |
| GUI | Tomt skrivebord og topplinje | IKKE TESTET | Krever autorisert VM + grafisk konsoll |
| GUI | Syv standardprogrammer åpner og desktop-id-er er riktige | IKKE TESTET | Krever autorisert VM |
| GUI | Super+Space, filter, piler, Enter, Esc | IKKE TESTET | Krever autorisert VM |
| GUI | Fokus, flislegging, flytting, arbeidsområder | IKKE TESTET | Krever autorisert VM |
| Sikkerhet | Lås autentiserer; reboot/shutdown/logout bekreftes | IKKE TESTET | Krever autorisert VM |
| Plattform | D-Bus, polkit, SELinux, lyd og portals | IKKE TESTET | Krever autorisert VM |
| Robusthet | Overlever restart, ingen duplisert autostart | IKKE TESTET | Krever autorisert VM |
| Fysisk | GPU, Wi-Fi, suspend og Secure Boot | IKKE TESTET | Ikke relevant/verifisert i VM |
| Installer/bootc | Bygg, installasjon og rollback | IKKE TESTET | Utenfor dette spiket |

Automatiserte tester må utvides med faktisk DMS-plugin- og Hyprland-integrasjonstest når pakkeversjonene er låst. Ingen GUI-status skal endres til PASS basert på SSH eller statisk konfigurasjon.
