# Wilsof OS — design-desktop: Command Center, Modern Terminal-kandidat og About, 2026-10-31

Status: **LEVERT SOM DRAFT — IKKE FULL AKSEPT**. Command Center, Modern Terminal-grunnlag (Ghostty/tema/snarveier) og About er implementert og QEMU-verifisert i avgrensede akseptpunkter; grafisk login, Terminal Idle, Appearance-editor, snarvei-editor og fysiske porter er ikke levert. Ingen ISO bygget; ingen merge/release.

Utviklingsperiode UTC: 2026-10-30 23:41 – 2026-10-31 07:12 (hovedøkt), avslutnings-/nykontrolløkt 08:07–08:2x. Status-issue: #16. Draft-PR-er: #44 (Command Center, base fix/internal4-completion), #45 (Modern Terminal + About, stablet på #44).

Kildegren: `feat/command-center-20261031` slutt-head `dbe20edb89a0730d3e05f933f72806af11f5a4a3`; `feat/modern-terminal-20261031` slutt-head `0b2f99742ec59779df38dd4a2392ad359376d911` (rebased på Command Center-head). Baseline: PR #43-head `19a68247b0f406965db25e6ea950ce12ed0707f2` (uien). PR #42/#43 uendrede.

## Bevisgrunnlag og avgrensning

- Tidligere rapportert: internal4-completion-rapporten (19a6824) etablerte baseline, R1/R2-tilstand og lås-/pauseskikk.
- Historisk direkte verifisert (hovedøkt, disponibel gjest): rendret Command Center-standardvisning, tastet søk, pilvalg, Enter-aktivering av Ghostty/Firefox/Downloads/About, `hyprctl -j binds`-lesback, Ghostty-configvalidering, About-identitet, DMS NRestarts=0.
- Kontrollert på nytt (avslutningsøkt, UTC-tidspunkter i `resume-*.json`): begge eksakte kode-heads fulle pytest (340/2 og 345/2), AST/JSON/ShellCheck/diff-check, 47/47 bevaringshasher, kontrollfilhasher, qemu-prosessfravær, offline qcow2-sjekk 0, tilgjengelig prosjektlås via uavhengig flock-probe.
- Ikke utført / ikke autorisert: ISO-bygg, installasjon, merge, release, fysisk disk/USB/Proxmox, reaktivering av scheduler/worker, fysisk maskinvaretesting, ny uavhengig review.
- Private bevis: `~/.local/state/wilsof-qa/design-desktop-20261031/` (logs, JSON-prober, skjermbilder, JUnit, privat QA-passordfil ekskludert fra all publisering).

## 1. Fullførte milepæler

- **Wilsof Command Center** (M1, høyest prioritet): DMS-plugin-modal (`wilsofCommandCenter`, daemon-komponent i eksisterende DMS-prosess — ingen ny launcher-rammeverk, tjener, daemon eller indeks). Standardvisning: søkefelt + Browser/Terminal/Files + de sju kategoriene. Gjenbruker DMS `AppSearchService` (apper+handlinger), `dms_settings_search` (innstillinger), `SessionService.launchDesktopEntry/Action`, DModal/fokusgrab/tema og bekreftelsesbeskyttet Power-meny. Lokalt hjemmenavn-søk via `wilsof-file-search` (ingen innholdsindeks, ingen nettverk; skjulte mapper/symlenker/andre filsystemer/genererte kataloger utelatt; 80 ms/20 000 oppføringer/40 resultater-begrensninger; fast probing av Downloads/Documents/Desktop/Pictures/Music/Videos). `wilsof-search toggle` krever vår `WILSOF_COMMAND_CENTER_OK`-kvittering og beholder Spotlight som fallback. Faktiske feil funnet og rettet underveis: hover-endret valg, filresultat-race under modal-mapping (RED→GREEN `Model.accept`), vanlige mapper skjult av budsjettet (RED→GREEN).
- **Modern Terminal-grunnlag** (M2-del): Ghostty-config med `#121820`/`#86B9CE`-palett, JetBrainsMono Nerd Font, padding 12/10, native splits/kopier/lim/zoom-keybinds; seet én gang, personlige endringer beholdes; `ghostty +validate-config` bestått i gjest. DMS-tema `surface/background` oppdatert til `#121820` (godkjente eiendeler, topbar/kontrollsenter/boot uendret). `Super+B`/`Super+E` i egen seed-once-fil; `Super+Enter` (Ghostty) og `Super+1–9`-kart finnes allerede i DMS-genererte binds; lesback verifisert.
- **About Wilsof OS** (M7): egen DModal med installert SOURCE_COMMIT, plattforminfo, upstream-attribusjon med eksakte pakkeversjoner/lisenser, ærlig «ingen prosjektlisens»/«nettsted ikke konfigurert», GitHub-lenke og dedikasjonen «Dedicated to William and Sofie.»

