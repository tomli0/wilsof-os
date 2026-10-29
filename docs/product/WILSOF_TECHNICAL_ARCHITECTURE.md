# Wilsof OS — teknisk arkitektur

Status: planleggingsdokument (ingen implementering). Dato: 2026-10-29 UTC. Kildegrunnlag: `integration/internal-iso-20261026` @ `219894f`[52] + Engineering Standards @ `a78d887`.[51]
Vedlikeholdsstatus (lest 2026-10-29): Dux Shell/DMS aktiv, MIT, v2.0.0 utgitt 2026-10-20;[54] Hyprland aktiv, BSD-3-Clause, v0.57.0 utgitt 2026-10-28;[56] Quickshell aktiv, LGPL-3.0, v0.3.2;[58] archinstall aktiv, GPL-3.0, v4.5;[57] Planify aktiv, GPL-3.0, v4.20;[59] Omarchy aktiv, MIT, v4.0.6.[55]

## 1. Faktisk implementasjon i dag (kategori 1)

Basert på direkte kildelesning av `config/`, `runtime/`, `bin/` og `installer/` ved `219894f`:[52]

| Komponent | Faktisk status |
| --- | --- |
| Base OS / oppstart | Arch + systemd-boot + greetd/tuigreet; guarded archinstall 4.5-adapter med blank-disk/identitetsporter; ISO-bygg via Archiso 91-materialisering (`docs/installer-runtime.md`).[52] |
| Compositor-config | DMS genererer `hyprland.lua`; Wilsof legger én markert `require("wilsof")`-rad; `wilsof.lua` eier gaps/border/rounding/binds (9 arbeidsområder, piler, launcher/lås/innstillinger/hjelp); en legacy `wilsof.conf` finnes fortsatt (dobbeltkilde, se §11). |
| Shell | DMS 2.0 (`dms.service` som user-unit + Wilsof-dropin: TimeoutStartSec=300, DMS_DISABLE_MATUGEN=1); settings-mal seeds én gang (bar: workspaceSwitcher/clock/tray+battery+controlCenterButton); Wilsof-temafil `wilsof-theme.json`. |
| Launcher | `wilsof-search toggle` → `dms ipc call spotlight toggle` (argumentvalidert bro; app-fokus). |
| Hjelp | `wilsof-help`/`wilsof-help-view` renderer `wilsof-shortcuts.json` til DMS Notepad-IPC. |
| Lås/idle | `wilsof-lock`-wrapper (én instans), `hyprlock.conf` (WS-profil), `hypridle.conf` (5 min + before-sleep), patchet hypridle-0.1.8-2.1 pakke med pinnet SHA256. |
| Bakgrunn | `wilsof-wallpaper.service` (oneshot, Requires=dms) + `wilsof-apply-wallpaper` (venter på DMS IPC-bekreftelse `SUCCESS: Wallpaper set to …`). |
| Konfig-distribusjon | `runtime/desktop.py` (offline, home-confined, per-fil backups, bevarer personlig DMS settings.json, Dux 2-migrering `.config/DankMaterialShell`→`dms`), `wilsof-config-update`-wrapper, `scripts/install-user-config.sh` (VM-mål). |
| Oppdatering | `wilsof-config-update` (kun Wilsof-filer, som bruker, aldri root); ingen systemoppdateringsflate aktivert i Wilsof i dag (DMS 2.0 har innebygd sysupdate-UI/bakende, se §4). |
| Tester | 201 passed/1 skipped ved kilde-CI for `f7c3945`;[53] suite dekker hypr-config, help, installer, ISO-materie, live-recovery m.fl. |
| Kvalitetsstatus | internal2: alle 13 VM-porter bestått med R1–R5-merknader (DMS-kaldstart-SIGKILL, hyprland-dialog-krasj, live gvfsd-fuse-krasj, Tracker-varsel, wallpaper-avhengighetsfeil); ingen fysisk verifikasjon; PR #27 OPEN/DRAFT; #34/#16 åpne.[53] |

## 2. Støttet av eksisterende avhengigheter, men ikke konfigurert (kategori 2)

