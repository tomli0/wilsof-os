# Wilsof OS — internal4-stabilisering og fysisk QA, 2026-10-30

Status: **kildekandidat levert som draft; kontrollert stopp før internal4-ISO**. Wi-Fi-/lydårsaken på fysisk PC er ikke fastslått. Fysisk godkjenning **PENDING**. Ny sesjons-/provisioneringskjede mangler uavhengig gjennomgang, og ny profilvelgers tastaturnavigasjon er ikke akseptert. Ingen merge/release.

Utvikling/nykontroll UTC: 21:41–22:34; publiseringskvittering følger i #16 og privat kontrollpunkt.
Gren: `stabilization/internal4-20261030`. Draft [#42](https://github.com/tomli0/wilsof-os/pull/42), base uendret `integration/internal3-20261030` @ `4112e45998430c50711a2e51e9e7ba26f97e5b4d`.

## Bevisgrunnlag og avgrensning

- Lest: Engineering Standards, CONTRIBUTING, produktvisjon/UX/arkitektur/roadmap, sikkerhetsgrenser, rapporteringsstandard, intern testrunbook, internal3-rapporter/kontrollpunkter og bevarte journaler. GitHub #16/#27/#31/#38/#39/#40/#41, kommentarer, faktiske heads og CI kontrollert. Eldre NO-GO i #16/#41-kroppene var supersedert av E2-sluttkommentaren og rapporten ved `4112e459…`; ingen ny installasjon ble startet på grunnlag av den foreldede teksten.
- Historisk direkte bevis: internal3 faktisk ISO/installasjon/disk-only-aksept, med R1/R2-merknader. Første fysiske USB-observasjoner er eierens oppgitte resultater, ikke nye agentmålinger: UEFI, splash, desktop/DMS, Super+Space, CLEAN/STUDY, bar, batteri, kontrollsenter og bakgrunner visuelt godkjent. Wi-Fi og avspilling feilet; Bluetooth-adapter ukjent.
- Nytt: immutable SquashFS-pakkedatabase/enheter og innebygd DMS-QML inspisert uten å endre bildet; seks ISO-hasher kontrollert før og etter. Én disponibel COW-gjest over den bevarte installerte internal3-disken, aldri ny/parallel fysisk eller virtuell installasjon.
- Ingen fysisk disk/USB, Proxmox, main-/leveransegrenendring, vendorpatch, M3/M4/dashboard/Kanban, scheduler/worker, betalt reviewer eller automatisk videreføring. Private VM-disker, syntetisk passord og rålogger er ikke publisert.

## 1. Fullførte milepæler

### P0 — nettverk og lyd

Live-image har NetworkManager **1.58.1-2**, wpa_supplicant **2:2.12-1**, linux-firmware **20260916-1** med leverandørfamilier, SOF **2026.09.2-1**, ALSA/UCM, PipeWire/audio/Pulse **1:1.6.10-1**, WirePlumber **0.5.18-1**. NM-enablement, PipeWire/Pulse-sockets og WirePlumber-lenke finnes. Dermed er en generell påstand om manglende Wi-Fi-/lydstakk avkreftet for ISO-en, men ikke en bestemt fysisk modul-/firmware-/rfkill-/routingfeil.

Det faktiske installerte internal3-målet mangler `sof-firmware`, som live har. Minste generiske rettelse er eksplisitt SOF i desktop-manifestet, konsumert av både image og installasjonsplan. Pakken er bekreftet i brukt pakkedatabase, uten avhengigheter. Ingen chipsetspesifikk driver eller pakketransaksjon er gjettet/kjørt. **Dette forklarer ikke lydfeilen i eierens live-test.** Ny installasjon med pakken er ikke kjørt.

`bin/wilsof-hardware-report` er levert, testet og kjørt både på vert som smoke og som ordinær QA-bruker i gjesten. Skriptet bruker bare avgrensede read-only API-/statusforespørsler, gjør ingen nedlasting/konfigurasjon/opplasting, og sender JSON til stdout. Det inkluderer numeriske PCI/USB-ID-er, driver, rfkill, pakker/tjenester, anonymisert sink/source/default/mute/volum og filtrerte kernel-feiltellinger/manglende firmwarefiler. Ingen SSID/MAC/IP, nøkler, passord, mediatitler, streams, personlige filer eller råjournal deles. Utilgjengelig/tom/tilgangsbegrenset kerneljournal merkes `unavailable`, ikke «ingen feil». Vanlige lydstatusforespørsler kan socket-aktivere eksisterende brukertjenester; ingen policy endres.

VM-proben fant virtuell Ethernet aktiv og HDA-standard-sink med mute=false/40 %, ikke fysisk lydavspilling eller Wi-Fi. `bluez-libs` finnes, men `bluez`-daemon/tjeneste mangler. «No adapters» kan derfor ikke bevise fravær av fysisk adapter. Ingen BT-driver/tjenestepolicy endret. [Fysisk diagnose- og retestplan](../qa/2026-10-30-internal4-physical-plan.md).

### P1 — oppstart

Rotårsak er kilde- og pakkebevis: begge gjeldende greetd-konfigurasjoner startet `Hyprland` direkte; Hyprland **0.57.0-1** sin pakkede Wayland-session bruker `/usr/bin/start-hyprland`. Watchdog-kilden oppretter `--watchdog-fd` og eier compositor-barnet. Ingen advarselsvariabel skjules.

Én root-eid `wilsof-session` brukes nå fra live-autologin og installert tuigreet. Normal stdout/stderr føres med `systemd-cat` til `wilsof-session`-journalen, ikke `/dev/null`; diagnose-entry/`--diagnostics` beholder synlig output. Greetd/PAM og DMS-generert systemd-brukerøkt beholdes. Plymouth-design og normal UEFI-entry er uendret. Ny privilegert målfil har eksplisitt symlinknekt og Archiso-eierskap/modus.

Faktisk vanlig greeterinnlogging i COW-gjesten: PAM åpnet QA-brukerens økt; `start-hyprland` → `Hyprland --watchdog-fd 4`; journaloutput tilgjengelig; ferdig rendret desktop uten start-advarsel eller konsolltekst. En forutgående tom/feil autentisering ble avvist; den er ikke kalt en planlagt passordtest. Live-autologin er materialiserings-/regresjonstestet, **ikke** bootet fra et nytt image.

### P2 — små DMS-/UX-valg

- DMS 2.0s faktiske innebygde `ChangelogService.qml` bruker `.config/dms/.changelog-2.0`. Bare nye Wilsof-desktopbrukere får denne eksisterende release-line-kvitteringen. Ingen global/oppdiktet disable-setting, vendorendring eller undertrykking av fremtidige versjoners nyheter. Eksisterende personlige settings/markører bevares. Ny bruker fikk rendret desktop uten automatisk What's New.
- Standard `Fit`, bekreftet via faktisk DMS-IPC. Stor eksisterende logo er **2172×724 (3:1)**; `Fill` er upstream-standard/PreserveAspectCrop og gir sidebeskjæring på de nevnte skjermformatene. `Fit` bruker proporsjonal sentrering; originale assets er byte-uendrede. Statisk projeksjon for 16:9/16:10/3:2 består; 1280×800/16:10 viser de brede ytterkantene uten skjermkant-crop, men Power-panelet dekker midten. Andre to formaters render/fysisk aksept gjenstår. Ingen ny logo/redesign.
- Støttede mode-chips og alfabetisk tom appoversikt, ikke ny søkemotor. Upstreams relevante/fuzzy søk beholdes. Bare qv4l2/qvidcap får standard `NoDisplay`-brukeroverstyring; binærer/systemverktøy slettes ikke. Faktisk all-app-kategoriflyt/hiding i GUI er ikke fullakseptert.
- Første kandidat lot `profil` konkurrere med Firefox Profile Manager og QR. Den faktiske renderingen påviste dette. Endelig minste rettelse bruker DMSs støttede trigger **`profil`**, ikke Wilsof-filtrering av global søkestrøm. Baren åpner samme query; `profil study` filtrerer innen egen profilmodus. Frisk shell lastet triggeren og viste **kun CLEAN/STUDY/DEV/EVERYDAY**, uten app/QR/settings. Manifestendring krevde frisk shell; `plugins reload` alene oppdaterte ikke den gamle katalogtilstanden.
- Power-standard er `lock,suspend,logout,reboot,poweroff`. Reell visning viser de fem valgene og eksisterende **Hold to confirm (500 ms)**. Avanserte funksjoner/binaries/settings er ikke fjernet; ingen power-handling ble utløst.

## 2. Claude QA-funn og utbedringer

Ingen ny uavhengig Claude-/annen agentreview. Egen gjennomgang er ikke uavhengig review; ingen ekstra worker/agent eller betalt review startet.

| Funn | Bevis/status | Rettelse/gjenstår |
| --- | --- | --- |
| Direkte Hyprland-start | Bekreftet kilde og pakket session | Delt watchdog-wrapper, faktisk passordøkt testet |
| Installert SOF-asymmetri | ISO har pakken, installert mål mangler | Manifestrettelse; ny installasjon gjenstår |
| Globalt konkurrerende profiler | Faktisk første søk viste Firefox/QR over profilene | Støttet trigger; frisk shell viser fire isolerte rader |
| Kerneljournal uten tilgang kunne se ren ut | Negativ test | `unavailable`, ingen falsk nullfeil |
| Ny selector-keyboard | Syntetisk Down/Enter lukket selector, men beholdt CLEAN; ønsket STUDY ikke bekreftet | **Ikke bestått**, ingen spekulativ keybinding-/vendorpatch; fysisk/fokus-/timingoppfølging |

## 3. Kodekvalitet og sikkerhetsstatus

Faktisk RED før diagnostics, startup-routing, defaultvalg, profiltrigger, journaltilgang og ny session-symlinknekt; GREEN etter avgrensede rettelser. Full siste suite: **326 passed / 2 eksplisitte opt-in-skips**, null feil. ShellCheck for sh/bash, JSON, `git diff --check` og reell offline materialisering består. Første lokale system-Python manglet jsonschema; separat QA-venv med repoets requirements ble brukt. En automatisk Hermes/anyio pytest-plugin ga miljøvarsel ved én kjøring; ren kjøring uten plugin-autoload/PYTHONPATH ga 326/2 uten varsel. QML `.pragma library` er forventet og testes gjennom Node-harness som fjerner kun pragma, ikke som vanlig Node-modul.

Ingen endring av diskvalidering, ERASE, passord/PAM-policy, signaturer eller CheckSpace. Ingen installasjon på original QA-disk: eksakt originaldisk/firmware hashlike etter gjesten; disponibel COW offline check exit 0. Ny system-session/provisionering er review-pliktig: **uavhengig gjennomgang mangler**, derfor ingen ISO-bygg/godkjenningspåstand.

Endrede filer i kildekandidaten (21, fjernblob-identitet verifisert):

- `.github/workflows/validate.yml`
- `bin/wilsof-hardware-report`, `bin/wilsof-session`
- `config/dms/plugins/wilsofProfiles/{Launcher.qml,Profiles.js,plugin.json}`
- `config/dms/settings-template.json`, `iso/profiledef.sh`
- `runtime/{desktop-packages.txt,desktop.py,image-files.txt,provision-target}`
- `scripts/{boot-profile.py,prepare-iso.py}`
- `tests/{test_chroot_contract.py,test_desktop_runtime.py,test_hardware_diagnostics.py,test_profile_plugin.py,test_session_start.py,test_stabilization_defaults.py}`
- `docs/qa/2026-10-30-internal4-physical-plan.md`

Denne rapporten og sluttkontrollpunktet kommer i en separat docs-commit; de endrer ikke testede runtime-bytes.

## 4. Commits og CI-status

| Commit | Rolle | Eksakt CI |
| --- | --- | --- |
| `4112e45998430c50711a2e51e9e7ba26f97e5b4d` | Uendret internal3-base/rapport | Tidligere aksept beholdt, ikke ny test |
| `79fcb2e2fb087058df03cbd487a19095cbdbe730` | Første session/diagnostics/default-kandidat | Push 41135939034 og PR 41136397209 success; profilfiltrering senere forbedret |
| `5f19e69c3cb98927dd13924ea9b6fd7a6e4946d2` | Endelig kilde: trigger, SOF og journaltilgang | [Push](https://github.com/tomli0/wilsof-os/actions/runs/41137560781), [PR](https://github.com/tomli0/wilsof-os/actions/runs/41137566959) completed/success på eksakt head; logg 326/2 |

Alle 41 payload-filer i QA-kilden er hashidentiske med endelig commit. Dette er en lokalt anvendt kilde over internal3, ikke endret immutable systembundle/ISO. Alle 15 opprinnelige remote-heads er uendret; ny gren/draft #42 alene. CI-filtre utvidet kun for denne push-grenen og dens internal3-PR-base; read-only CI-token uendret. Rapport-head/ny CI leses tilbake i sluttkvitteringen, ikke selvrefererende omskriving av denne commit-en.

## 5. ISO-filnavn, størrelse, SHA256 og plassering

**Internal4: ikke bygget. Null byggforsøk/null ombygginger.** Uavhengig session/provisioneringsreview og profilvelgerens nye tastaturaksept mangler; ingen kostbar bygg-/installasjonsrunde startet for å omgå portene.

Siste bevarte leveranse er fortsatt `wilsof-internal-2026.10.30-internal3-x86_64.iso`, kilde `448e0190e786475f083abdce223b3b24dc2a85ef`, **2548035584 byte**, SHA256 **`b3cf9726f2d55a7a0398aadeb6327a839a5607a7dd7f5a10b9a862a5c1936dd1`**. Privat artefaktrot: `internal-test-20261030-internal3/`, med eksisterende manifest/SHA256SUMS. Alle seks eksisterende ISO-er hashuendrede før/etter; ingen sletting/overskriving. Ingen oppdiktet internal4-fil/hash.

## 6. Resultat fra full installasjon

| Port | Denne økten |
| --- | --- |
| Ny immutable internal4-audit/UEFI-live-boot | **Ikke utført; ingen ISO** |
| Ny blank disk / faktisk installer / målverifikasjon | **Ikke utført** |
| Ny internal4 disk-only boot | **Ikke utført** |
| Internal3-basert COW disk-only UEFI | Utført, én gjest; ikke ny-ISO-bevis |
| Ordinær passordinnlogging i endret session-wrapper | Bestått med syntetisk tastatur/PAM-prosessbevis |
| DMS-kaldstart + én bevisst restart | Aktiv, NRestarts=0 ved måling; ingen automatisk restart likestilles med den bevisste |
| Profiler | Alle fire satt/GUI-ack via eksisterende hjelper; fire isolerte rader visuelt; selector Down/Enter ikke akseptert |
| Power/wallpaper | Støttet innstilling + faktisk visning; ingen power-action; kun én faktisk skjermgeometri |
| Ny lock/unlock / suspend / full app- og klientbevaring | **Ikke kjørt**; eldre internal3-aksept overføres ikke |
| Avslutning | QEMU exit 0, offline overlay check 0; original disk/firmware hashlike |

Lagring **2026-10-30T22:34:28Z**: **89143566336 byte = 83.02141571044921875 GiB** tilgjengelig. Ikke en lagringsblokkering. Bevarte logger/artefakter ble ikke ryddet.

## 7. Oppstart og passordinnlogging

Kun den lokale kilde-QA-øktens vanlige greetd/PAM-innlogging er ny dokumentasjon. `start-hyprland` og faktisk watchdog-fd-barn er observert. Systemd bruker-session er bevart; DMS READY/aktiv og grafisk desktop er separat observert. Root/runuser ble brukt til oppsett av en privat syntetisk konto, **ikke** som autentiseringsbevis. ISO-live-autologin, ny installasjon, ny lås/opplåsing og fysisk klient er fortsatt separate porter.

## 8. Gjenstående feil og begrensninger — R1–R5

| Risiko | Faktisk status |
| --- | --- |
| R1 DMS/Shell SIGKILL | **Åpen, årsak ukjent.** Historisk 11:31:36Z UI killed → DMS exit137, minnepeak705.5M; dette alene beviser ikke OOM/timeout. Ny kaltstart og én bevisst restart viste NRestarts=0, MemoryMax=infinity/TasksMax7069/TasksCurrent40 ved måling; ingen målrettet ressursrettelse eller generell løsning hevdes. |
| R2 hyprland-dialog/libhyprtoolkit | **Åpen.** Tre historiske 11:33–11:34Z SIGSEGV; stack `CWaylandBuffer` → `resizeSwapchain` → `configure`, Hyprland0.57.0-1/guiutils0.2.2-4/toolkit0.6.0-1, Quickshell0.3.2-1/DMS2.0.0-1; TCG/Nehalem/software-rendering og treg appstart. Sannsynlig upstream-buffersti, ikke bevist fysisk eller en bekreftet upstream-fix. Ingen vendorpatch. Eksisterende coredump-index har gamle poster; ikke kalt nye krasj. |
| R3 live gvfsd-fuse | Uendret/ikke retestet i nytt live-image. |
| R4 Tracker | Uendret; ikke utvidet til søketjeneste-/indekseringsarbeid. |
| R5 wallpaper-reaktivering | Eksisterende hook beholdt; godkjent bakgrunn get-path/visning før og get-path etter DMS-restart. Ny Fit-innstilling testet separat fra reaktiveringsmekanismen. Full ny-ISO-aksept gjenstår. |

TCG gir fortsatt trege/stale frames og sporadisk Hyprland-IPC-timeout; sen Power-ramme viste `CLEAN · ?`, ikke en falsk GUI-bekreftelse. Profilhjelperens feilpresentasjon er beholdt. Syntetisk Super+Space ga ikke selvstendig renderaksept i denne økten; eierens tidligere fysiske internal3-observasjon er beholdt, ikke overført til nye bytes. Fysisk Wi-Fi, avspilling/mikrofon, BT-adapter, andre skjermformater, GPU/suspend/Secure Boot er ikke godkjent. QtMultimedia mangler i gjesten (DMSs valgfrie multimedia/sound-effects-probe); dette dokumenterer ikke fysisk PipeWire-avspillingsfeil og er ikke spekulativt pakketilføyd.

## 9. Engineering Standards og dokumentasjon-PR

Risikobasert minsteendring, RED/GREEN, eksplisitt manifest og målfilnekt fulgt. #42 er **OPEN/DRAFT**, stablet på uendret #41-gren, ikke merge-/releaseforespørsel. Høyrisiko-kjedens uavhengige review er **ikke bestått** ved å kalle egen QA uavhengig. Dette er en testet kildekandidat med oppgitte GUI-gap, ikke full stabilisering/ISO-/fysisk aksept. Rapport, fysisk plan og sanert kontrollpunkt publiseres i samme draft; ingen andre PR-er/issues lukkes.

## 10. API-/modellforbruk der det kan dokumenteres

Snapshot **22:34:29Z**: GPT-6.1-sol/openai-codex, `subscription_included`, **122 API-kall**, input370467/output58888/cache-read28984576; estimert0USD, `actual_cost_usd=null` — ikke en målt nullfaktura. Snapshotet gjelder den aktive, gjenbrukte CLI-sesjonen og er ikke en per-prompt-faktura. Senere rapporteringskall kommer i tillegg.

OpenRouter-nøkkel **21:45:43Z→22:34:29Z**: **50.380381901→50.380381901 USD**, observert delta **0.000000000 USD**, målt flere ganger med Decimal. Delt nøkkelteller/reportinglag er ikke eksakt attribusjon/faktura. Providergrensen100USD/måned håndhever **ikke** promptens5USD-økttak. Ingen betalt review/manuelt fallbackkall startet; eksisterende Codex→GLM/OpenRouter og auxiliary-oppsett er ikke endret. Ingen påfylling/ukontrollert retry. Ingen betalt videreføring brukes for å passere manglende reviewport. Endelig teller/konfig-hash kvitteres privat.

## 11. Aktive prosesser og prosjektlåser

Én hovedagent, én QEMU-livstid. Den eksisterende prosjektlåsen ble holdt i hovedprosessens vedvarende verktøykontekst og arvet av QEMU, slik at prosesslivstiden var dekket. Gjesten er kontrollert avsluttet exit0 og offline kontrollert før publisering; ingen installer/bygg startet. Ved publisering holdes låsen bare for rapport/remote-readback; faktisk frigivelse og nonblocking-probe kvitteres i #16/privat kontrollpunkt etter ekstern verifikasjon.

Scheduler `enabled=false/state=paused`, worker `paused=true/stop_requested=false`, uendret. Eksisterende Hermes gateway/dashboard og eldre GnuPG-daemon er ikke startet av oppgaven eller stoppet som «opprydding». Syntetiske QA-credentials, COW-disk, firmware, raw journal og alle tidligere QA-bevis beholdes privat. Ingen force/lazy-unmount eller sletting.

## 12. Neste anbefalte handling

**Én avgrenset neste oppgave: eierens read-only fysiske internal3-diagnose etter [planen](../qa/2026-10-30-internal4-physical-plan.md).** Del gjennomgått JSON og korte Wi-Fi-/lydobservasjoner uten nettverksnavn/nøkler. Deretter kan maskinvarefunn, ny selector-keyboard/fokusaksept og uavhengig session/provisioneringsreview vurderes før eventuell separat gjenopptaking av internal4-bygg. Ingen ny kode/reviewer/VM/ISO/worker/merge starter automatisk.

## Primærkilder for kompatibilitetsvalgene

DMS-kilden er også kontrollert mot QML-strenger i selve pakkede internal3-binæren, ikke bare en antatt tag-versjon.

- [Hyprland0.57 watchdog](https://github.com/hyprwm/Hyprland/blob/0aa6745f705f2c4b0a5004eb019ef76e5bbdb426/start/src/core/Instance.cpp)
- [DMS changelog-marker](https://github.com/duxlabs-dev/dux-shell/blob/9b413296b16721f7679fb62e624cb1ed2433fa58/quickshell/Services/ChangelogService.qml)
- [DMS plugin-trigger-guide](https://github.com/duxlabs-dev/dux-shell/blob/9b413296b16721f7679fb62e624cb1ed2433fa58/.agents/skills/dms-plugin-dev/references/launcher-plugin-guide.md)
- [DMS actual trigger routing](https://github.com/duxlabs-dev/dux-shell/blob/9b413296b16721f7679fb62e624cb1ed2433fa58/quickshell/Modals/DLauncherV2/Controller.qml)
- [DMS Fit-mapping](https://github.com/duxlabs-dev/dux-shell/blob/9b413296b16721f7679fb62e624cb1ed2433fa58/quickshell/Common/Theme.qml)

## Publiseringskvittering

Sluttcommit, rapportlenke, eksakt-head CI, #16/#42-readback og faktisk låsfrigivelse føres i privat kontrollpunkt og sluttkommentaren. Ingen selvrefererende docs-commit-loop. Fullrapport publisert på gren er ikke merge, uavhengig godkjenning eller ferdig internal4.
