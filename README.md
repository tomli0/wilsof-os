# Wilsof OS — Arch-skrivebordsprototype

Wilsof er foreløpig en Arch-basert skrivebordsprototype under utvikling. Dette er ikke et ferdig, selvstendig OS, et produksjonsklart installasjonsmedium eller en release.

## Nåværende prototype

- Arch Linux, Hyprland 0.56.2 og DankMaterialShell (DMS) 1.6.3 i den dedikerte test-VM-en.
- Godkjent WS-bakgrunn, mørk `#14181E` overflate og isblå `#86B9CE` aksent.
- Tomt skrivebord og en nedstrippet DMS-linje med arbeidsområder, klokke og nødvendig status.
- `Super+Space` åpner DMS Spotlight. DMS leverer programmer og lokale filtreff; vinduer og systemhandlinger må fortsatt verifiseres separat.
- `Super+L` og Hypridle bruker samme `wilsof-lock`-wrapper rundt Hyprlock. Wrapperen er idempotent per bruker og melder eksplisitt når Hyprlock allerede kjører. Autentisering/opplåsing er ikke testet av agenten.
- `Super+F1` åpner en lokal, tastatur-lukkbar snarveihjelp i Ghostty. Den leser Wilsofs versjonerte snarveimanifest; aktive Ctrl+Alt VM-testbindinger vises separat.

Faktisk teststatus, begrensninger og skjermbilder står i `docs/status.md`, `docs/testplan.md` og `docs/avvik.md`.

## Rask, kontrollert installasjon av brukerprofil

Kjør kun på den dedikerte Wilsof-VM-en som `wilsofdev`:

    WILSOF_TARGET_VM=1 /opt/wilsof-os/scripts/install-user-config.sh

Skriptet nekter andre operativsystemer, kopierer bare Wilsof-filer til brukerens hjemmekatalog og er idempotent. På første installasjon setter det en statisk DMS-palett og en minimal topplinje. Senere installasjoner beholder `~/.config/DankMaterialShell/settings.json`; tilbakestilling er dokumentert i `docs/vm-runbook.md`.

## Valgfri VM-testbinding

Hvis VM-klienten fanger Super, kan en Wilsof-bruker aktivere bare fire Ctrl+Alt-fallbacks med `wilsof-vm-test-binds enable`: Space (launcher), L (lås), I (innstillinger) og F1 (hjelp). Slå dem av igjen med `wilsof-vm-test-binds disable`. Wilsof-standardbindingene endres ikke.

## Utviklerkontroll

    pytest -q
    sh -n scripts/*.sh bin/wilsof-*
    python3 -m json.tool config/dms/wilsof-theme.json

## Om komponentene

Wilsof integrerer eksisterende Arch-, Hyprland-, Hyprlock-, Hypridle- og DMS-komponenter. Prosjektet påstår ikke eierskap til disse. Se `docs/arkitektur.md` for integrasjonsgrensene og `docs/beslutningslogg.md` for beslutningene.