1. **Quick Settings-tiles i Control Center:** DMS 2.0 har ferdige nettverks-/Bluetooth-/lyd-/lysstyrke-/batteri-/strøm-flater;[3] Wilsof har ikke aktivert dem som kuratert standard utover malens tre widgets.
2. **Systemoppdateringsflate:** DMS 2.0 sysupdate-modul + `dms system update --check/--json` + Shell-UI med reboot-anbefaling ved kernel-oppdatering;[48] Wilsof har ikke aktivert/curatert den (ingen Wilsof-opplevelse definert, ingen verifisert test i målet).
3. **Launcher-plugins:** plugin-API (`getItems`/`executeItem`, triggere, settings, persistens via pluginService) er dokumentert;[2][50] Wilsof har ingen profil-/systemhandlings-plugin i dag.
4. **Bar-widget-plugins:** `PluginComponent` med pills/popouts/CC-integrasjon;[3] Wilsof har ingen profilwidget.
5. **Fil/vindu/settings-søk i Spotlight:** upstream-støtte finnes, men `dsearch`-avhengigheten er ikke installert/pinnet og universell søke-aksept er eksplisitt ikke-oppnådd ( beholdes som ikke-påstand).[52]
6. **Workspaces minimum count / indikatorstiler:** DMS 2.0-funksjoner (release notes)[54] kan konfigureres, ucuratert i Wilsof.

## 3. Kan bygges som et lite tillegg (kategori 3)

1. **Profiltilstand** (`wilsof-profile set/get`): ~100 linjer Python/POSIX-sh med JSON-fil i `~/.local/state/wilsof-os/profile.json` + launcher-/bar-plugin som presenterer den. Ingen DMS-fork, ingen daemon.
2. **Dashboard/Kanban (Wilsof Tasks):** én egen desktop-app (se §6) — det eneste vesentlige egne byggjektet.
3. **Launcherelementer** for hurtigtaster/innstillinger/systemhandlinger: ren QML-plugin-konfig.
4. **Restore-kommando for Wilsof-filer** (`wilsof-restore`, se §8): gjenbruk av eksisterende backup-struktur fra `runtime/desktop.py`/`install-user-config.sh` med manifest og forhåndsvisning.
5. **Modal-dialog-vindusregel** i `wilsof.lua` (én `hl.window_rule` med `match = { modal = true }`, `float`, `center`).[45]
6. **Wallpaper-utholdenhet:** `Restart=on-failure` + `After=dms.service`-retry-semantikk (se §9).

## 4. Krever større utvikling/vedlikehold (kategori 4) — unngås i MVP

1. **Egen bar/shell/kontrollsentertjeneste:** DMS dekker alt (gjenbrukes; kategori 2). Ingen egen tjeneste bygges.
2. **Universell filsøk med dsearch:** supply-chain- og personvernvurdering (lokalt HTTP-API uten per-user auth er dokumentert i eksisterende research) utsetter dette;[52] ikke del av produkt-MVP.
3. **Snapshots/rollback:** Wilsofs kontrakt er ext4/systemd-boot;[52] Omarchy-type snapshot er Limine/Btrfs-bundet og kan ikke implementeres verifiserbart her uten nytt filsystem/bootløp — et større underspor som ikke inngår (jf. ingen-rollback-kravet).
4. **Universal search/»command platform»:** eksplisitt produktnektelse.
5. **AI-integrasjon/synk/kalender:** eksplisitt første-versjonsnektelse.

## 5. Komponentanalyse (per Engineering Standards §2–§8-format)[51]

### 5.1 Profiltjeneste (wilsof-profile)

- **Problem:** Fire arbeidsflyter trenger et valgbart oppsett uten flere brukerkontoer.
- **Finnes:** Plasma Activities ligner (men binder KDE-shell); Hyprland/DMS har ingen profilbegrep. Ikke behovsdekket i denne stacken.
- **Løsning:** Egen liten tilstandsløs CLI + JSON-fil; launcher-plugin og bar-widget leser samme fil. Én kilde til sannhet.
- **Avhengigheter:** kun kjerneverktøy; ingen.
- **Kompleksitet:** lav (~1–2 dager inkl. tester).
- **Drift:** ingen bakgrunnsprosess; fil formatter/versjon felt (schema v1) med fallback til CLEAN.
- **Sikkerhet/feil:** ugyldig fil → lesbar feil + CLEAN-fallback; ingen privilegier; confine innen `~/.local/state/wilsof-os/`.
- **Lisens:** egen GPL-vennlig; ingen ny avhengighet. (Merk: repo mangler prosjektlisens — Engineering Standards krever lisensavklaring før offentlig distribusjon;[51] følges opp som eierbeslutning.)
- **Test:** enhet på filparser (gyldig/ugyldig/tom/fraværende), launcher-plugin-elementer, bar-visning; VM-port M2.
- **Akseptanse:** bytter oppdaterer topbar ≤2 s; CLEAN-fallback ved korrupt fil; ingen vinduslukking (M2-matrise).

