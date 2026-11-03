# AS-02 — direkte native konsollverifikasjon, 3. november 2026

Status: DELVIS BESTÅTT. Første DMS-låseisolasjon, PAM-autentisering og funksjonell input etter opplåsing er verifisert. Umiddelbar relås og DMS-livssyklus er IKKE KJØRT. Full AS-02-aksept er ikke gitt. Uavhengig sikkerhetsreview PENDING; Integration3 NO-GO.

## 1. Fullførte milepæler og bevisgrunnlag

Videreført [forrige rapport](2026-11-03-as02-final-harness-attempt.md) fra `e6ed46d5386f39df1314ef7485472adf0a9ebf1f` og det private kontrollpunktet. Tidligere minimal native A/B PASS er bevart som historisk separat bevis, ikke gjentatt eller erstattet av denne økten.

Én ny disponibel QEMU COW-gjest, disk-only UEFI-oppstart, vanlig greeter/PAM-innlogging og eksakt eksisterende privat compositorpakke. Ingen akseptanseharness kjørt eller endret. Direkte QMP-tastatur/skjermbilder, QGA-skall, DMS IPC, native protokolljournal og uavhengig native låseeierskapskontroll ble brukt. Nye observasjoner er fra 3. november 2026, omtrent 11:49–12:03 UTC. Detaljerte logger og skjermbilder er private.

## 2. QA-funn og avgrenset stopp

Ingen ny Claude-review, reviewer eller betalt agent. Den tidligere umiddelbare `visible=false`-observasjonen er ikke en varig åpnefeil: vanlig snarvei åpnet faktisk Command Center. I denne kalde TCG-økten kom en vellykket synlighetsobservasjon omtrent 41 sekunder etter snarveien; IPC- og framebufferoppdateringer var merkbart forsinket. Systemd var fortsatt `activating/start` mens funksjonen virket. Dette er observerte forhold, ikke en full rotårsaksdiagnose av ytelse/notify.

Kontrollsekvensen stoppet etter normal opplåsing på et for strengt vertsassert som krevde eksakt tekst. Feltet gikk fra `recovered` til `recoveredinpuuut` etter ufarlig QMP-input, og senere skjermbilde viste samme tekst. Dette beviser gjenopprettet input, ikke en applikasjonsfeil. Ekstra repetisjon er observert; TCG er en plausibel forklaring, ikke uavhengig påvist årsak. Den opprinnelige feilkvitteringen og den korrigerte ettervurderingen er begge bevart privat. Ingen ny testrunde eller boot for å omgå stoppet.

## 3. Kodekvalitet, sikkerhetsstatus og testmatrise

| Port | Resultat i denne økten | Direkte bevis / begrensning |
| --- | --- | --- |
| Normal Command Center operation | PASS | Super+Space, faktisk tegnet panel, owning visible=true; `control` til `controlinput` med QMP og senere samsvarende skjermbilde |
| Locked IPC input isolation | PASS, avgrenset til observert DMS-klient og første låseintervall | Native lås sikret, aktivering via eksisterende IPC, uendret søk, 0 nye native keyboard.enter og 0 keyboard.key til sporet DMS-klient |
| Hyprlock authentication | PASS | Feil syntetisk passord avvist med lås beholdt; korrekt syntetisk passord ga PAM-autentisert normal opplåsing og locker-exit |
| Unlock recovery | PASS | Synlig Command Center tok imot ufarlige taster etter normal opplåsing; repetert bokstav dokumentert, ikke skjult |
| Immediate relock | NOT RUN | Kontrollsekvensen stoppet før dette trinnet |
| DMS lifecycle checks | NOT RUN | Ingen DMS-restart under lås eller eksplisitt IPC-frakobling/gjenoppkobling |

DMS/plugin-lastingen og positiv native keyboard.enter/key-kontroll under ulåst input er beholdt. Den komplette sikret-til-autentisert-perioden ble kontrollert i etterkant: fortsatt 0 ordinære enter/key-hendelser i DMS-sporet, også under autentiseringsforsøkene. Privat compositorfokusdiagnostikk er lagret. Hyprlock var levende, native låseeierskap ble uavhengig kontrollert før og etter sentinel, og den legitime lockeren mottok autentiseringsinput. Visuelt låsebilde alene ble ikke brukt som sikkerhetsbevis.

Dette er ikke en uttømmende tracing-garanti for enhver mulig ordinær klient: DMS/Command Center er den observerte ordinære klienten. Ingen ny alternativ Command Center eller minimal erstatningsklient ble startet. Ingen lock-passord ble sendt før den innledende zero-input-kontrollen. Ingen logger med lockerens rå tastetrykk ble aktivert.

## 4. Commits og CI

Kun denne sanerte rapporten legges til på `docs/as02-direct-console-20261103`, basert på `e6ed46d5386f39df1314ef7485472adf0a9ebf1f`. Produktkode, privat patch og gamle testfiler er uendret. Eksakt publisert head, rapportblob og CI-status leses tilbake og registreres i kontrollpunktet. Ingen CI-grønnstatus hevdes som følge av runtimeobservasjonene. Ingen merge, release eller endring av eksisterende PR-grener.

## 5. Artefaktidentitet og historisk ISO

