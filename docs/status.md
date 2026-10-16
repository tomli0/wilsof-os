# Status — Wilsof OS første prototype

Oppdatert: 2026-10-15 UTC

## Faktisk implementert på VM 112 (`wilsof-test`)

- Målmaskinen er Fedora Linux 44 Workstation på KVM. Rotfilsystemet er Btrfs på `/dev/sda3`; oppstartslinjen bruker diskens `root=UUID=…`. Ingen LiveOS-markør eller squashfs-mount er tilstede.
- GNOME/GDM er beholdt og `gdm` er aktivert som reserveinnlogging.
- Verifiserte pakker: DMS 1.6.3, Hyprland 0.56.2, Hyprlock 0.9.6, Hypridle 0.1.8 og xdg-desktop-portal-hyprland 1.4.1.
- DMS sin offisielle headless-generator har opprettet den primære Hyprland Lua-konfigurasjonen. Wilsof installerer en separat `wilsof.lua`, lastet én gang etter DMS sine moduler; den overstyrer designverdier og `Super+Space`/`Super+L` uten å endre DMS-genererte filer.
- `wilsof-search toggle` er en smal DMS Spotlight-bro. `wilsof-lock` starter den installerte PAM-baserte Hyprlock én gang; Hypridle bruker samme wrapper ved inaktivitet og før suspend.
- Godkjent bakgrunn er installert i brukerens Wilsof-ressurser og `wilsof-wallpaper.service` er aktivert i Wilsof-sesjonsmålet. DMS må kjøre før tjenesten kan sette bakgrunnen.
- Installasjonsskriptet er mål-VM-beskyttet, idempotent og aktiverer bare bruker-tjenester. Det oppretter ingen sudo-regler.

## Testresultater

| Kontroll | Status | Evidens |
|---|---|---|
| Lokale tester | PASS | `pytest -q`: 15 passed |
| Shell-syntaks og whitespace | PASS | `sh -n` for alle shellskript; `git diff --check` |
| Bootstrap kilde-/pakkevakt | PASS | Fedora 44- og pakkesjekk, RPM-signaturkontroll og GDM-vakt testet statisk; kjørt på VM |
| Mål-VM preflight | PASS | Fedora, `dnf`, `hyprctl`, `dms`, user-systemd og SELinux Enforcing |
| Pakker og kilder | PASS | RPM-versjoner og DMS/Hyprland COPR-er avlest på VM |
| Installer-idempotens | PASS | To kjøringer; nøyaktig én `require("wilsof")` i Hyprland Lua-entrypoint |
| Systemd-enheter | PASS | `systemd-analyze --user verify` uten feil |
| Hyprland-konfigurasjon | PASS | `Hyprland --verify-config --config ~/.config/hypr/hyprland.lua` → `config ok` |
| Wrapper-sikkerhet | PASS | ugyldige argumenter avvises med exit 64 |
| DMS/Hyprland-grafisk økt | IKKE TESTET | SSH-økten står fortsatt i GNOME; DMS og Hypridle starter først i Hyprland-økten |
| Bakgrunn og tomt skrivebord | IKKE TESTET | krever faktisk Hyprland-innlogging |
| Super+Space / DMS Spotlight | IKKE TESTET | krever aktiv DMS i Hyprland-økten |
| Hyprlock-autentisering | IKKE TESTET | krever faktisk lås, lokal autentisering og opplåsing |
| Portal, lyd og skjermdeling | IKKE TESTET | krever aktiv Hyprland-økt |

## Pakkekilder

- Fedora 44: grunnsystem, GDM og standardkomponenter.
- `copr:copr.fedorainfracloud.org:avengemedia:dms`: DMS 1.6.3; den aktiverte automatisk avhengigheten `avengemedia/danklinux`.
- `copr:copr.fedorainfracloud.org:ashbuk:Hyprland-Fedora`: Hyprland, Hyprlock, Hypridle og Hyprland-portalen.

## Neste nødvendige manuelle handling

Velg **Hyprland** i GDM for `wilsofdev` og gjennomfør GUI-sjekklisten i `docs/testplan.md`. GNOME beholdes som reservevalg.