### 5.2 Wilsof Tasks (dashboard/Kanban)

- **Problem:** STUDY/DEV/EVERYDAY trenger lokal oppgavehåndtering med Kanban og prosjekttilknytning, offline uten konto.
- **Finnes:** Planify (GPL-3, GTK4/libadwaita, SQLite, lokal + Todoist/Nextcloud-synk)[26][59] dekker liste-/prosjektbehov godt, men er en fullverdig GTD-app med sky-integrasjonstendens, GTK/libadwaita-ikonsistens med Charcoal, tung avhengighetskjede (webkitgtk, libsecret, libecal...) og uklar Kanban-først-fokus;[26] DMS-plugin-flaten (dash-tab/dashCard) kunne huse den,[50] men binder oppgavedata til shell-prosessens livssyklus — bryter kravet om at dashboardet kan feile selvstendig. **Derfor egen lett app.**
- **Løsning:** én Python-app — **PySide6/Qt Widgets** — pakket for Arch, DB i **SQLite** (public domain)[24] med WAL, stdlib `sqlite3`. Arkitekturvalg begrunnelse:
  - *Vanlig desktopapp fremfor DMS-komponent:* uavhengig prosesslevetid = feilisolert fra shell/innlogging (krav); enkel testbarhet uten Wayland.
  - *Qt/PySide6 fremfor GTK:* visuelt konsistent med DMS (samme Qt6/Wayland-stak allerede i pakkesettet),[53] LGPLv3/GPL-kompatibel;[20][21] Python+PySide6 gir lavest vedlikeholdskost for liten organisasjon.
  - *SQLite fremfor JSON-filer:* transaksjoner/atomic commits ved flyttinger,[23] ett-fil-backup, `VACUUM INTO` for konsistent kopi;[22] JSON-eksport lagt ved sidenav.
- **Avhengigheter:** `python-pyside6` (offisiell Arch-repo-pakke), python stdlib. Ingen nye rammeverk.
- **Kompleksitet:** middels (~1–2 uker for MVP med tester).
- **Drift:** ingen bakgrunnstjeneste; starter kun on-demand fra launcher/dashboard; autostart finnes ikke.
- **Sikkerhet/feil:** ren user-prosess; DB-beskyttelse via `BEGIN IMMEDIATE`-skriving og versionsfelt; krasj mister høyest siste transaksjon; appen kan SIGKILLes uten sideeffekter utover eget vindu.
- **Lisens:** PySide6 LGPLv3,[21] SQLite public domain,[24] Wilsof-kode antas GPL-3.0 når prosjektlisensen er avklart.
- **Test:** unit på lager/SQL-migreringer; integrasjon på DB-opprettelse/eksport; VM-port M4 (start/flytt/fullfør/avslutt/krasj).
- **Akseptanse (M4):** opprett/endre/flytt/fullføre oppgaver i alle tre moduser; data overlever app-krasj og profilbytte; eksport gir komplett JSON; SIGKILL av appen endrer ikke Hyprland/bar/innlogging.

### 5.3 Profil-bar-widget + launcher-plugin (DMS-plugins)

- **Problem:** synlighet av profil (bar) og valgflate (launcher).
- **Finnes:** DMS-plugin-API for både widget og launcher;[2][3][50] ingen eksisterende "Wilsof-profil"-plugin.
- **Løsning:** to små QML-plugins levert i `~/.config/dms/plugins/` via `runtime/desktop.py` (samme distribusjonsvei som øvrig Wilsof-materiale).[52]
- **Avhengigheter:** ingen ut over DMS (allerede i pakkesett).
- **Kompleksitet:** lav-middels (QML-ytringer, ikke apper) (~2–3 dager).
- **Drift:** følger DMS-oppdateringer; plugin-API er dokumentert og versjonert;[50] lav risiko.
- **Sikkerhet/feil:** plugin-feil påvirker kun egen widget (DMS isolerer); ingen datautoverflate utover lesing av profilfil.
- **Lisens:** QML-kode i egen plugin; DMS MIT.[54]
- **Test:** manifest-validering; manuell VM-inspeksjon av bar/launcher (fysisk tastatur Es/Enter-verifisering følger CONTRIBUTING-mønsteret[52] og merkes uverifisert i VM).
- **Akseptanse:** profilnavn synlig og klikbart; launcher viser 4 profiler + kuraterte handlinger; tastaturnavigasjon fungerer.

