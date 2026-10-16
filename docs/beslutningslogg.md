# Beslutningslogg

## D-001 — Arch som aktiv prototypeplattform

Status: vedtatt. Arch VM 113 er aktivt testmål. Fedora-materiale beholdes som historikk/referanse, men er ikke aktiv installasjonsvei.

## D-002 — DMS beholdes, Wilsof er override-lag

Status: vedtatt. DMS eier shell, bakgrunns-IPC og standardkonfigurasjon. Wilsof lastes separat sist, slik at DMS-generering ikke sletter prosjektets endringer.

## D-003 — Fast Wilsof-palett, ikke wallpaper-avledet

Status: vedtatt. `#14181E` og `#86B9CE` er faste designverdier. Matugen er deaktivert for DMS-tjenesten; custom theme er førsteinstallasjonsstandard og personlige senere valg beholdes.

## D-004 — Super+Space er én DMS Spotlight-inngang

Status: vedtatt med begrensning. Wrapperen åpner DMS Spotlight. DMS sine faktiske, visuelt dokumenterte programtreff brukes; ikke-verifiserte aggregatorfunksjoner påstås ikke.

## D-005 — ESP er `/boot`, ikke XBOOTLDR

Status: vedtatt. systemd-boot installeres med `--esp-path=/boot`; fallback-fil kontrolleres eksplisitt.
