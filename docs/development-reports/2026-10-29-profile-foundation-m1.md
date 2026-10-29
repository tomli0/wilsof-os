# Wilsof OS — M1: Profile Foundation & CLEAN-kontrakt

Status: **implementert og testet kildeleveranse, klar for eiergjennomgang i draft-PR #38**. Ikke en GUI-, ISO- eller fysisk aksept. Ingen M2-oppstart.
Utvikling/nykontroll: 2026-10-29 fra 18:02 UTC; rapportgrunnlag kontrollert 18:29–18:32 UTC. Senere publiserings-/låskvittering føres på #16.

- Gren: `feat/profile-foundation-m1-20261029`.
- Autorisert base: `integration/internal-iso-20261026` @ `219894f1d4fc365b5e6546c2af9a146141634a1c`.
- Testet/publisert kode: **`e4aecd6f8d1259098a843a9b56d8a2a2fef00fce`**.
- [Draft-PR #38](https://github.com/tomli0/wilsof-os/pull/38), [status #16](https://github.com/tomli0/wilsof-os/issues/16), [avgrenset wallpaper-oppfølging #37](https://github.com/tomli0/wilsof-os/issues/37).
- [Sanert maskinlesbart testbevis](../qa/2026-10-29-profile-foundation-m1.json), [gjenopptakingspunkt](../checkpoints/profile-foundation-m1-20261029.md).

## Bevisgrunnlag og avgrensning

Før beskyttet arbeid ble faktisk GitHub-status #16 med alle ni daværende kommentarer, PR-/grenoversikt, lokale checkouts/worktrees, prosesser, låser og pausekontroller rekonstruert. Integrasjonen stod faktisk på `219894f`; PR #27 var OPEN/DRAFT. Produktplanen lå kun i draft-PR #36 @ `8e3324ef474b8fcd4a1be1ee973820dac2cdd95c`; Engineering Standards lå i #35 @ `a78d88790754886750bb1a5f93dd33cb257cc47e`. Ingen av disse grenene er endret.

De fire produktdokumentene og Engineering Standards ble lest i sin helhet. Bare de aktuelle dokumentene, rapporteringsstandarden og dens maler er tatt inn som eksplisitte snapshots på M1-grenen, ikke en merge av dokumentasjonsgrenene. Standard-/malfilene er byte-identiske med #35. Produktvisjonens opprinnelige 41-tegns, ugyldige SHA-token er dokumentert som kildefeil; faktisk base er verifisert separat, ikke stille «reparert» ved oppslag.

Siste internal2-rapport er lest ved eksakt integrasjonscommit. Originalt privat runtime-journalarkiv ble kontrollert read-only for wallpaper-avhengighetskjeden. Tidligere 13 VM-porter og Claude-review er historiske bevis, ikke gjentatte M1-tester. Nye M1-bevis er ekte fil-/CLI-/prosesstester, feilinjeksjon, statiske sjekker, syscall-smoke og CI. Ingen fysisk disk/USB, Proxmox, VM-oppstart, installasjon, ISO-bygg, merge eller release er utført. Private rålogger, traces og kontrollpunkt ligger i bevisgruppen `m1-20261029/`, ikke i offentlig Git.

## 1. Fullførte milepæler og CLEAN-kontrakt

Kun M1 er implementert:

- `bin/wilsof-profile`: selvstendig kjørbar fil, Python-standardbibliotek, `get`, `list`, `set clean|study|development|everyday`.
- CLEAN er standard uten fil; `get` er lesende og oppretter ingenting. Ugyldig fil gir `clean` på stdout, tydelig stderr og exit 1. Ugyldige argumenter gir exit 2 før filoperasjoner.
- `set` validerer eksisterende tilstand under lås og nekter å overskrive korrupt/usikker/fremtidig tilstand. Brukerens uttrykkelige arkivering før nytt `set` er dokumentert og testet uten tap av originalbytes.
- Versjonert lokal JSON, private rettigheter, atomisk erstatning, synkronisering og bounded skrivelås. Ingen ekstern avhengighet, root, nettverk eller ny bakgrunnstjeneste.

[CLEAN i UX §2.2/§2.6](../product/WILSOF_UX_SPECIFICATION.md) ble korrigert **før implementeringen**:

1. Ingen synlig Wilsof-dashboardflate, heller ikke fra tidligere profil; ingen ny dashboardprosess i CLEAN.
2. Andre brukerprogrammer lukkes/flyttes aldri automatisk; deres arbeid og oppgavedata endres ikke.
3. Tidligere dashboard kan leve skjult med usendt arbeid intakt. Fremtidig app-eid hide/show for alle egne toppnivåvinduer og dialoger, versjonert privat samme-UID-kanal, målrettet identitetskontroll og bekreftet skjuling er dokumentert. Ingen daemon, `pkill`, tittelglob, overlay eller masseflytting.
4. Opptatt arbeidsområde 1 beholdes urørt: dashboard starter/vises ikke der, flyttes ikke automatisk til et annet område, og stjeler ikke fokus. Senere eksplisitt åpnehandling lar brukeren velge et ledig område, med ny opptattkontroll.
5. M2/M4 må skille ønsket lagret profil fra faktisk anvendt synlighet; ingen falsk CLEAN-kvittering ved hide-feil. Dashboardets første mapping/reconnect må kontrollere siste profil. Dette er **kun kontrakt**, ikke M1-kode eller GUI-bevis.

Ingen launcher, dashboard, top bar, DMS-/Hyprland-endring eller automatisk installasjon er levert. CLI er testet både fra kilde og som kopi av bare filen. Eksisterende desktop-/installer-manifester beholdes uendret; distribusjonskobling må inngå eksplisitt i en senere godkjent milepæl.

## 2. Claude QA-funn og egen gjennomgang

**Ingen ny Claude-/annen uavhengig modellreview og ingen delegert utviklingsagent.** Én hovedagent har utført oppgaven. Den tidligere reviewen gjelder tidligere installerproduksjonskode, ikke M1. Ingen `[verified]`-/uavhengig-review-påstand er brukt for commit-en. Draft-PR #38 står til eiergjennomgang; sikkerhets-/release-reviewporter er ikke omgått.

Egen diffgjennomgang og testdrevet utvikling avdekket blant annet at en katalog-`fsync`-feil etter rename først fikk en misvisende «file preserved / CLEAN fallback»-sluttekst. En konkret rød test fanget det; rettelsen skiller lesefallback fra lagringsfeil og oppgir at ny profil kan være skrevet, med ukjent holdbarhet. Ingen test er svekket for å skjule feilen.

RED/GREEN: første fraværstest feilet fordi CLI manglet, deretter bestod den; lesing/listing/skjema feilet før implementasjon og ble grønne; fire faktiske `set`-tester feilet før lagring ble implementert. Sikkerhets-/konkurranse-/fault-testene ble deretter utvidet mot den kjørende komponenten. Testfixture for «gyldig tilstand» måtte eksplisitt sette trygge foreldremoduser fordi vertens umask ellers ga 0775; egne negativtester beholder og avviser nettopp 0775. Dette er dokumentert fixturekorreksjon, ikke lemping av produksjonskontrollen.

## 3. Tilstandsformat, dataintegritet og testresultater

Full normativ kontrakt: [WILSOF_PROFILE_STATE.md](../product/WILSOF_PROFILE_STATE.md).

    ~/.local/state/wilsof-os/profile.json
    {"profile": "clean", "schema_version": 1}

Maks 4096 byte UTF-8; nøyaktig to felt; versjon må være heltallet 1 (ikke bool/flyttall/streng); profil må være et av fire eksakte navn. Ekstra/dupliserte/manglende/feiltypede felt, ugyldig JSON, for stor/dypt nøstet fil og fremtidig versjon avvises. Ingen oppgaver/layout/appdata lagres.

Fil/lås/temp opprettes 0600, egen tilstandsmappe 0700. Eksisterende sikre 0755-tilstandsmapper kan innsnevres til 0700 ved `set`, ikke ved lesing. Andre foreldremapper chmoddes ikke; usikre gruppe-/verdensskrivbare mapper avvises. FD-relativ gange og `O_NOFOLLOW` avviser symlenker; regulær fil, korrekt eier, nøyaktig 0600 og én hardlenke kreves. FIFO åpnes nonblocking og avvises før lesing.

Skriving: behold samme låseinode, vent høyst 2 s, valider eksisterende fil, skriv unik `O_EXCL`-temp i samme mappe, flush/fil-`fsync`, `os.replace`, mappe-`fsync`. Siste vellykkede commit i låsrekkefølgen vinner. Samtidig lansering har ingen garantert schedulerrekkefølge; kontrollert konkurransetest beviser deterministisk resultat når låsrekkefølgen er fastlagt. En reell SIGKILL før rename beholder gammel tilstand; mulig privat orphan-temp verken brukes eller overskrives av neste kall. Ingen falsk rollback etter rename.

### Alle tolv etterspurte testkrav

| Nr. | Krav | Faktisk testbevis |
| --- | --- | --- |
| 1 | Manglende fil | `test_missing_state_is_clean_without_any_writes`: CLEAN/0, ingen opprettede filer. |
| 2 | Gyldig fil | `test_valid_state_selects_each_profile_without_rewriting`: korrekt profil, uendrede bytes. |
| 3 | Fire profiler | Parametriserte get/set-tester for alle fire, også faktisk lagringsformat. |
| 4 | Ugyldig profil | `test_strict_arguments_do_not_create_state`: navn, case, traversal, ekstra/manglende argumenter avvist. |
| 5 | Korrupt JSON | `test_invalid_state_is_clean_with_error_and_preserved_bytes` og arkiveringsflyt før set. |
| 6 | Ukjent versjon | Ukjent v2/v99 og ikke-heltall; ingen automatisk nedgradering ved eksplisitt set. |
| 7 | Feil felter | Manglende/ekstra/dupliserte felter og ugyldige typer; original beholdes. |
| 8 | Atomisk skriving | `test_atomic_replace_sync_order_and_old_open_reader`: fil-sync → samme-mappe rename → mappe-sync; gammel åpen leser beholder gammel komplett fil. |
| 9 | Rettigheter | 0600/0700, permissiv umask, eldre 0755, usikre moduser, symlenker, hardlenke, FIFO og katalog. |
| 10 | Avbrudd/bevaring | Injisert write/fsync/rename-feil og reell SIGKILL før rename; gammel profil og orphan-bevaring verifisert. Post-rename syncfeil gir ærlig feilstatus. |
| 11 | Samtidighet | To reelle skrivere med kontrollert lock/rename-barriere, busy-timeout, pluss tolv konkurrerende skrivere med aktiv rå-JSON-leser. |
| 12 | Ingen uventede sideeffekter | `test_no_changes_outside_state_directory`: DMS-, Hyprland-, oppgave- og dokumentfixture uendret i bytes/modus/mtime; bare profil/lås lagt til. Kopiert CLI kjører uten repo/grafikk. |

Faktiske sluttkjøringer mot den publiserte kodecommit-ens filhash:

- `python -m pytest tests/test_profile.py tests/test_profile_integrity.py tests/test_profile_boundaries.py -q`: **69 passed, exit 0**.
- `python -m pytest -q`: **270 passed / 1 skipped, exit 0**. Baseline uten nye tester hadde **201 passed / 1 skipped**. Den ene skippen er den eksisterende opt-in native Arch chroot-fixturen, ikke en profiltest.
- Begge ShellCheck-dialekter etter CONTRIBUTING, tre eksisterende JSON-konfigurasjoner, Python AST inkl. 3.12-grammatikk, lokale dokumentlenker, sikkerhetsmønstre på nye linjer og Git-diffkontroll: **bestått**.
- Isolert strace-smoke for get/list/fire set/get: **sju kall**, null nettverkssyscalls, kun initial interpreter-`execve`, ingen nye app-/desktopprosesser.

Lokalt brukes eksisterende QA-venv med Python 3.14.7 som vanlig UID1000. Første forsøk med vertens generelle Python manglet `jsonschema`; ingen pakke ble installert og ingen test endret for dette — riktig eksisterende venv ble brukt. En execute-kernel-kjøring arvet dessuten en uvedkommende Hermes/anyio-plugin via PYTHONPATH og ga én deprecation warning; råloggen er bevart. Endelig prosjektisolert kjøring uten kernelens injiserte PYTHONPATH/PYTHONHOME/VIRTUAL_ENV hadde ingen warnings. CI bruker ren Python 3.12 og bestod samme suite. Ingen ny Ruff/mypy-avhengighet ble installert; AST, ShellCheck og egen kildegjennomgang er de faktisk utførte statiske kontrollene.

## 4. Commits og faktisk CI

| Commit | Rolle | Kontrollert resultat |
| --- | --- | --- |
| `219894f1d4fc365b5e6546c2af9a146141634a1c` | Uendret autorisert integrasjonsbase | Git/remote/PR27 verifisert på nytt, ikke M1 levert til base. |
| `e4aecd6f8d1259098a843a9b56d8a2a2fef00fce` | M1-kode, tester, kontrakter og CI-filter | [Validate 40931174013](https://github.com/tomli0/wilsof-os/actions/runs/40931174013): **completed/success**; eksakt head kontrollert; logg viser **270 passed / 1 skipped** på Python 3.12. |
| Etterfølgende rapport-/beviscommit | Denne rapporten, sanert JSON og kontrollpunkt | Eksakt remote-head, alle publiserte blobs og ny head-CI kontrolleres etter push og kvitteres på #38/#16; ikke antatt grønn på forhånd. |

Eksisterende Validate-jobb gjenbrukes. Filtrene omfatter M1-push og PR mot integrasjonsbase, slik at fravær av CI på dokumentasjons-/produktgren ikke forveksles med pass. Ingen ny CI-stack, scheduler eller review-workflow. Alle eksisterende tester og runtime-/installer-/desktopfiler er uendret; bare tre nye profiltestfiler er lagt til. Ingen merge.

## 5. Artefakter og ISO-identitet

**Ingen ny ISO bygget.** Leveranseartefaktet er den kjørbare kildefilen ved identifisert commit; størrelse og SHA256 finnes i sanert JSON og kan verifiseres mot eksakt Git-blob. Ingen installert/deployert revisjon på dagens skrivebord påstås.

Tidligere internal2-ISO, testdisker, firmware, kontrollpunkter og crash-/GUI-bevis er ikke endret eller slettet. Den historiske internal2-identiteten er fortsatt den tidligere rapportens, ikke M1:

- Fil: `wilsof-internal-2026.10.28-internal2-x86_64.iso`.
- ISO-kilde: `f7c39451e2ff00ae28b6eb2a1809b17ae29072fe`.
- Historisk størrelse: 2546053120 byte; SHA256 `dc4bfb3944767e743f858880d32b0d1179b5a6c629e5cfed68410e3a73a4f8d1`.

M1 har **ikke** repetert full ISO-/diskhashing eller tatt eldre VM-aksept som bevis for nye bytes. Ingen bevarte lab-røtter er kjørt.

## 6. Full installasjon og VM-vurdering

Ikke relevant for ren CLI-/filtilstand; oppdraget forbyr ny installasjon og ISO-bygg. Alle M1-kriterier kan testes headless med vanlige brukerprosesser og disponible mapper, inkludert faktiske avbrudd og konkurranse. Derfor er **ingen VM startet**.

UEFI, live-desktop, diskvalg, formatering, installer-exit, disk-only boot, normalt passord, app-/lås-/opplåsingsporter: **ikke kjørt i M1**, ikke omdefinert til pass. Native opt-in chroot-test krever separat miljø/autorisasjon og er ikke relevant for denne nye lokale profilkomponenten.

Lagring målt **2026-10-29T18:29:26.989346Z**: **106672062464 tilgjengelige byte = 99.34609985351562 GiB**. Ingen byggeplassallokering, disk-/LVM-/partisjons-/Proxmox-endring eller artefaktrydding. Ny måling etter publisering føres i sluttkvitteringen.

## 7. Oppstart og passordinnlogging

Ikke endret eller testet: ingen autostart, økt-, innloggings-, PAM-, locker- eller installerendring. M1 CLI fungerer med DISPLAY/Wayland/D-Bus/compositorvariabler fjernet og som selvstendig kopi. Dette beviser headless CLI, ikke grafisk innlogging eller fysisk klientaksept.

## 8. Åpne feil, wallpaper og begrensninger

[Wallpaper-analyse og testplan](../qa/2026-10-29-wallpaper-follow-up.md), [oppgave #37](https://github.com/tomli0/wilsof-os/issues/37).

R5-avhengighetsfeilen er bekreftet ved direkte lesing av originaljournalen: wallpaper-jobb `dependency` ved DMS status137, deretter automatisk DMS-restart. Tidligere forslag om `Restart=on-failure` + `After=` **alene er utilstrekkelig** for en jobb som aldri nådde ExecStart. Helperen har allerede begrenset IPC-retry. Minste foreslåtte separate rettelse er en feil-isolert, ikke-blokkerende ExecStartPost-aktivering fra eksisterende DMS-dropin etter READY; nødvendig `--no-block`, jobbkoalesering, bounded feil og logout må bevises i en isolert user-manager-fixture og senere autorisert VM. **Forslaget er ikke implementert eller runtime-verifisert.** Wallpaper-tjeneste, helper og DMS-dropin er uendret i M1.

R1-killer/årsak er ukjent; R2-dialog-/toolkit- og R3-live-hjelpekrasj har utilstrekkelig verifisert rotårsak. Ingen av dem er «fikset» av denne analysen. #27 forblir OPEN/DRAFT; #34, #30, #31 og øvrige installer-/stabilitets-/fysiske issues er ikke lukket.

Øvrige begrensninger:

- Ingen GUI-CLEAN-garanti er implementert; mekanismen og testportene er M2/M4-kontrakt.
- Ingen automatisk CLI-distribusjon til eksisterende skrivebord/ISO. Ingen launcher/bar/dashboard.
- Kun Linux/lokale POSIX-semantikker; ikke en sandbox mot root eller kompromittert samme UID/Python-runtime. Delte/nettverksfilsystemer og reelt strømbrudd er ikke sertifisert.
- Korrupsjon krever eksplisitt eierinspeksjon/arkivering; ingen automatisk migrering, opprydding eller rollback. Fast produktsti, ikke XDG-overstyring i M1.
- Prosjektlisens/release-, fysisk USB/input/GPU/Wi-Fi/lyd/suspend-, update/recovery- og øvrige eksisterende akseptporter består. Ingen ny fysisk klienttest er nødvendig for den rene M1-CLI-en, men fremtidig GUI må verifiseres separat.

## 9. Engineering Standards og dokumentasjon

Middels risiko: ny lokal, upriviligert tilstandsgrense; øvrige brukerdata og desktop er utenfor komponentens ansvar. Minste sammenhengende løsning: én 171-linjers CLI, små funksjoner, ingen klasser/framework/service eller nye runtime-pakker. API/tilstand og feilkoder er dokumentert før GUI-konsumenter innføres. Ingen generell refaktorering.

Engineering Standards og rapporteringsmalene er tatt inn uendret fra #35 for lesbar, selvstendig M1-PR; produktplanen fra #36 er presisert kun for kontrakt/avgrensning/kildefeil og wallpaper-forslag. Eksisterende integrasjons-/dokumentasjonsgrener og workspaces er bevart. Lokale lenker, sensitive mønstre og diff er kontrollert. Uavhengig review er ikke påstått; #38 forblir draft.

En større framtidig grense er eksplisitt dokumentert fremfor implementert: lagret ønsket profil er ikke det samme som bekreftet GUI-synlighet. M2/M4 trenger koordinert, feil-synlig avstemming før mapping og ved konkurrerende valg. Det er ikke grunn til å utvide M1 til en økt-daemon.

## 10. Dokumenterte API-/modellkostnader

Read-only usage-snapshot **2026-10-29T18:29:26.989173Z**, før siste rapport-/publiseringskall:

| Rolle | Registrert rute/kall | Kostnadsstatus |
| --- | --- | --- |
| Primærøkt | gpt-6.1-sol / openai-codex, **53 kall** | `billing_mode=subscription_included`, `cost_status=included`, estimated_cost_usd=0. Aggregate actual_cost_usd er **null/ukjent**, ikke revidert 0-faktura. |
| Tittel | Samme modell/provider, **1 kall** | Lagrede kostnadsfelt 0, separat cost_status mangler. Ikke en betalt reviewrute. |
| Ny reviewer/delegasjon/fallback | Ingen barnesession eller slik rute i snapshot-et | **0 nye review-/utviklingsagenter**, ingen bestilt betalt modellrunde. Tidligere Claude-kostnad tilhører forrige oppdrag. |

Primærens registrerte tokenfelt: input 285208, output 38058, cache-read 9339264, cache-write 0, reasoning 8281. Feltene er separate og skal ikke ukritisk summeres; modellrader og sesjonsaggregat er heller ikke to ulike regninger. Publisering øker antall kall etter snapshot-et. Ingen ny betalt tjeneste, providerbudsjettprobe, modellruting, kredittgrense eller påfylling er endret. Samlet månedsfaktura/prosjektforbruk i NOK er ikke dokumentert av dette snapshot-et. Eksisterende konfigurasjonsidentitet er bevart i privat kontrollpunkt.

## 11. Prosesser, prosjektlås og pausekontroller

Eksisterende eksklusiv prosjekt-`flock` ble tatt før worktree/oppretting/utvikling av persistent hovedagents execute-kernel (eier-PID **339577**). Konkurrerende nonblocking-probe bekreftet busy mens arbeidet pågikk. Ingen lås fra annen agent ble overstyrt. Alle nye testsubprosesser er synkrone/disponible og avsluttet; ingen QEMU, mkarchiso, installer eller ny worker er startet. En eksisterende gateway og historisk gpg-agent er ikke behandlet som aktive utviklere eller avsluttet.

Ved rapportskriving holdes låsen fortsatt gjennom verifisert GitHub-publisering. **Faktisk frigivelse og påfølgende tilgjengelighetsprobe skjer først etter avsluttede beskyttede operasjoner og kvitteres på #16 og i privat kontrollpunkt**; rapporten forhåndserklærer ikke frigivelse.

Wilsof-jobb `8df95a6101e7`: **enabled=false / state=paused**. Separat worker-kontroll: **paused=true / stop_requested=false**. Ingen scheduler/worker er resumert eller opprettet. Originale grener og registrerte worktree-heads ble kontrollert før push; endelig kontroll utføres i sluttkvitteringen. Ingen M2-oppstart.

## 12. Anbefaling og neste beslutning

**Anbefal M1 godkjent som avgrenset kilde-/CLI-milepæl etter eierens gjennomgang av draft-PR #38 og endelig eksakt-head CI-kvittering.** Ikke godkjenn det som ferdig grafisk profilopplevelse, ISO-integrasjon eller uavhengig sikkerhetsreview. Ingen kjente lokale test-/CI-blokkere i kodecommit-en.

M2 kan **planlegges**, med CLEAN-kontrakten, skillet ønsket/anvendt profil, opptatt arbeidsområde 1 og distribusjonskoblingen som eksplisitte akseptkrav. Implementering krever en separat eierbeslutning og skal ikke starte automatisk. Wallpaper #37 er et separat avgrenset stabilitetsspor, ikke en skjult del av M1 eller en forklaring/lukking av R1–R3.

## Publiseringskvittering

Rapport-/beviscommit følger den allerede verifiserte kodecommit-en. Etter faktisk push leses eksakt fjern-head og hver levert Git-blob tilbake, draft/base/head og alle rapporterte CI-kjøringer kontrolleres, og #16/#38 får direkte rapportlenke, slutt-SHA, faktisk prosess-/låstilstand og nyere lagringstall. Dette hindrer et selvrefererende rapportcommit-løp og skiller første kode-CI fra senere publiserings-head. Historikk, #27 og øvrige åpne issues beholdes. Ingen ny milepæl startes.