## 6. Dashboardarkitektur — endelig anbefaling

**Anbefaling: vanlig desktopapplikasjon (Python + PySide6 + SQLite), ikke DMS-komponent, ikke web-app.**

Begrunnelse (sammenfattet fra §5.2 og §5.3): DMS-plugin ville arvet shell-prosessens krasjprofil (internal2 viste DMS-SIGKILL/krasj hendelser R1/R2)[53] og da konflikt med "dashboard må kunne feile uten å påvirke Hyprland/shell"; GTK-apper trekker inn en annen stak og designmotor; Planify dekker ikke Kanban-først og trekker med 10+ ekstra biblioteker.[26][59] Qt/Python er allerede plattformens språk for skriptlaget (runtime/desktop.py), gir LGPL-kompatibel,[20][21] lavthyrig løsning en liten utvikler kan holde ved like, og eksisterende CI (pytest) tester slike komponenter direkte.

## 7. Datalagring, migrering og gjenoppretting (dashboard)

- Plassering: `~/.local/share/wilsof-os/dashboard/tasks.db` (SQLite, WAL) + `export/` for JSON-eksport.
- Skjema versjoneres (`PRAGMA user_version`); migrering er additive kolonner/tables i én transaksjon;[23] ukjent høyere versjon → app nekter skriving med lesbar feil (ingen silent downgrade).
- Eksport: "Eksporter JSON" skriver komplette data (prosjekter+oppgaver+metadata) til valgt fil via filvelger; bekreft/overskriv-dialog.
- Sikkerhetskopi: `VACUUM INTO`-kopi (konsistent snapshot)[22] til `~/.local/state/wilsof-os/backups/dashboard/` ved appstart hvis DB endret siden siste kopi (maks 7 roterende).
- Gjenoppretting: dokumentert prosedyre — stopp app, bytt fil, start app; verifisert som del av M4.
- Ingen behandling av personlige filer utenfor de valgte prosjektreferansene (kun banestrenger i DB; ingen lesing av filinnhold).

## 8. Oppdateringer og stabilitet

### 8.1 Systemoppdateringer — gjenbruk DMS 2.0 sysupdate, kuratert

- **Oppdagelse:** DMS sysupdate poller med konfigurerbart intervall og viser tilgjengelige oppdateringer; `pacman`-bakenden bruker `checkupdates` (pacman-contrib, GPL-2.0+)[18] med fakeroot-/`pacman -Qu`-fallback.[32] Wilsof legger `pacman-contrib` til pakkesettet og beholder poll-intervall conservativt (standard fra DMS; ingen egen oppdagelseskode).
- **Presentasjon:** DMS System Updater-UI (bar-widget/SystemUpdate + Settings-side) viser liste og antall;[54] Wilsof kuraterer synligheten i topbar via settings, ikke egen widget.
- **Utførelse:** brukerstarter via UI; bakenden kjører privilegert `pacman -Syu --needed` (kun full synkronisert oppgradering; `systemHoldsAllowed=false` for pacman-familien hindrer delvis repo-hold),[32][6] med sudo/doas/run0-deteksjon,[48] eller terminal-flyt for AUR-hjelpere (Wilsof installerer ingen AUR-hjelper → plain pacman, offisielle repoer kun, iht. eksisterende leverandørpolitikk).[52]
- **Autentisering:** DMS bruker sudo/doas/run0/pkexec etter deteksjon;[33][48] avbrutt autentisering (pkexec 126) håndteres som eksplisitt avbrudd, ikke suksess.[33]
- **Nettverksfeil/avbrudd:** check-steg har kort timeout, upgrade-steg lang timeout;[48] midt i en avbrutt `pacman -Syu` er tilstanden delvis — Wilsof/UI kommuniserer at omstart av kommandoen er trygg neste steg, og at partiell oppgradering aldri tilbys (Arch-vedlikeholdspraksis: aldri delvis oppgradering).[43]
- **Omstartsbehov:** DMS rapporterer reboot-anbefaling ved kernel-oppdateringer;[54][34] UI tilbyr omstart med eksplisitt bekreftelse.
- **Ingen egen pakkebeholder bygges.** `--ignore`-listen (settings) ekskluderer kun pakker som ikke inngår i repo-transaksjonen (dropPacmanRepoIgnores sikrer at repo-pakker allikevel oppgraderes sammen — delvis oppgradering forhindret).[32]

