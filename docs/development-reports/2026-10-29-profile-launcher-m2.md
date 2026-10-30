# Wilsof OS — M2: launcher og profilmarkør, 2026-10-29

Status ved A-kontrollpunktet: **kildeleveranse og automatiserte porter fullført som draft-PR #39; avgrenset VM-aksept delvis bestått, ikke full GUI-/ytelsesaksept**. Dette er kontrollpunktet før B; avsluttende C-tillegg nederst dokumenterer senere GUI-bekreftelser og en avgrenset M2-feilvisningsrettelse.

- Start: 2026-10-29 22:44 UTC. Rapportgrunnlag: samme kveld, etter kode-CI.
- Kode: `ac037b0e57ca4a7e5dac266fdacddddfbb71fbad` på `feat/profile-launcher-m2-20261029`.
- Stablet base: M1 draft [#38](https://github.com/tomli0/wilsof-os/pull/38) @ `f8709a38d4cf939c4088bbadf6eb8abf2d487a70`. M1 er ikke merget. Integrasjonen er fortsatt `219894f1d4fc365b5e6546c2af9a146141634a1c`.
- [Draft-PR #39](https://github.com/tomli0/wilsof-os/pull/39), [status #16](https://github.com/tomli0/wilsof-os/issues/16), [detaljert M2-kontrakt](../product/WILSOF_PROFILE_LAUNCHER.md).

## Bevisgrunnlag og avgrensning

Faktisk PR-base/head, alle eksisterende worktree-heads og statuser, remote-grener, tilgjengelige ressurser, prosesser og pausekontroller ble lest før endringer. Alle eksisterende worktrees var rene. Den eksisterende prosjektlåsen ble tatt eksklusivt; en konkurrerende nonblocking-probe ble avvist. Én hovedagent, ingen delegert utvikler eller betalt reviewer.

DMS v2.0.0-primærkildene for launcher/widget, komposittmanifest, plugininnstillinger og Spotlight IPC ble hentet og lest direkte. Tidligere internal2-aksept er historikk, ikke automatisk aksept av M2. Native M2-kontroll bruker én disponibel qcow2-overlay over den bevarte internal2-disken, kopierte firmwarevariabler, ingen ISO og ingen installasjon. Opprinnelige disk- og firmwarehashverdier og offline qcow2-integritet ble kontrollert før oppstart. QEMU arver prosjektlåsen fra sin identifiserte supervisor.

## 1. Fullførte milepæler

- Fire profiler i eksisterende DMS-launcher: CLEAN, STUDY, DEV, EVERYDAY. Super+Space-bindingen beholdes; søk `profil`. Klikk barens profilnavn åpner samme launcher med søk.
- DMS-barplugin viser bekreftet profil; ukjent tilstand har `· ?`, feil er synlig. Et valg varsles som vellykket bare etter faktisk hjelperresultat uten feil.
- `wilsof-profile-ui` skiller `saved`, `applied`, `error`, bruker M1s validering/atomiske lagring/lås og utfører kun lesende klient-/laginventar fra Hyprland. Ingen app, vindu, arbeidsområde eller oppgave muteres. Ingen dashboard eller daemon innføres.
- CLEAN i M2 betyr bekreftet fravær av dashboardflater. Hvis `org.wilsof.Tasks` oppdages, avvises operasjonen uten å drepe/flytte/skjule vinduer. M4s fremtidige hide/show-protokoll er ikke implementert eller påstått bestått.
- Eksisterende image-manifest distribuerer begge hjelpere og seks pluginfiler. Runtime bevarer personlig DMS-layout og eksplisitt plugin-deaktivering; nye hjem får profilwidget som standard. Det eldre VM-skriptet gjenbruker samme runtime.

## 2. Claude QA-funn og utbedringer

Ingen ny uavhengig AI-/Claude-review. Dette er en middels-risiko UI-/brukerkonfigurasjonsendring, ikke disk-, autentiserings- eller pakkekjedeendring. Egen gjennomgang er utført; PR er draft til eiergjennomgang. Tidligere Claude-review av installer gjelder ikke ny M2-kode.

Egen RED-test avdekket at feil etter atomisk rename kunne rapportere gammel lagret profil. Rettelsen leser faktisk lagret tilstand tilbake, beholder `applied=null` og rapporterer ukjent holdbarhet/feil. Først feilet regresjonen; deretter bestod den. Ingen test er svekket for å skjule feilen.

## 3. Kodekvalitet, sikkerhet og tester

**299 passed / 1 skipped** i full suite. Skip er den eksisterende opt-in native Arch-chroot-porten; ingen installerendring krever at den gjentas. 29 M2-tilfeller dekker faktisk helperprosess, ekte JS-modell kjørt i Node, distribusjon og bevarings-/feilgrenser. M1s 69 tester er fortsatt med i regresjonen.

Kommandoer:

    python -m pytest -q --junitxml=.../m2-regression.xml
    python -m pytest tests/test_profile_ui.py tests/test_profile_plugin.py tests/test_profile_deployment.py -q
    shellcheck --exclude=SC1091 --shell=sh [eksisterende sh-manifest fra CONTRIBUTING.md]
    shellcheck --shell=bash automation/wilsof-github-worker.sh scripts/install-arch-test-vm.sh iso/profiledef.sh
    git diff --cached --check

Første fulle kjøring brukte feil Python uten jsonschema og stoppet i collection. Dette var ikke en bestått test; den eksisterende isolerte QA-venven ble deretter brukt, uten installasjon/endring av vertens runtime. RED-loggene viser manglende helper, modell/plugin, distribusjon og post-rename-feil før rettelser. ShellCheck, JSON, Python AST med 3.12-grammatikk, diffkontroll og avgrenset skanning av tilføyde linjer etter nøkkelmønstre/farlige kommandoer bestod. Dette er ikke en full sikkerhetssertifisering.

Negative porter: ingen GUI, ugyldige argumenter, korrupt/fremtidig profiltilstand, synlige dashboardklienter på annen skjerm/lag, feilformatert/feilet/timet-out IPC, personlig layout og eksplisitt deaktivert plugin, ødelagte/symlinkede plugininnstillinger og feil etter lagring. Ingen falsk anvendt-kvittering eller stille korrupsjonsreparasjon.

## 4. Commits og CI-status

Kodecommit `ac037b0e57ca4a7e5dac266fdacddddfbb71fbad` er pushet og PR-base/head/draft er lest tilbake. Eksakt kode-head har to beståtte Validate-kjøringer:

- [Push-CI 40972538900](https://github.com/tomli0/wilsof-os/actions/runs/40972538900).
- [PR-CI 40972544732](https://github.com/tomli0/wilsof-os/actions/runs/40972544732).

`gh pr checks 39` viste begge som pass. Workflowfiltrene er bare utvidet for egen gren og stablet M1-base. Slutt-head med denne rapporten får separat CI-kvittering i PR/status og kontrollpunkt; kode-CI tilskrives ikke automatisk en senere dokumentasjonscommit.

## 5. ISO og bevarte artefakter

Ingen ny ISO eller offentlig release. Uendrede internal2-bytes inneholder ikke M2. Opprinnelig installert disk ble kontrollert mot bevart SHA256 `f28d75d3cfc9845424519922e1eba6ff73eff1a1f5aab8492d4326245b229b6e`; firmware mot `6c31b3818d5f111ba9eaf12321d24cf23892ddf9edbe5a925f318113f0cee9ca`. Ny overlay og kopiert firmware er private QA-artefakter, aldri distribuert ISO-data. Endelig post-stop-kontroll føres i sluttrapporten.

## 6. Faktisk VM-kontroll

Miljø: QEMU TCG, Nehalem, 2 vCPU, 6144 MiB; ingen tilgjengelig KVM-tilgang. Installert Arch med Hyprland 0.57.0-1, Dux/DMS 2.0.0-1 og Quickshell 0.3.2-1. Bare ett gjestesystem er startet.

| Port | Utfall og avgrensning |
| --- | --- |
| Disk-only boot / ordinær QA-innlogging | Bestått i disponibel overlay; ingen ny installasjon. |
| Native pluginlasting | DMS rapporterte `wilsofProfiles [loaded]`; eksplisitt plugin-reload returnerte success. |
| Native QML | Alle tre sluttfiler bestod gjestens qmllint mot faktisk DMS-runtime; installerte filhashverdier bevart. |
| Super+Space | Syntetisk QEMU-tast åpnet eksisterende launcher; fysisk klientvideresending og ≤1 s er ikke verifisert. |
| Fire profilrader | CLEAN/STUDY/DEV/EVERYDAY, Aktiv-markering og søket `profil` visuelt kontrollert i eksisterende DMS-launcher. |
| Profilbytte | Faktisk lagret STUDY, CLEAN, STUDY via launcher/Enter; barens CLEAN og STUDY visuelt kontrollert. |
| Tre eksisterende apper | Ghostty, Text Editor og Files hadde identiske klientadresser, PID-er, posisjon, størrelse, skjerm og arbeidsområde før/etter den dokumenterte CLEAN/STUDY-syklusen. Ingen dataendring utført av profilbytte. |
| DEV/EVERYDAY full syntetisk syklus | Ikke bestått som full aksept. STUDY-ventingen på 10 s feilet før sen faktisk lagring ble observert; DEV-forsøket nådde ikke forventet lagring innen 30 s. Årsaken er ikke isolert. Ikke automatisk kalt TCG-feil eller godkjent. EVERYDAY-valget ble ikke gjennomført etter stoppet. |
| Ytelse / flere skjermer / levende dashboard | Ikke verifisert. Ingen ≤1 s/≤2 s-rendergaranti, fysisk flerskjermtest eller M4-hide/show-aksept. |

Cold TCG ga faktisk IPC-timeout ved 0,75 s og 3 s og treg rendering. Hjelperens produksjonsgrense ble avgrenset til 3 s per lesing, QML-watchdog 18 s; dette er fortsatt begrenset, ikke endeløs retry. Polling er delt mellom flater og hvert femte sekund; anvendelsessvaret oppdaterer markøren direkte. Et inntruffet idle-låsforløp ble ordinært autentisert; deretter ble DMS' eksisterende midlertidige idle-inhibitor brukt i QA. Dette er ikke en ny idle-/låsaksept.

Visuelle bevis: [fire profilrader](../../evidence/m2-20261029-four-profiles.png), [CLEAN-markør](../../evidence/m2-20261029-clean-bar.png), [STUDY med tre apper](../../evidence/m2-20261029-study-three-apps.png). Alle er faktisk inspiserte bilder med syntetisk QA-innhold. QML-varslet om at launcherens logiske Item ikke er plassert i en graphics scene er bevart; ingen tilhørende TypeError/ReferenceError ble observert.

## 7. Oppstart og passordinnlogging

Ordinær greeterinnlogging og opplåsing brukte eksisterende privat syntetisk QA-hemmelighet, uten argument-/logglekkasje. Root/QGA-deploy påstås ikke å være innlogging. Den historiske internal2-autentiseringsporten omskrives ikke. Ingen fysisk maskin-, passordpolicy- eller installerendring.

## 8. Gjenstående feil og begrensninger

Fireprofil-GUI-syklusen og timingportene er åpne. Eiers faktiske Super-tast fra fysisk klient, Esc/Enter-flyt under normal akselerasjon, alle profilvalg, flere skjermer og barens timing må observeres. M4s dashboardprotokoll og usendt arbeid er utenfor økten. Bevarte R1–R3-upstream-/runtimefunn er ikke rettet. Wallpaper #37 holdes separat.

## 9. Engineering Standards og rapportering

CONTRIBUTING, produktkontrakten og Engineering Standards er fulgt med eksplisitte avvik/ukjørte porter. Egen kildegren, stablet draft, ingen merge eller integrasjonsgrenendring. Personlige DMS-settings ble først bevart i VM; deretter ble widgeten eksplisitt lagt til bare i den disponible QA-layouten med egen backup. Dette er ikke en skjult endring av installasjonens bevaringspolicy.

## 10. Dokumentert modellforbruk

Primær er GPT-6.1-sol via openai-codex; faktisk sesjon ble lest som `subscription_included` / `cost_status=included`. Aggregate `actual_cost_usd` mangler og kalles ikke fakturert null. Eksisterende fallback er GLM 5.3 via OpenRouter; konfigurasjon, nøkler og betalingsgrenser er uendret. Ingen betalt review eller delegert modell er bestilt.

OpenRouter GET key/credits ble lest før arbeid: nøkkelbruk **48,328455501 USD**, nøkkelgrense 100 USD, gjenværende **51,671544499 USD**. Kreditt-endepunktet rapporterte 90 USD total kreditt og **58,472343972 USD** total bruk. Separate senere key-målinger gjennom M2-kodepublisering viste uendret **48,328455501 USD**, altså **0,000000000 USD observert nøkkeløkning**. Dette er en konservativ øvre grense for ny øktkostnad fra denne nøkkelen i måleintervallet, ikke sikker attribusjon av delt nøkkel eller faktura. Økttaket er 5 USD; ukjent eller truet budsjett betyr kontrollpunkt/stopp. Ingen påfylling eller routingendring.

## 11. Prosesser, prosjektlås og kontrollpunkt

Ved dette A-kontrollpunktet er én disponibel gjest fortsatt bevisst levende for en eventuell separat B-kontroll; prosjektlåsen holdes fortsatt av supervisor og er arvet av QEMU. Den må ikke frigis eller gjestedisken åpnes av en annen prosess før kontrollert stopp. Eksisterende cronjobb er enabled=false/state=paused; worker paused=true/stop_requested=false. Ingen reaktivering.

Private logger, røde/grønne tester, JUnit, CI-avlesning, native QML/hashbevis, screenshots, klientinventar og budgetbaseline ligger i bevisgruppen `overnight-20261029-224438/`. Et separat privat kontrollpunkt registrerer faktisk PID/socket/overlay/lockeier og sikkert neste steg. Ingen gamle kontrollpunkter/testartefakter er slettet.

## 12. Neste sekvensielle handling

M2 er kontrollert levert som kilde/draft med ovenstående GUI-gater åpne. Før B: bekreft publikasjon, CI, fortsatt låseierskap og kostnad/ressurser, og lag nytt kontrollpunkt. B kan kun undersøke minste rettelse for #37 på separat gren; ingen M3/M4, dashboard, ISO, installasjon, fysisk disk, Proxmox, merge eller release. Ved utilstrekkelig rotårsaksbevis skal B stoppe uten spekulativ kode. Endelig C-rapport skal bekrefte faktisk gjestestopp/låsfrigivelse og oppdatere #16.

## C — avsluttende kvalitetssikring, 2026-10-29/30 UTC

Dette tillegget supplerer det fryste A-kontrollpunktet; tidligere feilede eller ukjørte porter ovenfor er ikke omskrevet til bestått historikk.

- Etter B-portens faktiske DMS-restart/kaldstart ble DEV og EVERYDAY valgt gjennom **visuelt kontrollert, navngitt første profilrad** og Enter. `saved=applied=development/everyday`, `error=null` ble lest fra faktisk hjelper, og [DEV-markør](../../evidence/m2-20261029-dev-bar.png) / [EVERYDAY-markør](../../evidence/m2-20261029-everyday-bar.png) ble visuelt kontrollert. Alle fire profiler er dermed faktisk valgt og vist i bar på tvers av økten. Dette er ikke en bestått automatisk fireprofilsyklus med tre åpne apper eller en ytelsesmåling. Den tidligere treklient-/geometribevaringen gjennom CLEAN/STUDY gjelder fortsatt sin avgrensede port.
- DMS' generelle søk kan rangere app- og innstillingstreff foran profilrader. De tidligere korte/naive automatiske seleksjonsforsøkene forblir feilet/ufullstendige. Senere aksept valgte den faktisk observerte `Profil · DEV` / `Profil · EVERYDAY`-raden, ikke en antatt første rad. Brukerveiledningen presiserer dette; ingen ny launcher eller tastatursnarvei er innført.
- En disponibel korrupsjonsfixture ga faktisk helper exit 1, `saved=clean`, `applied=null`, lesbar parsefeil og uendrede korrupte bytes. Baren viste rød `CLEAN · ?`, aldri Aktiv/suksess. Egen QA avdekket at launcherens undertittel ikke viste den underliggende feilen; en ny assert mot den faktiske JS-modellen feilet før rettelsen. **Korrigerende kodecommit `7ba3bb89322258eefbcc1f6a7b82a82444070355`** legger bare feilmeldingen til eksisterende profilrader. Full regresjon består fortsatt: **299 passed / 1 expected skip**.
- [Push-CI 40976408936](https://github.com/tomli0/wilsof-os/actions/runs/40976408936) og [PR-CI 40976413698](https://github.com/tomli0/wilsof-os/actions/runs/40976413698) er completed/success på eksakt korrigert kode-head. En generell Node-syntakssjekker forstår ikke QML-direktivet `.pragma library`; den faktiske JS-modelltesten håndterer direktivet eksplisitt, og native QML/DMS er separat kontrollert. Det er ikke en ignorert produksjons-syntaksfeil.
- Et rent DMS-prosesskontekst var nødvendig for å avstemme endret delt JS; plugin-reload alene viste fortsatt tidligere undertittel. Etter ordinær DMS-restart ble [lesbar Feil/parsefeil i launcheren](../../evidence/m2-20261029-readable-error.png) og `CLEAN · ?` faktisk visuelt kontrollert, uten Aktiv-markering. Ingen automatisk reparasjon av korrupsjonen. QA beholdt både korruptfilen og opprinnelige bytes, og gjenopprettet deretter bare sin egen syntetiske profilbackup før stopp.
- Under den lange diagnostikken kom eksisterende idle-lås inn igjen etter DMS-restart. Første syntetiske input ga konkret stray-release-/PAM-avvisning; en ny avgrenset, langsommere privat input ga faktisk `auth: authenticated for hyprlock` og locker-exit. En stale frame viste fortsatt kontrollfeltet etter exit, og ble ikke kalt GUI-suksess. Ingen autentiseringsrettelse eller ny fysisk idle-/unlock-aksept påstås.
- Begge sekvensielle QEMU-livsløp er nå avsluttet med **exit 0**; siste exit ble verifisert **2026-10-30T00:05:13.668478+00:00**. Ingen samtidige gjester. Begge nye overlay-filer bestod offline qcow2 check; første overlay ble bevart frosset gjennom kaldstart i en COW-barnfil. Original internal2-ISO, installert disk og firmware matcher fortsatt sine opprinnelige hashverdier.

M2 har dermed testet kilde og avgrensede ekte GUI-bevis for fire profiler og synlig korrupsjonsfeil. **Timinggrensene, fysisk Super-ruting, fysisk flerskjerm og M4-dashboardkontrakten er fortsatt ikke akseptert.** Ingen uavhengig reviewer, merge eller ISO. Prosjektlåsen holdes gjennom sluttpublisering/status; faktisk frigivelse føres i sluttrapportens statuskvittering på #16.