## 2. QA-funn og utbedringer (egen gjennomgang — ikke uavhengig review)

| ID | Alvorlighet | Bevis | Utbedring |
| --- | --- | --- | --- |
| Søkeresultat-race | Middel | Filtresultater forkastet mens modal fortsatt mappet (`downloads`-spørring returnerte count 0) | `wantedOpen`-tilstand + `Model.accept(generation, query, wantedOpen)`; RED→GREEN; QEMU: `downloads` → valgt `file:/home/designqa/Downloads` |
| Vanlige mapper skjult av budsjett | Middel | `budget_ms=0`-test fant ikke Downloads | Fast, grunn probing av seks standardmapper før BFS; RED→GREEN |
| Hover endret valg | Lav | Musepeker over rad endret `selected` ved åpning | Hover-handler fjernet; kun piler/klikk endrer valg |
| Direkte exec av snarveier | Middel | `Quickshell.execDetached(["firefox"])` ville dø med DMS-prosessen | DesktopEntries.heuristicLookup + SessionService.launchDesktopEntry; locker/xdg-open via systemd-run --user --scope |
| Ghostty-splits | Lav | Ctrl+Shift+O/E sendt; skjermbilde viste fortsatt én pane | Status IKKE VERIFISERT — står som åpent GUI-punkt |
| TCG-ytelse | Høy (aksept) | Vertsmåling 48–53 ms total for 6001-oppføringsfixture; QEMU-TCG `downloads` 10 555 ms til nyttig rad; `about wilsof` 136–2 173 ms | 150 ms-målet er IKKE oppnådd i QEMU; mål er vertsmålbart, ikke TCG-sertifisert |

## 3. Kodekvalitet og sikkerhet

Endrede/nye filer (Command Center-gren, 5 commits): `config/dms/plugins/wilsofCommandCenter/{plugin.json,Model.js,CommandCenter.qml}`, `bin/wilsof-file-search`, `bin/wilsof-search`, `runtime/desktop.py`, `runtime/image-files.txt`, `tests/test_command_center.py`, `tests/test_file_search.py`, `tests/test_scripts.py`, `docs/product/WILSOF_COMMAND_CENTER.md`, `.github/workflows/validate.yml`. Modern Terminal-gren (2 commits til): `config/ghostty/config`, `config/dms/wilsof-theme.json`, `config/hypr/wilsof-app-shortcuts.lua`, `config/hypr/wilsof.lua`, `config/wilsof-shortcuts.json`, `bin/wilsof-about-info`, `About.qml`, tilhørende tester, samme manifest/CI-utvidelse.

- Filnavnssøk gjør bokstavelig navnesammenligning (tester med `$(touch pwned); note.txt`), følger aldri symlenker, krysser aldri filsystemgrenser, leser aldri innhold, sender aldri spørringer ut av verten.
- Søketekst håndteres aldri av et shell; `xdg-open` mottar ett kodet URI-argument.
- `runtime/desktop.py` bevarer eksisterende personlige settings/plugin-disable (tester for bevarte bytes etter reinstall), nekter symlink-destinasjoner og skriver kun i brukerhjemmet.
- Ghostty/app-snarveisfiler seedes kun når fraværende; kundeditede bytes testet bevart.
- Ingen berøring av autentisering, ERASE-gate, blankhetskontroll, signaturnivå, diskvalidering, approved assets, boot/splash/topbar/kontrollsenter eller DMS-genererte filer (`git diff --name-only` mot baseline på beskyttede stier: tom).

## 4. Commits og CI-status

