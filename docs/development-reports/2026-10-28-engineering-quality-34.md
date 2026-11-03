# Wilsof OS — Engineering Quality Milestone #34, 28. oktober 2026

**Status: A–D implementert og lokalt verifisert; kontrollert stopp ved blokkert uavhengig Claude-review. Ikke full milepæl-/ISO-aksept.**

Arbeidet startet 2026-10-28 kl. 19:20 UTC. Rapportgrunnlag og lagring ble oppdatert kl. **20:09:12 UTC**; endelig publiserings-, CI- og låsekvittering gis i [status-issue #16](https://github.com/tomli0/wilsof-os/issues/16). Integrasjonsgren: `integration/internal-iso-20261026`. Kodeleveranse: **`f628884b314dd13c3bf9d7059eee2fefec1b3400`**, [draft-PR #27](https://github.com/tomli0/wilsof-os/pull/27). [Issue #34](https://github.com/tomli0/wilsof-os/issues/34) holdes åpen.

## Bevisgrunnlag og avgrensning

- Tidligere rapportert/verifisert: installerrettelsen `b3b8e74ea5e6b8513d9bfde27b7d672921a43839`, senere integrasjons-head `9aebacdd82072257f57c0c31d17a1f7f600a4acb`, historisk GLM-/Claude-review og mislykket `internal1`-installasjon. Se [full historisk 12-punktsrapport](https://github.com/tomli0/wilsof-os/blob/1910e80d50573ab4bba83e2884f1d44ebae81ffa/docs/development-reports/2026-10-28-autonomous-session.md).
- Lagringsgrunnlag: [kontrollert opprydding og bevaring](https://github.com/tomli0/wilsof-os/blob/a78d88790754886750bb1a5f93dd33cb257cc47e/docs/development-reports/2026-10-28-storage-cleanup.md). Den lille marginen over 25 GiB måtte måles på nytt; ingen gammel byggerot ble behandlet som komplett runtime.
- Kontrollert i denne oppgaven: aktuelle PR-/issue-heads, standardene fra PR #35, worktrees, prosesser, prosjektlås og pausekontroller; nye atferdstester, native integrasjon, statiske sjekker, faktisk CI og ISO-identitet.
- Ikke utført: nytt ISO-bygg, VM-installasjon, fysisk disk-/USB-/Proxmox-operasjon, merge, release eller ny betalt modellreview. Ingen parallelle utviklingsagenter og ingen modellkonfigurasjonsendring.
- Private bevis beholdes i den varige QA-kontrollpunktgruppen `engineering-quality-34-20261028`: RED/GREEN-logger, native-rapport, fixture-manifester og revisjoner, mutasjonsresultater, kildearkiv/diff, budsjettgate og GitHub-/CI-kvitteringer. Rå samtaler, legitimasjon og private serveropplysninger publiseres ikke.

## 1. Fullførte milepæler

| Tiltak | Resultat og bevis | Begrensning |
| --- | --- | --- |
| **A. arch-install-scripts** | Eksplisitt pakke i `iso/packages.x86_64`. Generert customization kjører alltid `verify_arch_chroot_support()`, også uten lokal pakke, før eventuell installasjon. `pacman -Q`, ekte `vercmp` og faktisk `arch-chroot -r -h` kreves. Native verifisering brukte **31-2**. | Støttet baseline er konservativt **>=31**, ikke en påstand om første release med `-r`. Ny ISO må fortsatt bygges separat for å få inn denne gaten. |
| **B. Resolver-postbetingelse** | Reell midlertidig target-filstruktur brukes ved kjøring av `provision-target.main()`. Korrekt, også dangling, systemd-resolved-symlenke bevares. Feil lenke, vanlig fil, manglende fil og katalog avvises etter transaksjonen. Kommando-feil beholder exit 17, også ved resolver-skade eller inspeksjonsfeil. | Ny produksjonskontroll gjelder installert desktop-provisioning, ikke live-modus. Native-testen kontrollerer dessuten resolver under og etter ekte chroot/Pacman. |
| **C. install_package(Path('/'))** | Ni fullflyttilfeller dekker direkte Pacman-argv, ingen nesting, eksakte kopierte bytes/modus, allerede innbygget pakke uten selvkopiering, ugyldig/manglende pakke, symlenker, exit 27 og feil installert binær. Ingen fallback. To mutanter, tvungen nesting og utelatt pakkevalidering, ble faktisk avvist. | `/` sine filoperasjoner omdirigeres til en reell midlertidig rot i enhetstesten. Eksisterende separat kommandotest bruker ekte Path-semantikk; vertsroten berøres ikke. |
| **D. Ekte arch-chroot-integrasjon** | Repositoryets opt-in-inngangspunkt er kjørt: **2 passed**. Uendret upstream-script, ekte Arch Pacman, API-mounts, resolver, lokal pakkeinstallasjon, ugyldig pakke, kommando-exit 23, injisert sysfs-feil og teardown kontrolleres. Ingen blokknoder eksponert, container fjernet. | Rootless containerlab, ikke en full installasjon. Lab-only dev/sys-bind er uttrykkelig beskrevet nedenfor; dette er ikke fysisk devtmpfs-/maskinvareaksept. |

**Samlet:** alle fire ønskede kode-/testtiltak er levert, men ny uavhengig review av disse endringene er ikke gjennomført. De markeres ikke som review-godkjent.

## 2. Claude QA-funn og utbedringer

Historisk Claude Sonnet 4.6-review gjelder **`b3b8e74`**, ikke denne nye leveransen. Den konkluderte uten blokkerende funn, men identifiserte disse oppfølgingene:

| Historisk funn | Vurdering/oppfølging nå |
| --- | --- |
| F02, low: transitiv/udokumentert arch-install-scripts-avhengighet | Tiltak A løser deklarasjon og kjørbar gate. En historisk detalj var feil: reviewet hevdet at `-r` først kom i v28. [Faktisk oppstrøms v28](https://github.com/archlinux/arch-install-scripts/blob/v28/arch-chroot.in) har `getopts ':hNu:'` uten `r`. Denne oppgaven bruker derfor testet baseline >=31 og ekte opsjonsparsing, ikke den historiske påstanden. |
| F04, low: resolver-postbetingelse mangler | Tiltak B legger til produksjonskontroll og atferdsbaserte suksess-/feiltester; D kontrollerer native-transaksjonen. |
| F09, medium: manglende full `/`-flyt, ekte wrapper, resolver og provisioning-flyt | Tiltak A–D dekker de etterspurte kontraktene. Native-porten er med vilje ikke automatisk aktiv i vanlig CI. |
| F11, low/ubekreftet: skjør negativ kilde-/teksttest | Den gamle teksttesten er erstattet av faktisk `main()`-kjøring og eksakt observert prosessgrense. |
| F07, teoretisk/ubekreftet device-eksponering; F08, low: delt live `/run` | Ikke skjult som løst i produksjon. Upstream-grensen består; laben isolerer devices og dokumenterer at `/run` deles under transaksjonen. |
| F01/F03/F05/F06/F10, info | Historisk vurdering av kommando, `-r`, diskvern, feilpropagering og input/symlenker beholdes som historisk. Ingen ny uavhengig godkjenning av endrede bytes hevdes. |

### Ny review er blokkert før dispatch

Eksisterende konfigurerte rute er **OpenRouter / `anthropic/claude-sonnet-4.6`**. Bare den eksisterende nøkkelens kostnadsgate ble lest, uten å skrive nøkkel eller hente modellgenerering. Den viste **50 USD månedlig grense**, **47,734092261 USD registrert månedsforbruk** og **2,265907739 USD gjenværende**, reset **1. november 2026 kl. 00:00 UTC**.

Dette dokumenterer ikke Engineering Standards' **samlede 300 NOK/måned**, valuta-/flernøkkelkontroll eller deaktivert automatisk påfylling. Derfor ble **ingen ny betalt Claude-review sendt** og ingen alternativ modell/fallback brukt. Blokkeringen er kostnads-/akseptkontrollen, ikke et oppdiktet Claude-funn. Gammel review kan ikke overføres til `f628884`.

## 3. Kodekvalitet og sikkerhetsstatus

Produksjonsendringen er avgrenset til eksplisitt pakke, avhengighetsgate/customization og resolver-postbetingelse. `installer/wilsof_installer.py`, diskvalg, blankhet/identitet/bekreftelse, autentisering og de virkelige pakke-/binærpinnene er uendret. Ingen CheckSpace-, signatur- eller DownloadUser-omgåelse er lagt til.

Nye tester ligger i `test_chroot_contract.py`, `test_arch_chroot_integration.py` og `tests/integration/`. [Native-runbooken](../native-chroot-contract-test.md) beskriver kommandoer, tillitsgrenser og reproduksjon. Testadapteren inngår ikke i `runtime/image-files.txt`.

Native-isolasjon ble bekreftet før privilegerte transaksjoner: rootless user namespace uten host-root-mapping, eksakt avgrensede capabilities (`SYS_ADMIN`, `SYS_CHROOT`, `SETUID`, `SETGID`, `CHOWN`), ingen `MKNOD`/rådisk-capability, ingen blokknoder, read-only image-rot, ingen verts-home/socket og kun loopback. Ingen `--privileged`. Testdata ligger i disponible tmpfs-er; ressursgrenser er én CPU, 384 MiB og 128 prosesser. Sikkerhetsprofilene for mount-laben er avgrenset til denne rootless-containeren, ikke endret på verten.

Upstream-wrapperens SHA256 er **`56c50ac2f6d58325d4f5eaa0a0e359ca3019bffe08b7b37468de3bddae09e8d5`**. Labens mount-adapter bruker isolert Docker `/dev`-bind i stedet for global devtmpfs og read-only container-`/sys`-bind i stedet for ny sysfs. Resten av API-oppsett og upstream teardown kjøres faktisk. Slike lab-substitusjoner er ikke produksjonsrettelser eller bevis på fysisk device-sikkerhet.

Native-resultat: API-mounts for proc/sys/dev/devpts/shm/run/tmp til stede; installasjon exit **0**, ugyldig pakke exit **1**, eksplisitt kommando-feil **23**, injisert API-oppsettfeil **1**. Symlenke og opprinnelig resolver-data er bevart, registrerte API-mounts er borte etter hver suksess/feil, og den eide lab-containeren er fjernet. Den syntetiske pakken har ingen hooks/avhengigheter; testens lokale hash-overstyringer endrer ikke produksjonspinnene eller bygger virkelig Hypridle på nytt.

Oppsettet av den minimale fixturen avdekket konkrete miljøforutsetninger: SFS-kataloger med 0555, tmpfs som krevde eksplisitt exec, `ALPM_DB_VERSION=9`, alpm-identitet og nødvendig `CHOWN` for Pacmans DownloadUser-cache. Disse ble rettet i disponibelt testmiljø, ikke ved å svekke kontrollene. Feilforsøkene er bevart. Den **siste komplette uttrekkshjelperen er kjørt**; manifestet med **62 filer og 52 lenker** samsvarer eksakt med den bevarte native-testfixturen. Uendrede sync-databasevarsler i offline-fixturen er ikke nettverksnedlasting eller mislykket installasjon.

RED/GREEN-bevis finnes for ny gate og resolver-kontroll, inkludert opprinnelig feilstatus ved inspeksjonsfeil. Root-regresjonen verifiserer eksisterende korrekt atferd, supplert med de to faktisk feilede mutasjonsprobene. Begrenset hemmelighets-/injection-/privatsti-scan av staged tillegg fant ingen treff; dette er ikke en full sikkerhetssertifisering.

## 4. Commits og CI-status

| Revisjon | Rolle | Faktisk verifikasjon |
| --- | --- | --- |
| `9aebacdd82072257f57c0c31d17a1f7f600a4acb` | Ren integrasjons-head ved start | Tidligere [CI 40697951215](https://github.com/tomli0/wilsof-os/actions/runs/40697951215) lest tilbake som success; ikke en ny test av milepælen. |
| **`f628884b314dd13c3bf9d7059eee2fefec1b3400`** | A–D og native-runbook, 10 eksplisitte eide filer | Commit/push og GitHub-tree for alle ti blobs kontrollert. [Eksakt-head CI 40760360240](https://github.com/tomli0/wilsof-os/actions/runs/40760360240) **success**, avlest 20:08 UTC. CI-logg viser **201 passed, 1 skipped**. |
| Påfølgende dokumentasjonscommit | Denne rapporten og sanert kontrollpunkt | Ingen nye produksjonsendringer. Dens eksakte SHA/remote-innhold og eventuell egen head-CI kvitteres i status-issue etter faktisk publisering; denne rapporten gir ikke seg selv en oppdiktet commit-ID. |

Lokalt kjørt, exit **0**:

- `python -m pytest tests/ -q`: **201 passed, 1 skipped**. Native-porten er eksplisitt hoppet over uten opt-in.
- Opt-in `python -m pytest tests/test_arch_chroot_integration.py -q`: **2 passed**. Isolasjonsenhetstesten overlapper standardsuiten; tallene skal ikke ukritisk summeres til 203 unike tester.
- Begge ShellCheck-kommandoer i `CONTRIBUTING.md`, med prosjektets sh/bash-dialekter.
- JSON-validering av shortcuts, DMS-settings og tema; kompilering av endrede Python-innganger; `git diff --check` og staged diff-kontroll.
- Komplett sluttversjon av fixture-uttrekk, med byte-/lenkemanifest som samsvarer med kjørt native-grunnlag.

CI-workflowen kjører ordinær suite, JSON og ShellCheck for PR mot main. Den **kjører ikke native opt-in automatisk**, og grønn CI erstatter ikke manglende Claude-review. PR #27 og #35 var **OPEN/DRAFT**, issues #34 og #16 **OPEN**, ved ny lesing. Main var uendret på **`d4cb093ec2e6040a5d548c24c62a5ba26fb72a94`**. Ingen merge, force-push eller release.

## 5. ISO-filnavn, størrelse, SHA256 og plassering

| Felt | Bevart artefakt, ikke ny leveranse |
| --- | --- |
| Filnavn | `wilsof-internal-2026.10.28-internal1-x86_64.iso` |
| Image-kilde | `98bda89c453365b9fc51a0b40ad4174c40b4af8a` |
| Størrelse | **2545111040 byte** |
| SHA256 | **`ab78770ce5c4c5fe8b7b913263ade47e4f2d8830a4ffbb6a38c935c9e9a45e83`** |
| Plassering | Privat bevart artefaktrot `internal-test-20261028-internal1/`; ingen offentlig ISO/release. |
| Ny kontroll | Eksisterende ISO ble checksum-verifisert og lest for minimale native-fixtures, uten endring av ISO-bytes. |
| Aksept | Historisk installasjon feilet; denne ISO-en inneholder ikke den senere installerrettelsen eller A–D. Ingen `internal2` er produsert. |

## 6. Resultat fra full installasjon

| Port | Status i denne oppgaven |
| --- | --- |
| Ny ISO-/UEFI-/live-oppstart | **Ikke kjørt**; ingen VM startet. Tidligere begrenset internal1-live-bevis er historisk. |
| Ny diskvalg-/formaterings-/installerkjøring | **Ikke kjørt**. Ingen disk, partisjon, testdisk eller firmware endret. |
| Full installasjon med exit 0 | **Ikke verifisert for rettet image**. Bevart internal1-installasjon feilet historisk med exit 1. |
| Disk-only boot uten ISO | **Ikke kjørt for rettet image**. |
| Vanlig passordinnlogging, installert desktop, lås/opplåsing, oppdatering | **Ikke kjørt for rettet image**. Native chroot er ikke erstatning. |
| Avslutning | Eide lab-containere avsluttet/fjernet; ingen gjest eller byggeprosess startet. Bevarte ISO-/disk-/firmwareartefakter urørt. |

### Faktisk lagringsstatus

Før arbeid: **26980790272 byte = 25,127819061 GiB**. Ny måling **2026-10-28T20:09:12Z**: **26770972672 byte = 24,932411194 GiB** tilgjengelig på byggfilsystemet. Netto reduksjon er **209817600 byte**; nye bevarte fixtures/logger/bevis inngår, men dette er ikke et eksklusivt fil-for-fil-regnskap for hele vertsaktiviteten.

Minimum **25 GiB = 26843545600 byte** er ved denne målingen **ikke oppfylt**: differanse **72572928 byte**. Foretrukket 30 GiB er heller ikke nådd. Ingen bevart ISO, testdisk, firmware, kontrollpunkt eller testbevis er slettet. Tidligere disk-/LVM-opprydding er ikke gjentatt, og ingen disk-/Proxmox-endring er forsøkt. Ny plasskontroll og en godkjent lagringsløsning kreves før et eventuelt senere bygg. Dette er reell tilgjengelig lagring, adskilt fra den opprinnelige misvisende mtab/CheckSpace-feilen i chroot.

## 7. Oppstart og passordinnlogging

Ingen ny aksept. Tidligere boot/login på eldre image og tidligere unprivilegert `runuser`-bevis overføres ikke til en fremtidig ISO. Denne oppgaven kjørte ikke vanlig greeter-innlogging, feil-passord-kontroll, autentisert opplåsing eller installert restart/persistens. Fysiske tastatur-/klient-, USB-/firmware-, GPU-, Wi-Fi-, lyd- og suspend-porter er fortsatt uprøvd innenfor denne leveransen.

## 8. Gjenstående feil og begrensninger

1. **Uavhengig Claude-review av `f628884` er blokkert før dispatch** på manglende dokumenterte samlede kostnadskontroller. Derfor ingen full review-/milepælaksept, selv om A–D består lokalt.
2. **Issue #34 forblir åpen:** separat godkjent nytt image må inneholde rettelsen og bestå installasjon, disk-only boot og vanlig autentisering. Kildefiks eller syntetisk native-pakke lukker ikke feilen.
3. **Lagring er igjen under 25 GiB** ved rapportmålingen. Ingen automatisk opprydding eller bygg startes.
4. Lab-only dev/sys-substitusjon, namespace-/upstream-tillitsgrenser og delt live `/run` er dokumenterte begrensninger, ikke bortforklart fysisk sikkerhetsaksept.
5. Nye tester dekker kontrakten, ikke virkelig Hypridle-livssyklus eller ny installert GUI. Eksisterende #28/#29/#30/#31 og øvrige artefakt-/fysiske porter endres eller lukkes ikke av denne oppgaven.
6. Nyeste dokumentasjons-heads CI/publiseringskvittering må leses på den eksakte commit-en; eldre grønn CI skal ikke omtales som automatisk grønn for enhver senere head.

## 9. Engineering Standards og dokumentasjons-PR

Arbeidet følger [standardene fra den bevarte dokumentasjonsrevisjonen](https://github.com/tomli0/wilsof-os/blob/a78d88790754886750bb1a5f93dd33cb257cc47e/docs/ENGINEERING_STANDARDS.md): liten produksjonsrettelse, atferdstester, minste nødvendige lab-privilegier, opprinnelig feilstatus, faktisk verifikasjon og tydelige akseptgrenser. Standarden er ikke tolket som tillatelse til videre betalt arbeid når kostnadskravene mangler.

[PR #35](https://github.com/tomli0/wilsof-os/pull/35), `docs/engineering-standards-20261028`, head **`a78d88790754886750bb1a5f93dd33cb257cc47e`**, er fortsatt separat **OPEN/DRAFT** mot integrasjon. Dette worktreet er ikke endret eller merget. Rapporteringsstandarden og 12-punktsmalen fra denne grenen brukes uten å overskrive andre agenters arbeid. Denne rapporten og et sanert milepæl-kontrollpunkt publiseres på den autoriserte integrasjonsgrenen.

## 10. API-/modellforbruk der det kan dokumenteres

| Rolle | Faktisk omfang | Kostnadsstatus |
| --- | --- | --- |
| Hovedagent, Codex | Én hovedagent; utvikling, lokale verktøy og GitHub-publisering. Ingen parallelle utviklingsagenter. | Aktiv samtale bruker inkludert Codex-rute. En separat revidert oppgavefaktura/tokenfordeling er ikke etablert; ikke før hele den lange foreldresesjonen som kostnad for denne milepælen. |
| Ny Claude-review | **0 modelldispatcher / 0 nye Claude-genereringer**. Eksisterende QA-rute ble bare kontrollert. | **Ingen ny betalt QA-kostnad pådratt av en Claude-dispatch.** Budsjettgaten avviste oppstart. |
| OpenRouter-kostnadskontroll | Én read-only nøkkel-/budsjettprobe; ingen hemmelig verdi publisert. | Målt nøkkelstatus: 50 USD/mnd, forbruk 47,734092261 USD, igjen 2,265907739 USD. Dette er måneds-/nøkkelstatus, **ikke** milepælens kostnad eller en NOK-omregning. |
| Tidligere GLM/Claude | Tidligere review av `b3b8e74`; historiske estimater i den lenkede fullrapporten. | Ikke kjørt eller belastet på nytt her; estimater må ikke fremstilles som faktiske nye kostnader. |

Samlet prosjektgrense i NOK, øvrige nøkler, automatisk påfylling og nøyaktig ekstern fakturering er ikke sertifisert. Ingen fallback, ny tjeneste eller automatisk modellretry er startet.

## 11. Aktive prosesser og prosjektlåser

Ved avslutningskontroll var ingen `qemu-system`, mkarchiso, arch-chroot/Pacman-transaksjon, Wilsof-worker, bygg eller Claude-dispatch aktiv. Bare hovedøkten utførte synkron publisering. Eide lab-containere var fjernet; to eldre, allerede stoppede andre containere ble ikke berørt.

Prosjektets eksisterende eksklusive lås ble tatt før arbeid og var fortsatt holdt av hovedøkten under kilde-/rapportpublisering; konkurrerende probe returnerte **75 / busy** som forventet. Den er ikke en glemt gjestelås. Etter siste push og kontroll av at ingen beskyttet prosess lever, slippes bare denne øktens lås; faktisk tilgjengelighetsprobe og tidspunkt registreres i det private kontrollpunktet og den endelige GitHub-statuskvitteringen.

Wilsof-jobb **`8df95a6101e7`** er **enabled=false / paused**. Separat worker-kontroll er **paused=true, stop_requested=false**. En allerede kjørende Hermes-gateway er ikke en aktiv prosjektarbeider. Ingen scheduler, jobb eller worker er startet/resumert, og ingen ny bakgrunnsoppgave er opprettet.

## 12. Neste anbefalte handling

**Avklar og dokumenter kostnadskontrollen før én avgrenset, uavhengig Claude-review av den identifiserte kodecommit-en.** Det innebærer samlet månedsramme i NOK og påfyllingssperre eller en uttrykkelig eierbeslutning om godkjent rute/ramme. Ikke behandle nøkkelens 50 USD-grense som bevis på 300 NOK-policyen og ikke bestill review automatisk.

Deretter krever eventuell ISO-milepæl fortsatt separat byggetillatelse, frosset reviewet kilde og ny plassmåling som oppfyller minimum. Ny ISO, installasjon, fysisk klienttest og øvrige porter er ikke startet.

## Publiseringskvittering

Kildecommit og dens CI er allerede lest tilbake fra GitHub. Den påfølgende rapport-/kontrollpunkt-commit-ens eksakte URL, fjernverifikasjon, CI og avsluttet låsestatus gis i PR #27, issue #34, [status #16](https://github.com/tomli0/wilsof-os/issues/16) og terminalen etter faktisk push/read-back. Det private kontrollpunktet får endelige SHA-/kommentar-ID-er. Dette unngår en selvrefererende commit-løkke og påstår ikke publiseringssuksess før den er verifisert.
