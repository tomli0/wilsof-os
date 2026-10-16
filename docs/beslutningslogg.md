# Beslutningslogg

## D-001 — Arch som aktiv prototypeplattform

Status: vedtatt. Arch VM 113 er aktivt testmål. Fedora-materiale beholdes som historikk/referanse, men er ikke aktiv installasjonsvei.

## D-002 — DMS beholdes, Wilsof er override-lag

Status: vedtatt. DMS eier shell, bakgrunns-IPC og standardkonfigurasjon. Wilsof lastes separat sist, slik at DMS-generering ikke sletter prosjektets endringer.

## D-003 — Fast Wilsof-palett, ikke wallpaper-avledet

Status: vedtatt. `#14181E` og `#86B9CE` er faste designverdier. Matugen er deaktivert for DMS-tjenesten; custom theme er førsteinstallasjonsstandard og personlige senere valg beholdes.

## D-004 — Super+Space er én programfokusert DMS Launcher-inngang

Status: vedtatt med begrensning. Wrapperen åpner DMS Launcher med `toggleWith apps`, slik at programlisten er den forventede førstevisningen og QR-generatorens fritekstresultat ikke er vanlig søkeutfall. DMS sine faktisk visuelt dokumenterte programtreff brukes; filer, vinduer og systemhandlinger blir ikke påstått som launcherfunksjoner før de er testet.

## D-005 — ESP er `/boot`, ikke XBOOTLDR

Status: vedtatt. systemd-boot installeres med `--esp-path=/boot`; fallback-fil kontrolleres eksplisitt.