### 8.2 Wilsof-konfig-oppdatering (eksisterende, beholdes skilt)

`wilsof-config-update` forblir separat fra systemoppdatering, kjører som bruker, tar per-fil backup og bevarer personlige innstillinger (eksisterende kontrakt, uendret).[52] Issue #30 (Dux 2 settings-migrering i bundlet oppdaterer) er fortsatt åpen og inngår ikke her.

### 8.3 Restore-funksjon for Wilsof-eide filer (nytt lite tillegg)

- **Problem:** dagens installasjon tar backups men har ingen restore-kommando (dokumentert quality-audit-funn).[52]
- **Løsning:** `wilsof-restore [--list|--preview|--apply]`: lister innholdet i en valgt backupmappe (`~/.local/state/wilsof-os/backups/<timestamp>/`), viser diff mot nåværende filer (forhåndsvisning), og kopierer tilbake **kun Wilsof-eide stier** (samme manifest som `install-user-config.sh`/`desktop.py`) etter eksplisitt bekreftelse per fil eller --all.
- **Grenser:** berører aldri personlige DMS-settings, aldri brukerfiler, ingen transaksjonell rollback-påstand (filgjenoppretting dokumenteres som manuell gjenoppretting av filer, jf. Engineering Standards gjenopprettingsregler).[51]
- **Test:** enhetstester på mappevalg/diff/prompt; negativtest av stier utenfor manifest; VM-port M6.
- **Akseptanse:** backup fra tidspunkt T kan gjenopprettes med forhåndsvisning; nektede stier avvises; ingen suksess-påstand ved delvis feil.

## 9. Wallpaper-utholdenhet (internal2-funn R5)

- **Faktisk årsak (journalbevis):** `wilsof-wallpaper.service` (oneshot, `Requires=dms.service`) fikk `Job ... failed with result 'dependency'` da første DMS-UI ble SIGKILLet; ingen retry skjedde, og DMS sin friske session viste upstream standard.[53]
- **Planlagt utbedring (M5, ikke utført nå):** legge til `Restart=on-failure` + begrenset `RestartSec`/`StartLimit` i wallpaper-unitten, og/eller la DMS-tilkoblingen retry-bekrefte; `wilsof-apply-wallpaper` gjenbrukes uendret (den allerede validerer IPC-svar). En eventuell `ExecCondition`-beholdelse dokumenteres i enheten.
- **Akseptanse (M5):** etter simulert DMS-restart (systemctl --user restart dms) vises godkjent asset; `dms ipc call wallpaper get` returnerer samme sti i alle profiler; ingen manuell kommando trengs ved innlogging.
- Ingen ISO-endring inngår i dette dokumentet.

## 10. Andre arkitekturvalg (samlende)

- **Binds/tilstand:** `wilsof.lua` forblir bind-kilde; legacy `wilsof.conf` skal avvikles som del av M3 (én kilde, Engineering Standards §3),[51] med migreringsnote i brukerdok.
- **Internasjonalisering:** DMS har egne engelske labels; Wilsof-faser (hjelp, dashboard, profilnavn) er norsk-first uten DMS-fork (eksisterende praksis beholdes).[52]
- **CI:** eksisterende `validate.yml`-sjekker (pytest, json.tool, ShellCheck, git diff --check) utvides med nye testfiler; ingen ny CI-stack.[52]

## 11. Risiko- og eierskapsliste (sammendrag)