| Commit | Gren/innhold | CI |
| --- | --- | --- |
| `6d64838` | feat(desktop): native DMS Command Center-kandidat | push-gren lagt til validate.yml-filtrene |
| `904c2ea` | fix(launcher): native app-politikk + isolert locker-livstid | — |
| `4276436` | test(search): eksplisitt loader-spesifikasjon | — |
| `47ec9fc` | fix(search): behold lokale resultater under asynkron mapping | — |
| `dbe20ed` | fix(search): prioriter vanlige hjemmemapper | Command Center-slutt-head |
| `e6396d2`→rebased | feat(theme): seed Modern Terminal Ghostty uten å overskrive brukerconfig | — |
| `0b2f997`→rebased | feat(desktop): installert-system About + personlige appsnarveier | Modern Terminal-slutt-head |

CI: `validate.yml` kjører pytest/ShellCheck/JSON/diff og er utvidet til begge push-grener og PR-baser; faktiske kjøringer på de publiserte headene avventer push og leses tilbake i publiseringkvitteringen. Lokale tilsvarende sjekker bestått på begge eksakte head (pytest 340/2 og 345/2, AST alle Python inkl. bin/-scripts, JSON-validering, ShellCheck begge dialekter, `git diff --check`).

## 5. ISO-filnavn, størrelse, SHA256 og plassering

**Ikke bygget. Null byggforsøk.** Siste leveranse forblir `wilsof-internal-2026.10.30-internal3-x86_64.iso`, 2 548 035 584 byte, SHA256 `b3cf9726f2d55a7a0398aadeb3287a839a5607a7dd7f5a10b9a862a5c1936dd1`, privat rot `internal-test-20261030-internal3/` — hash reverifisert uendret i avslutningsøkten (47/47-manifest inkludert alle seks ISO-er).

## 6. Resultat fra QEMU-gjester (design-desktop-økten)

Én disponibel child-COW-overlay (`qemu-img create -b` mot bevart internal4-completion `vm-boot1/disk.qcow2`; kjede verifisert: source-qa.qcow2 → internal3-new-24g.qcow2), originaldisk aldri skrevet direkte, aldri ny installasjon, aldri parallelle gjester.

| Port | Resultat | Bevis |
| --- | --- | --- |
| Kald UEFI-boot uten ISO | Bestått | greetd aktiv; tuigreet Username/Password-prompts visuelt verifisert før syntetisk input |
| Vanlig passordinnlogging (designqa) | Bestått | PAM `session opened for user designqa(uid=1002)`; start-hyprland-watchdog intakt |
| DMS-kaldstart | Bestått | ActiveState=active, NRestarts=0 ved alle målinger |
| Command Center åpnes/IPC | Bestått | `toggle`/`search`/`status`; marker `WILSOF_COMMAND_CENTER_OK` |
| Standardvisning rendret | Bestått | skjermbilde 09: 3 snarveier + 7 kategorier, søkefelt, utvalg |
| Tastet søk + pil + Enter | Bestått (avgrenset) | `terminal`→Ghostty PID 2452 (hyprctl-klient), `firefox`→app-rad valgt/påstartet, `downloads`→Nautilus på `~/Downloads` (PID 4578, tittel «Downloads») |
| Om Wilsof OS rendret | Bestått | skjermbilde 23: installert kilde 448e019…, attribusjon, lisens, dedikasjon |
| Ghostty-config | Bestått | `ghostty +validate-config` 0; show-config viser palett/padding/font |
| Super+B/E-registrering | Bestått | `hyprctl -j binds`-lesback av B/E/Return/space/L/F |
| Bevaring | Bestått | 47/47 SHA256 uendret etter økten; originaldisk/firmware uendret |

Avslutning: gjesteprosessen (731859) var avsluttet før gjenopptakelsen; `qemu.err` viser SIGTERM fra den avsluttende CLI-prosessen ved 150-iterasjonsstoppen — **grasiøs gjesteavslutning kan derfor ikke bekreftes, kun at prosessen er borte og ingen QEMU/disk-holder eksisterer**. Offline `qemu-img check` på egen overlay: exit 0, ingen feil.

Lagring målt ved avslutning: 83 GiB tilgjengelig (df 83G/195G); se terminalkvittering for eksakte byte.

## 7. Oppstart og passordinnlogging

Se punkt 6. Eksisterende tuigreet/start-hyprland-kjede uendret; det syntetiske designqa-passordet ble opprettet kun i den disponible overlayen og oppgis ikke her.