| Felt | Faktisk kontrollert verdi |
| --- | --- |
| Privat pakke | hyprland-as02-private 0.57.0-1.1, x86_64; eksisterende arkiv, ikke publisert |
| Pakke byte | 53701518 |
| Pakke SHA256 | b81531b9cf70b9f372238539cd64ae7d2ad66b41f1fc429dec6e998c41873a1f |
| Kilde | 0aa6745f705f2c4b0a5004eb019ef76e5bbdb426 med eksisterende private kandidat |
| Kjørende ELF SHA256 | 8a4a88e1cfebe165f37b50a9a83cacb2632adce6a3bd66fef44b2365b0c0e096, også lest via kjørende prosess |
| Historisk ISO | wilsof-internal-2026.11.01-integration2-x86_64.iso |
| ISO byte | 2549536768 |
| ISO SHA256 | cfe0571664b69b94bb8f2aebe0121704aa3e8feb063b11270fee227debc95eec |
| Plassering | Eksisterende privat artefaktlager; ingen ny ISO eller offentlig pakke |

Pakke, kjørende binær og beskyttede originalartefakter samsvarer med tidligere kontrollpunkt. Ingen compositorrebuild, ISO-bygg eller ny pakkeinstallasjon.

## 6. Installasjonsresultat og disponibel disk

Ingen ny installasjon: bevart installert backing-disk ble brukt kun som COW-bakgrunn. Én ny privat overlay og separate firmwarefiler. Backing-disk ble sjekket offline før oppstart; ny overlay ble sjekket uten reparasjon etter verifisert QEMU-exit, exit 0 og ingen diskfeil. Ingen fysisk blokkdisk tilkoblet eller skrevet som testmål.

Full ISO-installasjon, live-skrivebord og nye installerporter er NOT RUN. Disk-only boot og vanlig innlogging i denne gjesten er PASS. Dette overfører ikke aksept til en ny ISO.

## 7. Oppstart, PAM og låsing

Vanlig konsollinnlogging til aktiv Wayland-brukerøkt er ferskt verifisert, ikke erstattet av administrativ runuser. Hyprlock ble startet direkte med eksisterende konfigurasjon. Native sikret-event, fortsatt låseeierskap, faktisk maskert låseflate, avvist feil passord, korrekt PAM-autentisering og normal locker-exit er separate bevis. Ingen tvungen opplåsing eller administrativ lockerterminering.

## 8. Gjenstående feil og begrensninger

Umiddelbar relås med låst IPC/input er IKKE KJØRT i DMS-integrasjonen. Gjentatte sykluser, DMS-restart under lås og eksplisitt Command Center IPC disconnect/reconnect er IKKE KJØRT. Første direkte Hyprlock-invokasjon er dekket; flere direkte invokasjoner er ikke det. Hypridle, logout/login, unormal lockerterminering og fysisk klient/hardware/GPU/input/suspend er ikke undersøkt.

Hyprland IPC-timeouts og treg tegning ble observert; årsak er ikke isolert. Ingen produktendring ble gjort for å skjule dette. Full native AS-02-integrasjon og uavhengig sikkerhetsreview er fortsatt PENDING, Integration3 NO-GO. Historisk minimal relås-PASS fyller ikke den nye DMS-relås-porten.

## 9. Engineering Standards og dokumentasjon

Prosjektets rapporteringsstandard og tolvpunktsmal følges. Separat dokumentasjonsgren, eksplisitt staging av én rapport og read-back av fjerninnhold; ingen eksisterende worktree eller PR overskrives. Issue #16 får et sanert sammendrag og commit-pinnet rapportlenke. Patch, pakke, VM-disk, credential, rå protokoll-/fokuslogger og sensitiv sårbarhetsdetalj forblir private. Ingen upstream-disclosure.

## 10. Modellforbruk og utførelsesgrense

Én hovedagent, oppgitt `gpt-6.1-sol` via `openai-codex`; ingen nye agenter, reviewers eller betalte tjenester. Fakturert kostnad er ukjent, ikke hevdet null. Én QEMU-boot og åtte direkte kontrollbatcher; ytterligere aktivitet etter stoppet er bevislesing, sanering og avslutning, ikke nye runtimeforsøk. Ingen ny testframeworkutvikling eller endring av det gamle harnesset.

## 11. Prosesser, lås, scheduler og bevaring

Identitetskontrollert QGA powerdown er fullført; QEMU exit 0 og prosessen er uavhengig bekreftet borte. Prosjektlåsen var arvet av gjesten og beholdt til exit. Etter offline disk-/hashkontroll ble den sluppet, og tilgjengelighet ble probet. Dokumentasjonspublisering bruker kortvarig samme lås. Worker er fortsatt paused; Wilsof scheduler er enabled=false/state=paused.

19 beskyttede hashverdier er uendret, inkludert originaldisker, firmware, privat pakke, historisk ISO, tidligere forsøksdisk og gammelt harness. Ingen historiske artefakter slettet. Privat bevisrot: logisk `wilsof-qa/as02-native-20261103/direct-console/`; kontrollpunkt: `wilsof-qa/as02-native-20261103/checkpoint.json`.

Lagring ved 2026-11-03T12:03:31.816268+00:00: 45400637440 tilgjengelige byte (42.283 GiB). Endelig publiseringskvittering og lås-/prosessstatus registreres privat etter read-back.

## 12. Neste anbefalte handling

Separat autorisert, avgrenset fullføring av manglende DMS-relås- og livssyklusporter; ikke nye frameworkendringer eller rebuild. Uavhengig sikkerhetsreview må deretter faktisk gjennomføres før AS-02-aksept. Ingen ny gjest, arbeider eller scheduler startes automatisk. Fysiske klienttester er fortsatt eierens separate port.