| Risiko | Sannsynlighet | Konsekvens | Mitigering |
| --- | --- | --- | --- |
| DMS 2.0 plugin-API-endringer bryter Wilsof-plugins | middels | lav-middels (visningsflate) | plugins holdes små; versjonspinn i pakkesettet; manuell VM-port per bygg |
| Profilbytte-tilstandsfeil | lav | middels | schema-versjon, CLEAN-fallback, M2-port |
| Dashboard-bug ødelegger data | lav | middels | SQLite-transaksjoner,[23] roterende VACUUM INTO-backups,[22] M4-port |
| Oppdateringsflow-endring oppstrøm (DMS sysupdate) | middels | middels | konfigurasjonsnivå snarere enn kode; `--check --json`-kontrakttest[48] |
| Låse/idle-regresjon | lav | høy | eksisterende hypridle-regresjonssuite gjenbrukes; fysisk port kreves (human-check)[52] |
| Manglende prosjektlisens blokkerer distribusjon | sikker | middels | eksplisitt eierbeslutning før release (Engineering Standards §8)[51] |
| internal2-runtime-merknader R1/R2 (DMS/Toolkit-krasj) forblir uforklart | middels | middels | forblir åpent på integrasjonsspoer; ingen produktfunksjon avhenger av å "fikse" dem i MVP |

## Sources

- [2] https://raw.githubusercontent.com/duxlabs-dev/dux-shell/v2.0.0/.agents/skills/dms-plugin-dev/references/launcher-plugin-guide.md
- [3] https://raw.githubusercontent.com/duxlabs-dev/dux-shell/v2.0.0/.agents/skills/dms-plugin-dev/references/widget-plugin-guide.md
- [6] https://raw.githubusercontent.com/duxlabs-dev/dux-shell/v2.0.0/quickshell/Services/SystemUpdateService.qml
- [18] https://man.archlinux.org/man/checkupdates.8.en
- [20] https://doc.qt.io/qt-6/licensing.html
- [21] https://doc.qt.io/qtforpython-6/licenses.html
- [22] https://sqlite.org/backup.html
- [23] https://sqlite.org/lang_transaction.html
- [24] https://sqlite.org/copyright.html
- [26] https://raw.githubusercontent.com/alainm23/planify/master/README.md
- [32] https://raw.githubusercontent.com/duxlabs-dev/dux-shell/v2.0.0/core/internal/server/sysupdate/backend_pacman.go
- [33] https://raw.githubusercontent.com/duxlabs-dev/dux-shell/v2.0.0/core/internal/server/sysupdate/executor.go
- [34] https://raw.githubusercontent.com/duxlabs-dev/dux-shell/v2.0.0/core/internal/server/sysupdate/reboot.go
- [43] https://wiki.archlinux.org/title/System_maintenance
- [45] https://raw.githubusercontent.com/hyprwm/hyprland-wiki/e9b1f8f56bc1e74d3f4d8cb64b55147152658fe2/content/configuring/core/rules/window-rules.md
- [48] https://raw.githubusercontent.com/duxlabs-dev/dux-docs/6bf44c0c03bd4c3a917abeaa6b366fda741c2f76/versioned_docs/version-2.0/dms/cli-system-updater.mdx
- [50] https://raw.githubusercontent.com/duxlabs-dev/dux-docs/6bf44c0c03bd4c3a917abeaa6b366fda741c2f76/versioned_docs/version-2.0/dms/plugin-development.mdx
- [51] https://github.com/tomli0/wilsof-os/blob/a78d88790754886750bb1a5f93dd33cb257cc47e/docs/ENGINEERING_STANDARDS.md
- [52] https://github.com/tomli0/wilsof-os/tree/219894f1d4fc365b5e6546c2af9a146141634a1c
- [53] https://github.com/tomli0/wilsof-os/blob/219894f1d4fc365b5e6546c2af9a146141634a1c/docs/development-reports/2026-10-28-internal2-acceptance.md
- [54] https://github.com/duxlabs-dev/dux-shell/releases/tag/v2.0.0
- [55] https://github.com/omacom/omarchy/releases/tag/v4.0.6
- [56] https://github.com/hyprwm/Hyprland/releases/tag/v0.57.0
- [57] https://github.com/archlinux/archinstall/releases/tag/4.5
- [58] https://github.com/quickshell-mirror/quickshell/releases/tag/v0.3.2
- [59] https://github.com/alainm23/planify/releases/tag/v4.20.0