## 8. Gjenstående feil, begrensninger og uferdige designfunksjoner

- **M3 Grafisk login: IKKE LEVERT.** regreet 0.5.0-1/cage er identifisert i offisielle Arch-repo som kandidat, men ingen greeter er implementert eller testet. Eksisterende tuigreet forblir grepens løsning.
- **M4 Terminal Idle: IKKE LEVERT.** Ingen WS-idleflate implementert; hypridle/hyprlock-konfig uendret fra baseline.
- **M5 Appearance: DELVIS.** Command Center åpner DMS personalization-innstillinger; egen editor for tekstskalering/aksentfarger er ikke levert.
- **M6 Snarvei-editor: IKKE LEVERT.** Wilsof-bind-kart dokumentert/utvidet; DMS sin egen KeybindsModal er oppstrømsflate, ikke Wilsof-levert.
- **150 ms-målet: IKKE OPPNÅDD i QEMU/TCG** (10,6 s til nyttig rad for `downloads` under kalde DMS-ramper). Vertsmåling for selve søkehjelperen: 48–53 ms inkl. prosessoppstart. Målet gjenstår som utviklingsmål under reelle forhold.
- **Ghostty splits: IKKE VISUELT BEKREFTET** (én pane i skjermbilde).
- Musklikk-aktivering i Command Center, fokusretur ved lukking, gjentatte åpne/lukke-sykluser og Power-menyaktivasjon: **IKKE FULLFØRT TESTET** (Power-menyens bekreftelsesdialog er beholdt, men ikke utløst i test).
- R1 (DMS SIGKILL-årsak ukjent) og R2 (hyprtoolkit#144 upstream): uendrede, åpne. Fysisk Wi-Fi/lyd/BT: PENDING. TCG-begrensninger (trege kaldrstarter, hyprctl-IPC-timeouter, syntetisk tastatur ≠ fysisk tastatur) gjelder alt GUI-bevis.

## 9. Engineering standards og dokumentasjons-PR

Risikobasert minsteendring; RED→GREEN for alle kodefiksene; eksplisitt manifest-distribusjon uten glob; separasjon av fullført leveranse/WIP/ikke-testet overholdt i denne rapporten. Uavhengig review: **IKKE UTFØRT** (egen gjennomgang kun). #45/#46 er OPEN/DRAFT; #42/#43/#41/#40/#39/#38/#36 og alle issues forblir åpne; ingenting lukket eller merget.

## 10. API-/modellforbruk der det kan dokumenteres

| Rolle/faktisk modell | Periode/omfang | Forbruk | Bevisstatus |
| --- | --- | --- | --- |
| Hovedagent z-ai/glm-5.3 (openrouter) | hovedøkt + avslutning | se session metadata | estimert; actual_cost ikke tilgjengelig |

Ingen betalt review, delegert kontekst, nøkkelpåfylling eller providerprobe i avslutningsøkten; config hash-ukontrollert uendret mot controls-before.

## 11. Aktive prosesser og prosjektlåser

Ved avslutningskontroll: **ingen QEMU-prosesser, ingen holder av design-overlayen eller prosjektlåsfilen**. Opprinnelig lockholder (730160) og QEMU (731859) var borte ved gjenopptakelse; avslutningsøkten tok låsen kortvarig for lesesikkerhet, frigjorde den, og en uavhengig `flock -n`-probe bekreftet tilgjengelighet. Scheduler `enabled=false/paused`; worker `paused=true/stop_requested=false`; kontrollfilhasher uendrede. Ingen nye prosesser startes etter denne rapporten.

## 12. Neste anbefalte handling

Ett avgrenset steg: **fullfør Command Center-akseptmatrisen på en ny disponibel COW-gjest** — musklikk-aktivering, fokusretur, gjentatt åpne/lukke, Power-menybekreftelse og Ghostty-splits — før M3 (grafisk login med regreet på separat disponibel gjest med tuigreet som fallback) tas opp. Fysisk klient (Super+Space på fysisk tastatur, flerskjerm, Wi-Fi/lyd/BT) forblir eierens PENDING-porter. Ingenting starter automatisk.

## Publiseringskvittering

Etter push/read-back: eksakte head-URL-er for #45/#46, CI-lesback, #16-kommentar-ID, målt ledig plass og endelig lås-/prosesstilstand føres her og i privat kontrollpunkt.
