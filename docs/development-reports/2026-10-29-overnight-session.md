# Wilsof OS — autonom nattøkt: M2, wallpaper #37 og sluttkontroll

Status: **kontrollert kildeleveranse i to separate draft-PR-er; lokale tester, CI og avgrensede ekte GUI-/livssyklusporter bestått. Ikke merge-, ISO-, ytelses- eller fysisk aksept.**

Arbeidet startet **2026-10-29 22:44 UTC** og runtime-kontrollen sluttet **2026-10-30 00:05:13 UTC**. Rapport/publisering skjer deretter 30. oktober UTC. Filnavnet bruker øktens startdato; dette er samme nattøkt, ikke en påstand om at avslutningen skjedde 29. oktober.

- [M2 draft-PR #39](https://github.com/tomli0/wilsof-os/pull/39): stablet på umerget M1 #38.
- [Wallpaper draft-PR #40](https://github.com/tomli0/wilsof-os/pull/40): separat fra M1/M2, direkte på uendret integrasjon.
- [Full M2-rapport med A-kontrollpunkt og C-tillegg](https://github.com/tomli0/wilsof-os/blob/28e0a8f856eacc4ecac8e8d5ceb79d0580e36929/docs/development-reports/2026-10-29-profile-launcher-m2.md).
- [Wallpaper-rotårsak og reproduksjon](../qa/2026-10-29-wallpaper-recovery.md), [sanert maskinlesbart bevis](../qa/2026-10-29-overnight-evidence.json), [status #16](https://github.com/tomli0/wilsof-os/issues/16), [åpen oppfølging #37](https://github.com/tomli0/wilsof-os/issues/37).

## Bevisgrunnlag og avgrensning

Dette er nye kilde-, test-, GitHub- og QEMU-observasjoner, ikke en gjenbruk av tidligere aksept som bevis for nye bytes. Historiske internal2-journaler ble lest for #37. Ingen ISO ble bygget, ingen full installasjon ble utført, og ingen fysisk disk/USB, Proxmox, offentlig release eller merge ble foretatt. M3/M4/dashboard/Kanban og ny scheduler/worker er ikke startet.

Én hovedagent, ingen parallelle utviklingsagenter eller betalt uavhengig reviewer. Det samme disponible QA-systemet ble kjørt i to **sekvensielle** QEMU-livsløp, med kontrollert exit/offline kontroll før ny COW-kaldstart. Aldri mer enn én aktiv QEMU-gjest. Den eksisterende prosjektlåsen ble holdt av identifisert supervisor og verifisert arvet i QEMUs åpne FD.

## 1. Fullførte milepæler

### A — M2

Fire profiler finnes gjennom eksisterende DMS-launcher, med beholdt Super+Space og profilmarkør i eksisterende top bar. Ingen separat launcher, ny daemon eller dashboard er bygget. `wilsof-profile-ui` skiller faktisk `saved`, `applied` og `error`; GUI-fravær, ugyldig IPC, korrupsjon eller synlig dashboard gir ingen falsk anvendt-kvittering. CLEAN bekrefter bare M2s implementerte fravær av dashboardflater; M4s fremtidige hide/show er fortsatt utenfor omfang.

M1-tilstanden, streng validering og atomisk lagring gjenbrukes. Ingen klient-, fokus-, arbeidsområde-, app- eller oppgavedata-mutasjon inngår i profilbytte. Eksplisitt eksisterende image-manifest og desktop-runtime distribuerer nødvendige komponenter; personlig DMS-layout og eksplisitt deaktivert plugin bevares. Nye hjem får profilwidget som standard.

A ble publisert, fjernlest byte-for-byte og kontrollpunktført før B startet. Under avsluttende C ble en liten feilvisningsmangel rettet på **M2-grenen alene**: profilradene viser nå faktisk underliggende feil, ikke bare ukjent barstatus.

### B — wallpaper #37

Den dokumenterte feilen er reprodusert: første mock-DMS feiler før READY, automatisk gjenoppretting gjør DMS aktiv, men den opprinnelige wallpaper-startjobben har feilet med `dependency` og gir null helperkjøringer. En regresjon som krever reaktivering feilet før rettelsen.

Minste produksjonsrettelse er én instruksjon i eksisterende DMS-dropin:

    ExecStartPost=-/usr/bin/systemctl --user --no-block start wilsof-wallpaper.service

Ingen endring av wallpaper-hjelper, asset, timeout, bekreftelsesregler eller Restart-policy. Ingen timer/daemon eller restart-løkke. Eksisterende installasjonsmanifest distribuerer allerede dropin-fila. R1s SIGKILL-årsak og R2/R3 forklares eller lukkes ikke av dette.

### C — sluttkontroll

Nye commits, kildeavgrensning, CI, bevis og opprinnelige grener/worktrees er kontrollert. Begge QEMU-livsløp er avsluttet med exit 0, private QA-fixtures er gjenopprettet/bevart, native fixture-enheter stoppet og midlertidig inhibitor deaktivert. Endelig GitHub-/låsfrigivelseskvittering publiseres på #16 etter eksakt read-back av rapport og status.

## 2. Claude QA-funn og utbedringer

Ingen ny Claude-/annen uavhengig review. UI-/user-unit-endringene er behandlet som middels risiko; ingen disk-, autentiserings- eller pakkekjedeendring ble introdusert. PR-ene forblir draft til eiergjennomgang. Historisk installerreview overføres ikke til ny kode.

Egen QA fant og rettet to konkrete M2-feil med observerte røde tester: post-rename-feil kunne oppgi gammel lagret profil, og launcherens undertittel viste ikke underliggende bekreftelsesfeil. Sistnevnte korreksjon er `7ba3bb89322258eefbcc1f6a7b82a82444070355`; faktisk ny feiltekst ble deretter visuelt kontrollert i rent DMS-prosesskontekst. Ingen feiltest er erklært bestått før ny kjøring.

## 3. Kodekvalitet og sikkerhetsstatus

| Port | Faktisk resultat |
| --- | --- |
| M2 full regresjon etter C-rettelse | **299 passed / 1 skipped**, JUnit: 300 tilfeller, null failures/errors. |
| Wallpaper full regresjon | **207 passed / 2 skipped**, JUnit: 209 tilfeller, null failures/errors. |
| Native systemd 262.1-1, separat fra CI | **7/7 passed**, 81,017 s i grønne fixtureporter. |
| Native wallpaper RED | Originalkontroll bestod, recovery-regresjon feilet konkret før rettelsen; null helperkall etter gjenopprettet DMS. |
| Statisk analyse | ShellCheck med riktig sh/bash-dialekt, Python AST/3.12-grammatikk, JSON og diffkontroll bestått. |
| Native QML | Alle tre M2-QML-filer bestod gjestens qmllint mot faktisk DMS-runtime; faktiske filhashverdier er bevart. |
| JS | Faktisk launcher-JS kjøres i Node-test, inklusive feilmelding og ingen Aktiv-markering ved ubekreftet profil. QMLs `.pragma library` håndteres eksplisitt, ikke som vanlig Node-fil. |
| Avgrenset sikkerhetsskann | Nye linjer kontrollert for nøkkelmønstre/farlige operasjoner; ingen funn. Ikke en full sikkerhetssertifisering. |

Native-portene dekker recovery/eksplisitt restart med nøyaktig én helperkjøring per vellykket DMS-start, ingen ventende startsyklus/duplikatstorm, synlig kosmetisk feil uten DMS-restart, køleggingsfeil isolert fra DMS, manglende binær, avgrenset permanent startfeil og avbrutt pending økt.

De to skipene i wallpaper-suiten er den eksisterende opt-in native Arch-chroot-porten og den nye opt-in systemd-livssyklusporten. Sistnevnte ble **faktisk kjørt separat i gjesten**, ikke simulert godkjent av CI. M2 har bare den eksisterende native Arch-chroot-skipen.

Hjelpernes og enhetenes privilegiegrenser er uendret. Native testharness har VM-/ikke-root-guard, unike navn, subprocessfrister og opprydding begrenset til egne nye unit-lenker/jobber; fixturefiler og journaler beholdes. Ingen eksisterende vertsskrivebord eller vertens user-units ble endret. Den første fulle M2-testkjøringen brukte feil interpreter og stoppet på manglende jsonschema; deretter ble eksisterende QA-venv brukt. Den feilkjøringen er ikke telt som bestått.

## 4. Commits, PR-er og faktisk CI

| Rolle | Eksakt commit | Verifisert CI |
| --- | --- | --- |
| M2 opprinnelig implementasjon | `ac037b0e57ca4a7e5dac266fdacddddfbb71fbad` | Push 40972538900 / PR 40972544732: success. |
| M2 A-publiseringskontrollpunkt | `7a7d5543030fcb14629653e5844add4782785413` | Push 40972930701 / PR 40972938189: success; logger 299/1. |
| M2 C-feilvisningsrettelse | `7ba3bb89322258eefbcc1f6a7b82a82444070355` | [Push 40976408936](https://github.com/tomli0/wilsof-os/actions/runs/40976408936) / [PR 40976413698](https://github.com/tomli0/wilsof-os/actions/runs/40976413698): success på eksakt kode-head. |
| M2 sluttdokumentasjon/bilder | `28e0a8f856eacc4ecac8e8d5ceb79d0580e36929` | [Push 40977813822](https://github.com/tomli0/wilsof-os/actions/runs/40977813822) / [PR 40977819438](https://github.com/tomli0/wilsof-os/actions/runs/40977819438): completed/success på eksakt slutt-head. |
| Wallpaper implementasjon | `d05ec2f8c11730c00145bf1bc9239bfdf4d4aaac` | [Push 40974405394](https://github.com/tomli0/wilsof-os/actions/runs/40974405394) / [PR 40974410572](https://github.com/tomli0/wilsof-os/actions/runs/40974410572): success; logger 207/2. |

M2-base er M1 `f8709a38d4cf939c4088bbadf6eb8abf2d487a70`; wallpaper-base er integrasjon `219894f1d4fc365b5e6546c2af9a146141634a1c`. Ingen merge. Wallpaper-PR inneholder **ingen** M1/M2-profilimplementasjon, og M2-PR inneholder **ingen** wallpaper-rettelse. Bare egne workflowfiltre er utvidet for relevante grener/PR-baser; eksisterende CI-stack er gjenbrukt.

Denne rapportens publiseringscommit/eksakt-head CI kan ikke selvrefereres før commit finnes. Den faktiske verdien, alle fil-read-backs og slutt-CI føres i status/PR og privat kontrollpunkt etter push, før arbeidet erklæres avsluttet.

## 5. ISO, størrelse, SHA256 og artefakter

**Ingen ny ISO.** Uendrede internal2-bytes inneholder ikke M2 eller denne lokale wallpaper-rettelsen. Opprinnelig ISO, installert base og firmware ble kontrollert mot bevarte hasher etter siste gjestestopp:

| Opprinnelig artefakt | Bekreftet uendret SHA256 |
| --- | --- |
| `wilsof-internal-2026.10.28-internal2-x86_64.iso` | `dc4bfb3944767e743f858880d32b0d1179b5a6c629e5cfed68410e3a73a4f8d1` |
| Installert internal2-virtuell base | `f28d75d3cfc9845424519922e1eba6ff73eff1a1f5aab8492d4326245b229b6e` |
| Opprinnelig installert firmware | `6c31b3818d5f111ba9eaf12321d24cf23892ddf9edbe5a925f318113f0cee9ca` |

Nye COW-overlay-/firmwarefiler og to hashverifiserte private runtime-arkiver er beholdt som QA-bevis, ikke distribuert image. Første overlay ble fryst etter første kontrollerte stopp og brukt read-only som backing for kaldstartens barn. Ingen eldre artefakt eller kontrollpunkt ble slettet.

## 6. Faktisk installasjon og runtime-porter

Ingen full installasjon eller ny boot fra ISO ble utført. Det eksisterende installerte systemet ble startet uten ISO i disponibel COW-kjede. Miljøet var QEMU TCG/Nehalem, 2 vCPU/6144 MiB, Hyprland 0.57.0-1, Dux/DMS 2.0.0-1, Quickshell 0.3.2-1 og systemd 262.1-1. KVM var ikke tilgjengelig.

| Runtime-port | Utfall |
| --- | --- |
| Eksisterende disk-only oppstart / normal QA-innlogging | Bestått i begge sekvensielle oppstarter. Ikke ny installer-/diskaksept. |
| M2 profilrader og barmarkører | CLEAN/STUDY/DEV/EVERYDAY faktisk observert og valgt over økten. |
| Ingen flytting/lukking ved profilbytte | Tre faktiske klienter beholdt PID/adresse/geometri/skjerm/workspace gjennom dokumentert CLEAN/STUDY-syklus. Ikke full fireprofil-/flerskjermsyklus. |
| M2 korrupsjonsfeil | Faktisk exit 1, CLEAN-lesefallback, applied=null, korruptfil bevart, rød `CLEAN · ?` og lesbar Feil/parsefeil i launcher, uten Aktiv-markering. |
| Faktisk DMS-restart med ny dropin | DMS active, NRestarts=0, post-hook exit 0; ny wallpaper InvocationID, helper exit 0 og Result=success. |
| Faktisk kaldstart | Normal innlogging; ny DMS-/wallpaper-invokasjon, post-hook og helper exit 0, ingen automatisk DMS-restart i den observerte porten. Readiness-proben brukte 179,287 s: ikke en ytelsesaksept. |
| Riktig bakgrunn | `dms ipc call wallpaper get` ga godkjent sti etter restart og kaldstart; riktig mørk geometrisk WS-bakgrunn faktisk visuelt observert begge ganger. |
| Avslutning | Begge prosesser exit 0; begge nye overlay-filer offline qcow2 check 0; alle opprinnelige artefakthasher uendret. |

Bilder: [wallpaper etter DMS-restart](../../evidence/wallpaper-37-20261029-restart.png), [wallpaper etter kaldstart](../../evidence/wallpaper-37-20261029-cold.png). M2-bildene ligger kun i M2-PR/rapporten lenket øverst, ikke som profilimplementasjon i wallpaper-PR.

Tilgjengelig plass **2026-10-30T00:06:54.114908Z**: **106147639296 byte = 98,8576927185 GiB**. Dette er et faktisk prepubliseringsøyeblikksbilde, ikke en garanti om uendret sluttmåling. Ingen plassopprydding eller diskoperasjon mot fysiske enheter ble foretatt.

## 7. Oppstart og passordinnlogging

Eksisterende private syntetiske QA-opplysninger ble brukt ved vanlig greeter og nødvendig ordinær opplåsing, uten hemmeligheter i argv/logger eller offentlig bevis. Root/QGA-filkopiering er ikke ført som passordinnlogging.

DMS-restart kan nullstille midlertidig idle-inhibitor. Under C-diagnostikken kom låsen inn igjen; første syntetiske input ga dokumentert stray-release-/PAM-avvisning, deretter ga en avgrenset langsommere input faktisk autentisering og locker-exit. En stale frame ble eksplisitt avvist som bevis før nytt bilde viste skrivebord/launcher. Det er ikke en ny autentiseringsrettelse, fysisk tastaturtest eller generell femminutters idle-aksept. Inhibitor ble deaktivert før avslutning.

## 8. Gjenstående feil og begrensninger

- Timingkravene ≤1 s launcher / ≤2 s rendret profilmarkør er **ikke verifisert** i den trege TCG-gjesten. Faktiske timeout-/renderforsinkelser er beholdt, ikke skjult eller kalt rene ytelsesporter.
- DMS' generelle `profil`/`dev`-søk kan rangere andre app-/innstillingstreff foran Wilsof-profiler. Tidligere naive syntetiske seleksjoner forblir feilet/ufullstendige; senere aksept valgte en visuelt identifisert eksakt profilrad. Ingen årsak er tillagt tidligere feilede forsøk uten bevis.
- Delt JS-kontekst ble ikke fullt avstemt av plugin-reload alene. Den korrigerte feilteksten ble testet etter ordinær DMS-prosessrestart; installasjonskontrakten krever fortsatt ny økt for aktivering av kildeoppdatering.
- Fysisk klient→VM Super-ruting, fysisk flerskjerm, GPU, USB, lyd, Wi-Fi og suspend er ikke testet. Full fireprofilsyklus med tre apper/flerutgang er ikke påstått.
- M4s levende dashboard, dialoger, usendt arbeid og hide/show/reconnect er ikke implementert. Ingen dashboard/Kanban eller M3/M4 startet.
- R1–R3 og øvrige tidligere åpne runtime-/installerporter forblir åpne. #37 får en testet kilderettelse til review, ikke en påstand om endrede gamle image-bytes eller autorisasjon til merge/release.

## 9. Engineering Standards og dokumentasjon

Arbeidet gjenbrukte CONTRIBUTING, Engineering Standards, produktkontrakten, eksisterende workerlås, installasjonsmanifest og CI. A hadde eksplisitt publikasjon/read-back/kontrollpunkt før B; B brukte en ny gren fra faktisk integrasjonsbase. Den lille C-feilvisningskorreksjonen ble testdrevet og lagt kun på M2-grenen. Ingen urelatert kodeopprydding eller avhengighetsoppgradering.

Før B var alle 20 daværende M2-fjernfiler byte-verifisert ved eksakt commit. Endelig C-read-back gjelder siste kilde/dokumentasjon og publisert rapport, ikke bare et vellykket push-kall. Tolv opprinnelige remote-ref-er og ni rene opprinnelige worktree-heads/statuser er verifisert bevart; nye grener kommer i tillegg. Ingen pauset automatisering ble aktivert.

## 10. Dokumentert modell-/API-forbruk

Primær: GPT-6.1-sol/openai-codex. Eksisterende GLM 5.3/OpenRouter-fallback og Claude Sonnet 4.6-reviewrute ble inspisert, ikke endret. Ingen betalt review, delegert modell eller manuelt fallback-kall ble bestilt. Ingen quota-reset er påstått og ingen 429-retryløkke er startet.

Faktisk hovedsesjonssnapshot **2026-10-30T00:06:54Z**:

| Felt | Målt verdi |
| --- | ---: |
| API-kall i hovedsesjonsregister | 128 |
| input_tokens | 308976 |
| output_tokens | 91150 |
| cache_read_tokens | 28243712 |
| cache_write_tokens | 0 |
| billing_provider / billing_mode | openai-codex / subscription_included |
| cost_status / estimated_cost_usd | included / 0,0 |
| actual_cost_usd | null — ingen fakturert null påstås |

Dette er et tidsstemplet snapshot; senere publiseringssamtale øker tellere. Sluttkvitteringen oppdaterer faktisk registerverdi uten å dobbelttelle eller anta at tokenfeltene er fakturerbare abonnementskostnader.

OpenRouter key-baseline før arbeid var **48,328455501 USD**; siste prepubliseringsmåling var fortsatt **48,328455501 USD**, altså **0,000000000 USD observert økning** på den aktuelle nøkkelen. Samme intervall hadde gjentatte uendrede målinger. Nøkkelgrense 100 USD/gjenværende 51,671544499 USD ble lest; kreditt-endepunktet viste opprinnelig 90 USD total kreditt og 58,472343972 USD total bruk. Nøkkeløkningen er et konservativt intervallmål/øvre grense, ikke eksakt øktattribusjon på en delt nøkkel eller en faktura. Brukt målbar OpenRouter-økning er under øktgrensen 5 USD; ingen kredittpåfylling eller betalings-/routingendring.

## 11. Aktive prosesser, lås, pause og bevis

Siste QEMU-exit er faktisk verifisert **2026-10-30T00:05:13.668478Z**, exit 0. Begge offline qcow2-kontroller ga 0. Ingen guest-disk åpnes av en ny gjest etter denne grensen. Private runtime-arkiver er hentet og SHA256-verifisert før stopp; alle testbevis, overlayfiler, firmwarekopier og korrupsjonsfixturer beholdes.

Prosjektlåsen er fortsatt bevisst holdt under denne rapportens commit/push/read-back og GitHub-statusskriving. Den frigis først etter beskyttede operasjoner; nonblocking-probe og faktisk frigivelsestid registreres i sluttkvittering på #16 og privat kontrollpunkt. Ingen foreldet PID eller uavsluttet historisk DB-sesjon brukes som prosessbevis.

Eksisterende Wilsof-cronjobb er enabled=false/state=paused; worker paused=true/stop_requested=false. De er bare lest. Faktisk prosesskontroll **2026-10-30T00:14:18.937117Z** fant **ingen** bygge-/QEMU-/testprosesser. De native testede helper-/JS-/dropin-bytene og lifecycle-harnesset matcher sluttsourcen. Eksisterende Hermes-gateway/dashboard er ikke prosjektarbeider og stoppes ikke som tilfeldig opprydding.

Private bevis ligger i `overnight-20261029-224438/`: røde/grønne testlogger, JUnit, exact-head CI-logger, metadata/fjernfilkontroll, begge native fixturearkiver, bilde-/klientinventarer, artefakthasher, modell-/kostnadssnapshots og gjenopptakingskontrollpunkt. Ingen rå samtalelogger eller QA-hemmeligheter publiseres i Git.

## 12. Neste anbefalte handling

Eiergjennomgang av draft #39 og #40, deretter én avgrenset aksept i akselerert VM/fysisk klient: korrekt Super+Space→profilrad→Enter/Esc, alle fire profiler, synlig feilstatus og bevarte klienter på flere skjermer, samt timingportene. Eventuell integrasjon, ny ISO og fysisk testing krever egen beslutning; PR #38/M1 og øvrige draft-grener er ikke merget av denne økten.

**Arbeidet stopper etter C og sluttkvitteringen. Ingen ny milepæl, scheduler, worker eller automatisk oppfølging starter.**
