# Wilsof OS — implementeringsroadmap

Status: produktplan fra PR #36, presisert for M1 2026-10-29 UTC. Kun profil-CLI/tilstand implementeres i M1; øvrige funksjoner er planlagte, ikke levert.
Rekkefølgen er satt etter fullført teknisk kartlegging (se WILSOF_TECHNICAL_ARCHITECTURE.md). Ingen milepæl starter automatisk.

## Forutsetninger for alle produktmilepæler

- Arbeid skjer på avgrensede grener fra `integration/internal-iso-20261026`-koden uten å endre PR #27s status; ingen merge til main/arch-install uten særskilt godkjenning (Engineering Standards §12).[51]
- Hver milepål leverer sine egne tester i eksisterende pytest/ShellCheck/JSON-verifiseringskjede og dokumenterer faktiske kommandoer/resultater.[51][52]
- GUI-/interaksjonsporter kjøres i VM etter eksisterende runbook; fysiske klientporter merkes human-check og utgår til eier (CONTRIBUTING.md review boundary).[52]
- Ingen ISO-bygg, QEMU-installasjonsporter eller fysiske diskoperasjoner inngår i produktmilepælene.

## Atskilt spor: internal2-stabilitet (IKKE produktutvikling)

Holdes fullstendig utenfor produktroadmapen; dagens status er internal2 virtuell funksjonsaksept med åpne merknader R1–R5, ingen merge/release, PR #27 OPEN/DRAFT, #34/#16 åpne.[53] Eksisterende anbefaling står ved lag: fysisk USB live-test av samme SHA256 krever separat eiergodkjenning.[53] Produktdokumentene forutsetter ikke at dette sporet er ferdig.

## M1 — Grunnmur: profiltilstand og CLEAN-garanti

- Prioritet: **MUST HAVE** (første implementeringsmilepæl).
- Omfang: `wilsof-profile` CLI (set/get/list) med JSON-tilstand i `~/.local/state/wilsof-os/profile.json`, schema v1, CLEAN som eneste standard; CLEAN-fallback ved ugyldig/fraværende fil; enhetstester; dokumentert tilstandsformat i `docs/product/`.
- Forutsetninger: ingen utover kildegrunnlaget.
- Leveranser: binær/skript, testfiler, docs-oppdatering.
- Risiko: lav (ren lokal tilstand, ingen UI).
- Tester: parser-enheter (gyldig/ugyldig/tom/korrupt), CLI-argumentvalidering, CI-grønn.
- **Definition of Done (presisert M1):** CLI-grensesnitt, alle fire profiler, korrupsjon/ukjent versjon, rettigheter, atomisk skriving, avbrudd, konkurranse og confinement verifiseres headless i eksisterende pytest/CI. Ingen VM er nødvendig for en ren fil-/CLI-kontrakt. GUI-synlighet er kun kontrakt nå, med aksept i M2/M4. Ingen eksisterende desktopatferd endres; faktisk eksakt-head CI, diffkontroll og kontrollpunkt rapporteres.[51]
- Detaljer: [tilstandsformat og gjenoppretting](WILSOF_PROFILE_STATE.md), UX §2.2/§2.6 (CLEAN og opptatt arbeidsområde 1). M1 installerer ikke CLI automatisk i eksisterende skrivebord.

## M2 — Wilsof Launcher-plugin og profil i topbar

