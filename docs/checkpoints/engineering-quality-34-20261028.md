# Kontrollpunkt — Engineering Quality #34, 28. oktober 2026

Status: **A–D lokalt verifisert; STOPP ved uavhengig review-/kostnadsgate. Ingen ISO- eller full milepælaksept.**

## Identitet og leveranse

- Gren: `integration/internal-iso-20261026`, draft [PR #27](https://github.com/tomli0/wilsof-os/pull/27).
- Start-head: `9aebacdd82072257f57c0c31d17a1f7f600a4acb`.
- Kodecommit: **`f628884b314dd13c3bf9d7059eee2fefec1b3400`**. Remote-head og alle ti endrede blobs kontrollert.
- [Full 12-punktsrapport](../development-reports/2026-10-28-engineering-quality-34.md).
- [Native-kontrakt/runbook](../native-chroot-contract-test.md).

## Faktisk verifikasjon

- A: eksplisitt arch-install-scripts, støttet baseline >=31 og faktisk `-r`-parsing; kjørbar customization testes før eventuell pakkeinstallasjon. Historisk v28-påstand korrigert mot oppstrøms kilde.
- B: resolver-postbetingelse og relevante negative tilfeller; opprinnelig feil/exitkode bevares også når resolverinspeksjon feiler.
- C: ni fullflyttilfeller for `install_package(Path('/'))`, ingen chroot/fallback; to avviste mutanter.
- D: eksakt opt-in-inngangspunkt med ekte arch-chroot **31-2** og Pacman, **2 passed**. API-mounts, resolver, installasjon exit0, ugyldig pakke exit1, kommando exit23, oppsettfeil exit1 og teardown verifisert. Rootless container, ingen blokknoder, avgrenset dev/sys-adapter, container fjernet.
- Full standardsuite: **201 passed, 1 skipped**. Native-gaten er ikke automatisk CI.
- ShellCheck, JSON, Python-kompilering og diffkontroll bestått.
- [CI 40760360240](https://github.com/tomli0/wilsof-os/actions/runs/40760360240): **success for eksakt f628884**, 201 passed / 1 skipped.
- Sluttversjonen av fixture-uttrekkshjelperen kjørt; manifest **62 filer / 52 lenker** identisk med testet fixtur.

## Blokkering og sikker stopp

Ingen ny Claude-review sendt. Eksisterende QA-rute er Claude Sonnet 4.6 via OpenRouter, men samlet 300 NOK/måned og deaktivert påfylling er ikke dokumentert av den eksisterende 50 USD-nøkkelgrensen. Ingen betalt fallback eller endring i providerkonfigurasjon.

Lagring ved **2026-10-28T20:09:12Z**: **26770972672 tilgjengelige byte (24,932411194 GiB)**, under 25 GiB med **72572928 byte**. Før oppgaven: **26980790272 byte (25,127819061 GiB)**. Bevarte artefakter og testbevis er ikke slettet.

Ingen ny ISO, VM-installasjon, fysisk disk-/USB-/Proxmox-operasjon, merge eller release. `internal1` er bevart med SHA256 `ab78770ce5c4c5fe8b7b913263ade47e4f2d8830a4ffbb6a38c935c9e9a45e83` og historisk installasjonsfeil; den inneholder ikke nye rettelser. Main er uendret. PR #35 og dets worktree er ikke endret.

Ingen beskyttet lab-/byggeprosess gjenstår. Prosjektlåsen holdes gjennom synkron publisering; faktisk frigivelses-/tilgjengelighetskvittering registreres privat og i status-issue etter siste push. Wilsof-jobb `8df95a6101e7` er paused/disabled; worker-kontroll paused=true. Ingen scheduler/bakgrunnsarbeider startes.

## Neste tillatte handling

Avklar kostnads-/akseptgaten før én avgrenset Claude-review av identifisert kodecommit. Ny plasskontroll og **separat eksplisitt godkjenning** kreves fortsatt før senere ISO-bygg. Issues #34 og #16 holdes åpne. Ingenting startes automatisk.

Private RED/GREEN-/native-/fixture-/kilde-/budsjett-/CI-bevis og endelige publiserings-ID-er er bevart i den varige QA-kontrollpunktgruppen for denne milepælen; ingen rå samtaler eller hemmeligheter inngår i Git.