- Prioritet: **MUST HAVE**.
- Omfang: DMS launcher-plugin (`type: launcher`) med 4 profiloppføringer + kuraterte systemhandlinger (lås, omstart med DMS-bekreftelse, åpne innstillinger, åpne hjelp, åpne Quick Settings); liten DMS bar-widget som viser aktiv profil og klikk-åpner profilvalg; distribusjon via `runtime/desktop.py`-manifestet; `wilsof-search`-dokumentasjon oppdatert med faktisk spotlight-modus (verifiser `spotlight toggle` vs. `launcher toggleWith apps` i VM).
- Forutsetninger: M1.
- Leveranser: plugin-mapper + manifest, desktop.py-utvidelse, VM-porte M2.
- Risiko: middels-lav (DMS plugin-API er dokumentert og stabilt i 2.0;[2][50] visningsfeil isoleres i plugin).
- Tester: manifest-validering, VM-visuell inspeksjon, tastaturnavigasjonspor (piler/Enter/Esc).
- **Definition of Done:** profilbytte via launcher og klikk i bar verifisert i VM med 3 åpne vinduer (ingen lukkes, topbar ≤2 s); launcher-oversikten dokumentert; fysiske tastaturporter listet som uverifiserte.

## M3 — Bar- og binds-konsolidering

- Prioritet: **MUST HAVE**.
- Omfang: settings-mal utvidet med DMS Quick Settings-widgetene (nettverk/Bluetooth/lyd + kontrollsenter; batteri betinget); én generisk modal-dialog-regel i `wilsof.lua`; avvikling av legacy `wilsof.conf`-dobbeltkilde (én bind-kilde; migreringsnotat).
- Forutsetninger: M2 (samme distribusjonsflate).
- Risiko: lav (konfigurasjonsendringer; window-rules er dokumenterte effekter).[45]
- Tester: eksisterende `test_hypr_config.py`/`test_desktop_runtime.py` utvides; VM-port for modal-dialog (GNOME-dialog-app).
- **Definition of Done:** bar-struktur per UX-spec §5.1 verifisert i VM; modal-dialoger flyter og sentreres; kun én bind-kilde i kilde-treet; CI grønn.

## M4 — Wilsof Tasks (dashboard/Kanban MVP)

- Prioritet: **MUST HAVE** (STUDY/DEV/EVERYDAY avhenger av den; CLEAN uavhengig).
- Omfang: PySide6-app med SQLite-lager; tre moduser; To Do/In Progress/Done; prosjekt-/fagsvelger; fristfelt; JSON-eksport; VACUUM INTO-rotasjon; versjonert migrering; Charcoal-tokens; launcher-oppføring.
- Forutsetninger: M1 (profiltjeneste for startmodus); arkitekturdokumentets valg godkjent av eier.
- Leveranser: app-kilde, PKGBUILD-utkast (kun i repo, ikke bygg), tester, brukerdok.
- Risiko: middels (største egne kodeflate; nye avhengighet python-pyside6).
- Tester: lager-/migreringsenheter, eksport-integrasjon, krasjisolasjonstest (SIGKILL under redigering), VM-port M4-matrise.
- **Definition of Done:** alle M4-akseptansekriterier i arkitekturdokumentet §5.2 verifisert i VM; appen krasj-testet uten effekt på Hyprland/innlogging; eksport gjeninnlesbar; dokumentasjon oppdatert.

## M5 — Wallpaper-utholdenhet og Restore

- Prioritet: **SHOULD HAVE** (R5-utbedring haster visuelt; Restore er dokumentert audit-funn).
- Omfang: wallpaper-reaktivering ved DMS-start/restart etter [R5-oppfølgingen](../qa/2026-10-29-wallpaper-follow-up.md); ikke `Restart=on-failure` alene ved avhengighetsfeil. Separat `wilsof-restore --list/--preview/--apply` for Wilsof-eide filer med backupmanifest; negative tester for stier utenfor manifest.
- Forutsetninger: M1 (distribusjonsutvidelser på plass).
- Risiko: lav-middels (systemd-unit-endring; ingen ny tjeneste).
- Tester: enhet på restore-valg/diff; VM-port: DMS-restart → bakgrunn korrekt; restore avWilsof-fil med forhåndsvisning.
- **Definition of Done:** etter simulert DMS-restart vises godkjent asset (VM-bevis); restore-port bestått; ingen rollback-påstand utover dokumentert filgjenoppretting.

## M6 — Oppdateringsopplevelse (kuratering, ikke kode)

- Prioritet: **SHOULD HAVE**.
- Omfang: aktiver/kurater DMS System Updater-UI i Wilsof-settings; legg `pacman-contrib` i pakkesettet; definer default poll-intervall og ignor-liste-politikk; dokumenter brukerflyten (sjekk → presentasjon → sudo/doas/run0-autentisering → full `-Syu` → omstartsanbefaling ved kernel); VM-port med full pakkeoppgradering på disponibel disk (separat godkjenning, iht. eksisterende oppdateringsporter).
- Forutsetninger: M3; eiergodkjenning for reell upgrade-test.
- Risiko: middels (berører privilegert kjede;[33] fulle Engineering Standards høyrisikokrav gjelder).[51]
- Tester: `dms system update --check --json`-kontrakttest i VM; full oppgraderingsport kun etter tillatelse.
- **Definition of Done:** dokumentert flyt, verifisert check-steg i VM, full oppgraderingsport utført eller eksplisitt fremført som gjenstående med begrunnelse; ingen delvis oppgradering mulig via Wilsof-flaten.[32]

## M7 — Designgjennomgang og designsystem-fiksering

- Prioritet: **SHOULD HAVE**.
- Omfang: programmatisk kontrast-sjekk av Charcoal-tokens mot UX-akseptansekriteriene; token-fil som én delt kilde for dashboard/plugins; eventuelle avvik rettes (kun Wilsof-eide flater).
- Risiko: lav.
- **Definition of Done:** alle akseptansekriteriene i UX-dokumentet §7.4 verifisert eller eksplisitt utsatt med grunn; token-kilde dokumentert.

## FUTURE (eksplisitt utsatt; ikke i roadmap-budsjett)

- Filsøk via dsearch (supply-chain/personvernvurdering kreves først;[52] ikke-omfattende i MVP).
- README/bruksdok på engelsk; tema-lysvariant; flere profilinnstillinger.
- Snapshots/rollback på vilkår av fremtidig boot/filsystemvedtak (ingen løsning finnes på nåværende ext4/systemd-boot-kontrakt uten større underspor).
- Kalender-/synk/AI-integrasjoner (produktnektelser i første versjon).

## Anbefalt rekkefølge og avhengigheter

M1 → M2 → M3 (parallell med M4-forarbeid) → M4 → M5 → M6 → M7. M4 kan startes etter M1 hvis eier godkjenner dashboardarkitekturen tidlig. Hver milepål avsluttes med kontrollpunkt og rapport per fast rapporteringsstandard; ingenting auto-startes.[51]

## Sources

- [2] https://raw.githubusercontent.com/duxlabs-dev/dux-shell/v2.0.0/.agents/skills/dms-plugin-dev/references/launcher-plugin-guide.md
- [32] https://raw.githubusercontent.com/duxlabs-dev/dux-shell/v2.0.0/core/internal/server/sysupdate/backend_pacman.go
- [33] https://raw.githubusercontent.com/duxlabs-dev/dux-shell/v2.0.0/core/internal/server/sysupdate/executor.go
- [45] https://raw.githubusercontent.com/hyprwm/hyprland-wiki/e9b1f8f56bc1e74d3f4d8cb64b55147152658fe2/content/configuring/core/rules/window-rules.md
- [50] https://raw.githubusercontent.com/duxlabs-dev/dux-docs/6bf44c0c03bd4c3a917abeaa6b366fda741c2f76/versioned_docs/version-2.0/dms/plugin-development.mdx
- [51] https://github.com/tomli0/wilsof-os/blob/a78d88790754886750bb1a5f93dd33cb257cc47e/docs/ENGINEERING_STANDARDS.md
- [52] https://github.com/tomli0/wilsof-os/tree/219894f1d4fc365b5e6546c2af9a146141634a1c
- [53] https://github.com/tomli0/wilsof-os/blob/219894f1d4fc365b5e6546c2af9a146141634a1c/docs/development-reports/2026-10-28-internal2-acceptance.md
