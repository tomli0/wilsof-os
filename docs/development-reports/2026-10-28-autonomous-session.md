# Wilsof OS — fullstendig sluttrapport, autonom økt 28. oktober 2026

**Hovedstatus:** Installerrettelsen er implementert, testet og uavhengig gjennomgått, men ikke verifisert i en ny ISO. Ingen `internal2` ble produsert. Den eksisterende `internal1` feilet installasjon og er ikke godkjent. Ingen merge eller offentlig release.

Denne rapporten rekonstruerer alle 12 punktene i sluttrapporten fra Hermes-sesjon `20261028_131138_b8e544`. Utviklingsøktens første melding er fra 13:13 UTC; den opprinnelige sluttrapporten er merket avsluttet 13:40 UTC. Samme sesjon inneholder også en kort statusforespørsel kl. 15:25 UTC. Dokumentasjonsoppfølgingen nedenfor er en separat, lesende statuskontroll og publisering, ikke en ny utviklings-/QA-økt.

## Bevisgrunnlag og tidsavgrensning

- **Historisk verifisert:** lagrede resultater fra den avgrensede installerrettelsen, begge review-rundene, den opprinnelige sluttrapporten og kontrollpunktet `autonomous-20261028-1311/checkpoint.json`. Disse testene er ikke kjørt på nytt for rapportens skyld.
- **Kontrollert på nytt 28. oktober 2026, ca. 15:34–15:38 UTC:** lokale grener/worktrees/commits, GitHub PR-er og issue-tråder, tre eksisterende CI-kjøringers faktiske head/conclusion, reviewfiler og dispatchmetadata, sesjonenes lagrede forbruksmetadata, eksisterende ISO-filnavn/størrelser og SHA256 for `internal1`, tilgjengelige byte, prosesser, prosjektlås og pausekontroller.
- **Ikke utført i rapporteringsoppdraget:** applikasjonskodeendringer, nye tester, modellreviews, ISO-bygg, VM-start, installasjon, fysisk disk-/USB- eller Proxmox-operasjon, merge, offentlig release eller aktivering av automatisering.
- Rå samtaler, providerlogger, dispatchskript, legitimasjon og private verts-/tilgangsdetaljer er ikke lagt i Git. Private bevis er referert med logiske kontrollpunktnavn. Rapporten er en sanert sammenstilling, ikke et råloggvedlegg.

## 1. Fullførte milepæler

1. Prosjektstatus ble gjenopprettet fra `pacman-chroot-fix-20261028`, med kontroll av eksisterende bevis, grener, worktrees, PR #27, status #16, bug #34, lås og pauset automatisering. Ingen beskyttet prosess var aktiv ved gjenopptakingen.
2. Uavhengig review av installerrettelsen `b3b8e74ea5e6b8513d9bfde27b7d672921a43839` ble gjennomført i to runder. Første runde hadde feil modellrute; den ble bevart og korrekt merket før det påkrevde Claude-reviewet ble gjennomført.
3. Engineering Standards og en teknologiuavhengig tilpasningsmal ble fullført på egen dokumentasjonsgren i commit `6947fd8261a9325781d56482a275b5eb61c6d600`, med separat draft-PR #35.
4. Status ble oppdatert på integrasjonsgrenen gjennom `b9330f5` og `9aebacd`, pushet og kontrollert mot eksakt-head CI. PR #27, issue #16 og #34 ble oppdatert og lest tilbake.
5. ISO-/installasjonsmilepælen ble **stoppet før oppstart**, ikke fullført: utilstrekkelig lagring. Kontrollpunkt, tidligere artefakter og bevis ble bevart; prosjektlåsen ble frigitt ved avslutning.

Kontrollert på nytt: integrasjon står fortsatt på `9aebacdd82072257f57c0c31d17a1f7f600a4acb`; dokumentasjonsgrenen var ren på `6947fd8` før denne rapporteringen. Ingen annen agents arbeid er overtatt eller overskrevet. Rapporten og rapporteringsstandarden leveres videre på PR #35s eksisterende gren; integrasjonsgrenen oppdateres ikke av dette dokumentasjonsoppdraget.

## 2. Claude QA-funn og utbedringer

### Modellruter og avvik

- **Runde 1 — GLM, ikke Claude:** `z-ai/glm-5.3`, 16 API-kall, 289,64 sekunder. Forelderens Codex-rute traff abonnementskvoten med HTTP 429 kl. 13:19:25 UTC og gikk automatisk til konfigurert GLM-fallback. Den upinnede delegasjonen arvet denne ruten. Den først feilmerkede reviewfilen ble korrigert til `glm53-qa-findings-fallback-route.json`. Resultatet ble ikke behandlet som oppfyllelse av Claude-kravet.
- **Runde 2 — påkrevd review:** `auxiliary.review` → `anthropic/claude-sonnet-4.6` via OpenRouter, pinnet med tom fallback-kjede; modellkonfigurasjonen ble ikke endret. 19 API-kall, 242,67 sekunder. Lagret resultat: `claude-qa-findings.json`; dispatch-resultatet viser fullført review, riktig modell og `no_blocking_findings`.
- Begge runder vurderte den samme, uendrede commit-en `b3b8e74`. Ingen kritiske eller høye funn ble bekreftet. Claude registrerte 11 funn: **1 medium, 4 lave og 6 info**. «Ingen blokkerende funn» betyr ikke at testdekningen eller ISO-akseptansen er fullstendig.

### Samtlige funn

| ID | Alvorlighet | Vurdering og konkret bevis | Status / oppfølging |
| --- | --- | --- | --- |
| F01 | Info | `runtime/pinned-package.py:19` bygger `arch-chroot -r TARGET ...` for eksterne mål. Upstream setter opp proc/sys/dev/run/tmp og registrerer EXIT-opprydding før første mount. Bare chroot forklarer den manglende API-konteksten. | Bekreftet korrekt mekanisme. Ingen kodeutbedring påkrevd av reviewet. |
| F02 | Lav | `arch-install-scripts` står ikke eksplisitt i ISO-manifestet; tilgjengeligheten er transitiv via `archinstall`. Reviewer verifiserte at `-r` krever versjon ≥ v28. Eldre/manglende wrapper feiler tydelig, men kan oppdages for sent. | Bekreftet avhengighets-/valideringsgap. Eksplisitt manifestføring eller bygg-gate anbefalt før neste ISO-aksept. |
| F03 | Info | `provision-target:77–80` setter resolverlenken før grensesnittkallet ved :81. `-r`/keepresolvconf hopper over upstream resolverendring. | Bekreftet korrekt rekkefølge og resolverbevaring. |
| F04 | Lav | Ingen atferdsassert etter transaksjonen kontrollerer at målrotens resolver fortsatt er den tilsiktede symlenken. Den aktuelle repotesten kontrollerer kildetekst, ikke filtilstand. | Bekreftet. Legg til resolver-postbetingelse eller eksplisitt lab-gate. |
| F05 | Info | `installer/wilsof_installer.py` er ikke endret i commit-en. Full-zero-skann, `O_NOFOLLOW`, wipefs-/holder-avvisning, stabil diskidentitet, mål-mountkontroll, eksakt ERASE-bekreftelse og umiddelbar reprobe er bevart. | Bekreftet uendrede sikkerhetskontroller; ikke ny installasjonsaksept. |
| F06 | Info | `check=True` i pakke-/provisjoneringskallene propagerer feil til installerens exit-1. Upstreams EXIT-trap rydder egne API-mounts også etter delvis oppsettfeil. En allerede kopiert verifisert pakke og delvis provisjonering kan bli igjen etter feil. | Bekreftet, ingen ny skjult fallback eller regresjon. Delvis installasjon skal ikke fremstilles som automatisk tilbakeført. |
| F07 | Info | Upstreams globale devtmpfs gjør live-miljøets blokknoder synlige inne i chroot under provisjonering. Standard enhetsrettigheter og uprivilegert desktop-kall begrenser tilgangen; ingen konkret datatapsvei ble påvist. | **Ubekreftet/teoretisk**, ikke en bekreftet utnyttelse. Labens minimale device-tmpfs er en uttrykkelig testbegrensning. |
| F08 | Lav | Upstream deler live-miljøets `/run` inn i target under transaksjonen. Resolveren bruker dermed live-resolved; runtime-tilstand opprettet der blir ikke varig målrotstilstand etter teardown. | Bekreftet upstream-atferd med transient påvirkningsmulighet, ikke en egen bekreftet datatapsfeil. Skal være dokumentert. |
| F09 | Medium | Repoets subprocess-kall er mocket. Ingen full `install_package(Path('/'))`-test, ingen ekte `arch-chroot`-integrasjon i repoet, ingen resolver-postbetingelse, ingen atferdstest av `provision-target` sin runuser-feil, skjøre kildestrengtester og ingen pakke-/wrapper-gate. Den andre vellykkede subprocess-argv-en er heller ikke separat assertet. | Bekreftede dekningshull. Historiske eksterne labresultater erstatter ikke vedlikeholdbare regresjoner. Fire prioriterte tiltak står nedenfor. |
| F10 | Info | Kommandoer er argv-lister uten shell-ekspansjon. Brukernavn valideres; target normaliseres; pakke-/binærhash og symlink-avvisning bevares; passord går ikke gjennom provision-target. Ingen gjenværende bar chroot i berørte runtime-/installer-kall. | Bekreftet ingen introdusert injeksjons-, symlink- eller passordregresjon innenfor reviewets omfang. |
| F11 | Lav | Ny Claude-observasjon: negativ test på den gamle bokstavelige chroot-strengen kan ikke alene fange en annen konstruksjonsform. En positiv grensesnittassert finnes, men dette er fortsatt kildestrengtesting. | Lagret som **UNCONFIRMED**, lav testdesign-observasjon, ikke dokumentert runtime-feil. Foretrekk atferdsassert i provisjoneringsflyten. |

Claude bekreftet GLMs F01–F06 og F08–F10; F07 forble teoretisk/ubekreftet. F11 ble lagt til av Claude. Ingen alvorlig bekreftet feil utløste ny kildeutbedring i utviklingsøkten. De fire prioriterte forbedringene ble registrert på [#34](https://github.com/tomli0/wilsof-os/issues/34#issuecomment-6470447362):

1. Eksplisitt `arch-install-scripts`-avhengighet eller byggkontroll av wrapper og `-r`.
2. Resolver-postbetingelse etter chroot-transaksjonen.
3. Test av hele `install_package(target=Path('/'))`-grenen.
4. Miljøavgrenset integrasjonstest med ekte `arch-chroot -r` mot disponibel rot.

Kontrollert på nytt: begge eksisterende funnfiler, Claude-dispatchens modell/fullføringsmetadata og reviewbarnas lagrede modell-/forbruksrader. **Ingen ny betalt QA-runde er kjørt.**

## 3. Kodekvalitet og sikkerhetsstatus

### Rotårsak og levert rettelse

Den tidligere `internal1`-installasjonen feilet fordi bar `chroot TARGET pacman -U ...` ikke monterte målrotens API-filsystemer. Archs `/etc/mtab -> ../proc/self/mounts` var intakt, men lenkens mål var utilgjengelig uten target `/proc`. Pacmans CheckSpace-feil var derfor misvisende; dette var **ikke** samme problem som rapporteringsøktens faktiske lagringsmangel.

Archinstall forbereder API-filsystemene for sine enkelte chroot-kall. Det oppsettet blir ikke automatisk arvet av et separat Wilsof `provision-target`. `b3b8e74` innførte derfor ett delt kommandogrensesnitt: `arch-chroot -r TARGET COMMAND...` for eksterne mål, direkte kjøring når roten allerede er den forberedte `/`. Ingen erstatning av mtab-lenken, CheckSpace-/signaturomgåelse eller egen mount-manager ble brukt.

### Historiske verifikasjoner — ikke kjørt på nytt

- RED/GREEN av relevant regresjon; 16 fokuserte pakke-/desktoptester og **175 tester totalt** besto før den autonome reviewøkten.
- ShellCheck, Python AST, JSON-validering og diffkontroll besto i rettelsesoppgaven.
- Den gamle helperen reproduserte faktisk mtab-/CheckSpace-feilen i en disponibel klonet Arch-rot med korrekt montert root og intakt symlink.
- Den rettede helperen utførte en ekte offline Pacman-transaksjon fra Hypridle `0.1.8-2` til `0.1.8-2.1`, exit 0; binærhashen matchet pinnen.
- Injisert sysfs-oppsettfeil propagerte uten pakkeendring/fallback; tidligere montert proc ble ryddet og resolveren bevart. API-oppsett/teardown, uprivilegert runuser-kontekst og forberedt `/`-gren ble kontrollert.
- Laben brukte private mount-/PID-/nettverksnavnerom og en minimal device-tmpfs i stedet for global devtmpfs for ikke å eksponere fysiske vertsblokknoder. Dette begrenser hva testen beviser om standard upstream-device-eksponering.

Se [det committede rettelseskontrollpunktet](https://github.com/tomli0/wilsof-os/blob/b3b8e74ea5e6b8513d9bfde27b7d672921a43839/docs/checkpoints/pacman-chroot-fix-20261028.md). Reviewet bekreftet minste privilegium, intakte checksum-/symlink-/disk-/passordgrenser og feilpropagering innenfor dette omfanget. Det er ikke en komplett sikkerhetssertifisering eller fysisk maskinvareaksept. Utviklingsøkten endret kun dokumentasjon; den nåværende oppfølgingen gjør også kun dokumentasjonsendringer.

## 4. Commits og CI-status

| Commit | Rolle / gren | Kontrollert resultat |
| --- | --- | --- |
| `b3b8e74ea5e6b8513d9bfde27b7d672921a43839` | Installerrettelse fra foregående avgrensede oppgave; integrasjon | [CI 40690753659](https://github.com/tomli0/wilsof-os/actions/runs/40690753659): completed/success, eksakt head bekreftet på nytt. |
| `b9330f593e0a0a76e042c64bd1ee4d04d67d9b55` | Første autonome statusoppdatering; integrasjon | [CI 40695558116](https://github.com/tomli0/wilsof-os/actions/runs/40695558116): completed/success, eksakt head bekreftet på nytt; testjobben 20 s. |
| `9aebacdd82072257f57c0c31d17a1f7f600a4acb` | Sluttkontrollpunkt/status; integrasjon | [CI 40697951215](https://github.com/tomli0/wilsof-os/actions/runs/40697951215): completed/success, eksakt head bekreftet på nytt; testjobben 23 s. |
| `6947fd8261a9325781d56482a275b5eb61c6d600` | Engineering Standards + tilpasningsmal; dokumentasjonsgren | Ingen rapporterte CI-sjekker for PR #35; dette er ikke «grønn CI». Tekst, lokale lenker og diff ble kontrollert i leveringsøkten. |

Den eksisterende Validate-arbeidsflyten kjører blant annet pytest, JSON, ShellCheck og diffkontroll. Triggerne er push til `arch-install` og PR mot `main`; PR #35 har integrasjon som base og utløste derfor ikke samme CI. Her er eksisterende kjøringer bare lest, ikke startet på nytt.

Kontrollert på nytt før rapportpublisering:

- [PR #27](https://github.com/tomli0/wilsof-os/pull/27): OPEN, DRAFT, head `9aebacd`, base `main`, ingen merge.
- [PR #35](https://github.com/tomli0/wilsof-os/pull/35): OPEN, DRAFT, dokumentasjonsgren `docs/engineering-standards-20261028`, base `integration/internal-iso-20261026`, ingen merge. Opprinnelig head `6947fd8`; rapportoppfølgingen tilfører bare dokumentasjon på denne grenen.
- [Issue #16](https://github.com/tomli0/wilsof-os/issues/16): OPEN, permanent statusdashboard.
- [Issue #34](https://github.com/tomli0/wilsof-os/issues/34): OPEN; reviewerens kommentar supplerer issue-kroppens eldre «review pending»-tekst. Ingen lukking uten faktisk ny-ISO-verifikasjon.

Dokumentasjonsgrenen startet fra en eldre integrasjonsbase og inneholder ikke i seg selv installerrettelsen. Rapporten peker derfor til eksakte integrasjonscommits for testbevis; ingen kode er flettet inn, fjernet eller tilbakeført som del av rapporteringen. Ingen merge til `main` eller `arch-install`, ingen force-push og ingen inngrep i README-arbeidet på #32/#33.

## 5. ISO-filnavn, størrelse, SHA256 og plassering

**Ingen ny ISO ble bygget i utviklingsøkten eller rapporteringsoppfølgingen.** `2026.10.28-internal2` var et planlagt versjonsnavn, ikke en fil eller levert artefakt.

Siste eksisterende ISO:

| Felt | Verdi |
| --- | --- |
| Filnavn | `wilsof-internal-2026.10.28-internal1-x86_64.iso` |
| Faktisk image-kilde | `98bda89c453365b9fc51a0b40ad4174c40b4af8a` |
| Størrelse | **2545111040 byte** |
| SHA256 | `ab78770ce5c4c5fe8b7b913263ade47e4f2d8830a4ffbb6a38c935c9e9a45e83` |
| Plassering | Privat lokal artefaktrot, under `internal-test-20261028-internal1/`; `manifest.json` og `SHA256SUMS` følger samme interne bunt. Ingen offentlig ISO-URL eller release. Eksakt lokal rot beholdes i privat kontrollpunkt. |
| Aksept | Installasjon FEILET, exit 1. Inneholder ikke `b3b8e74`; ikke godkjent for installasjon. |

Størrelse og full SHA256 er **kontrollert på nytt** med lesing av eksisterende fil. Den samme hashen ble også kontrollert ved utviklingsøktens avslutning. [Datert bygg-/immutable-auditspor](https://github.com/tomli0/wilsof-os/blob/75ad980f5d46985f45ff581376633e01556ec774/docs/checkpoints/internal-iso-build-20261028.md) gjelder kun disse image-bytene, ikke den senere rettelsen.

Tidligere filer finnes fortsatt, og størrelser er lest på nytt:

| Fil | Byte | Omfang av ny kontroll |
| --- | ---: | --- |
| `wilsof-internal-2026.10.26-x86_64.iso` | 2533040128 | Tilstedeværelse/størrelse; ikke ny checksum- eller oppstartstest. |
| `wilsof-internal-2026.10.26-stabilize1-x86_64.iso` | 2539548672 | Tilstedeværelse/størrelse; ikke ny checksum- eller oppstartstest. |
| `wilsof-internal-2026.10.26-stabilize2-x86_64.iso` | 2539565056 | Tilstedeværelse/størrelse; ikke ny checksum- eller oppstartstest. |

Ingen ISO, bevart testdisk, firmware eller tidligere testbevis er slettet eller overskrevet. De bevarte diskene/firmwarefilene er ikke åpnet som nye installasjonsmål eller hashverifisert på nytt i dette rapporteringsoppdraget.

## 6. Resultat fra full installasjon

For enhver planlagt **post-rettelses-ISO** er status:

| Akseptansepunkt | Resultat | Begrunnelse |
| --- | --- | --- |
| 1. UEFI-oppstart fra ISO | IKKE TESTET | Ingen ny ISO finnes. |
| 2. Live-skrivebord | IKKE TESTET | Ingen ny gjest startet. |
| 3. Installerens diskvalg og sikkerhetskontroller i den nye ISO-en | IKKE TESTET | Kildereview er ikke test av en ferdig ISO. |
| 4. Full installasjon med exitkode 0 | IKKE TESTET | Null byggforsøk; ingen ny installasjon. |
| 5. Oppstart fra installert disk uten ISO | IKKE TESTET | Intet nytt installert system. |
| 6. Vanlig passordinnlogging | IKKE TESTET | Ingen normal ny-ISO-innlogging gjennomført. |
| 7. Skrivebord og grunnleggende apper etter installasjon | IKKE TESTET | Ingen post-rettelses-installering. |
| 8. Låsing, feil passord og korrekt opplåsing | IKKE TESTET | Ingen installert autentiseringsport kjørt. |
| 9. Avslutning og opprydding av ny testgjest | IKKE TESTET / ingen gjest å avslutte | Prosess-/låskontroll ved avslutning er separat og faktisk utført. |

**Historisk `internal1`:** ISO/live-portene og avvisning/kansellering av ugyldige mål har tidligere bevis. Den senere reelle installasjonen på én ny disponibel disk svarte på fem interaktive PTY-prompter og feilet i målrotens Pacman, exit 1. Passord ble ikke skrevet ut. Delvis disk, firmware, ISO og private logger ble bevart; gjest og supervisor ble avsluttet kontrollert. Dette er ikke en vellykket full installasjon. QEMU exit 0 ville uansett ikke bevist installer exit 0.

### Faktisk lagringsblokkering og rettelse av tidligere enhetspåstand

- Opprinnelig kontrollpunkt: **5593186304 tilgjengelige byte**, omtrent **5,209 GiB**. Den tidligere teksten «5,6 GiB» blandet desimal GB med binær GiB og korrigeres her, uten å omskrive de historiske råbevisene.
- Ny lesekontroll kl. **15:37:44 UTC**: **5589602304 tilgjengelige byte**, omtrent **5,206 GiB**; **21253943296 byte** under kravet.
- Prosjektkravet i [docs/iso.md](https://github.com/tomli0/wilsof-os/blob/9aebacdd82072257f57c0c31d17a1f7f600a4acb/docs/iso.md) er minst **25 GiB = 26843545600 byte** tilgjengelig i filsystemet for work/output. Lesingen viser reell kapasitetsmangel. Diskplass endrer seg mens systemet logger; tallene er tidsstemplet, ikke et løfte om fremtidig ledig plass.
- Eksisterende ISO-bunter bruker rundt 10,16 milliarder allokerte byte. Lesbar QA-/bygg-/diskhistorikk utgjør minst rundt 40,29 milliarder byte. Den uprivilegerte `du`-inventeringen meldte 63 utilgjengelige kataloger og exit 1; QA-tallet er derfor **ufullstendig**, ikke en nøyaktig total eller en slettetillatelse.
- Null ISO-byggforsøk og null QEMU-start i den autonome utviklingsøkten; heller ingen i rapporteringsoppfølgingen. Ingen opprydding ble improvisert for å presse frem et bygg. Tidligere artefakter og bevis skal fortsatt bevares.

## 7. Oppstart og passordinnlogging

**Ikke testet for et nytt bilde med rettelsen.** `internal1` inneholder ikke korrigeringen og forblir avvist etter installasjonsfeilen. Tidligere pass på andre image-/installasjonskilder kan ikke overføres hit.

Den isolerte Pacman-/runuser-verifikasjonen beviser prosesskontekst og pakkeinstallasjon, ikke normal greeterinnlogging, PAM, lås, feilpassordkontroll eller korrekt opplåsing. Disse portene må observeres etter vellykket installasjon og disk-only boot av en identifisert ny ISO.

## 8. Gjenstående feil og begrensninger

- **#34 åpen:** kildeutbedring og uavhengig review er levert, men faktisk ny-ISO-installering, disk-only boot og normal autentisering gjenstår.
- **Lagring:** minst 25 GiB tilgjengelig må være dokumentert på godkjent bygglagring før et senere bygg. Ingen lagringsendring eller sletting er autorisert her.
- **Reviewets fire forbygg-/akseptansetiltak** i punkt 2 er fremdeles gjenstående; rapporteringen implementerer dem ikke. F09s øvrige runuser-/atferds-/argv-dekningshull og F11 skal heller ikke forsvinne fra risikobildet.
- **F07/F08:** devtmpfs-eksponering er teoretisk/ubekreftet; delt `/run` er bekreftet transient upstream-atferd. Ingen påstand om verifisert utnyttelse eller full chroot-isolasjon.
- **#30:** kildebasert updater-/migrasjonsrettelse inngår i eksisterende integrasjon/image-historikk, men faktisk oppdatering, bevaring og manuell filgjenoppretting i det fremtidige installerte bildet er ikke akseptert.
- **#31:** tidligere Hypridle-harness og faktisk compositor-/sesjonsteardown har egne daterte bevis; dette lukker ikke gjenværende livssyklus-/latens-/låseporter eller den fremtidige ISO-akseptansen. Ingen ny Hypridle-pakke bygges for rapporten.
- **Fysisk klient/maskinvare:** faktisk USB-/firmwareboot, tastaturruting, GPU, Wi-Fi, lyd, suspend, skjerm-/WS-logo-layout og relevant låse-/power-profile-atferd på fysisk klient er ikke verifisert av denne økten. Ingen Proxmox-tilgang eller fysisk operasjon ble forsøkt på nytt.
- **Emulator:** tidligere QEMU-arbeid brukte TCG og dokumenterte CPU-/renderingbegrensninger. En emulatoromvei er ikke generell maskinvarestøtte eller fysisk aksept.
- **Publisering/review:** PR #27/#35 er fortsatt draft og ikke merget. Denne dokumentasjonsoppfølgingen har ingen ny uavhengig modellreview; det er bevisst, og ikke et skjult ekstra betalt QA-steg.

Formuleringen i den opprinnelige rapporten om at «alt annet ligger klar» skal ikke forstås som at disse portene er bestått. Hovedmålet om en vellykket installert ny ISO er fortsatt ikke levert.

## 9. Engineering Standards og dokumentasjons-PR

[PR #35](https://github.com/tomli0/wilsof-os/pull/35) inneholder opprinnelig:

- `docs/ENGINEERING_STANDARDS.md`: risikobasert omfang, kodekvalitet, minste privilegium, validering, sikker feil-/mount-/diskhåndtering, testing, supply chain/lisens, autentisering/oppdatering, review, sporbarhet og ressursgrenser, Definition of Ready/Done og sjekkliste.
- `docs/templates/ENGINEERING_STANDARDS_TEMPLATE.md`: teknologiuavhengig tilpasningsmal.

Opprinnelig leveranse fikk tekst-, lokale lenke- og diffkontroll. Ingen rapporterte CI-sjekker på dokumentasjons-PR-en; ikke beskrevet som grønn. Den separate grenen og PR-en forstyrrer ikke integrasjonsarbeidet.

Rapporteringsoppfølgingen tilfører en fast normal avslutningsprosedyre og [rapportmal](../templates/DEVELOPMENT_REPORT_TEMPLATE.md), [rapporteringsstandard](../development-reporting.md), [sanert rapporteringskontrollpunkt](../checkpoints/2026-10-28-autonomous-session-reporting.md) og prosjektinstruksjon. Standarden krever alltid: oppdatert kontrollpunkt → full Markdown-rapport → commit/push på autorisert gren → oppdatering av relevant status-issue → direkte GitHub-lenke i terminalen. Dette er normal agentavslutning, **ikke** en ny scheduler, bakgrunnsarbeider, CI-jobb eller plugin. Innholdet publiseres på dokumentasjonsgrenen og er ikke automatisk flettet inn i andre grener/worktrees.

## 10. API-/modellforbruk der det kan dokumenteres

### Historisk rute og dokumenterte estimater

| Del | Modell / dokumentasjon | API-kall | Dokumentert kostnad, USD |
| --- | --- | ---: | ---: |
| Primærrute | Codex `gpt-6.1-sol`, abonnement inkludert | Del av blandet foreldresesjon; ikke isolert fakturagrunnlag | Ikke separat målt API-faktura. HTTP 429 og automatisk GLM-overgang er dokumentert. |
| Review 1 | `z-ai/glm-5.3`, lagret reviewbarn | 16 | **0,087832445**, estimert. |
| Review 2 | `anthropic/claude-sonnet-4.6`, lagret reviewbarn og dispatch | 19 | **0,5695074**, estimert; dispatch avrundet til 0,569507. |
| Begge reviewrunder | Sum av de to barneestimatene | 35 | **0,657339845**, omtrent 0,66. |

Historiske budsjettprober viste håndhevet OpenRouter-nøkkelgrense **50 USD per måned**, med gjenværende beløp fra **4,089908851** til **2,454451723 USD** og registrert reset 1. november 2026 kl. 00:00 UTC. Differansen er omtrent **1,635457128 USD**. Det er observert endring i nøkkelens gjenstående ramme, ikke en revidert faktura eller sikkert isolert oppgavekostnad. Fratrukket reviewestimatene er rest rundt 0,98 USD, i samsvar med den tidligere rapportens omtrentlige «øvrig GLM ~1,0 USD», men annen samtidig nøkkelbruk kan ikke utelukkes.

Nøkkelgrensen 50 USD dokumenterer **ikke alene** håndheving av Engineering Standards' samlede månedsramme på 300 NOK, valutaeffekter, flere nøkler eller påfyllingspolicy. De samlede kontrollene er ikke sertifisert på nytt her. Dette rapporteringsoppdraget foretar ingen budsjett-/modellprobe hos en betalt provider, ingen ny betalt review og ingen modellkonfigurasjonsendring.

### Metadata lest på nytt, ikke nye modellkall

| Lagret sesjon | Input-tokenfelt | Output | Cache read | Cache write | Merknad |
| --- | ---: | ---: | ---: | ---: | --- |
| GLM-reviewbarn | 127990 | 27165 | 592960 | 0 | 16 API-kall, status estimated, ingen actual_cost. |
| Claude-reviewbarn | 21 | 11231 | 668898 | 53416 | 19 API-kall. Dispatch oppgir samlet input 722335 = de tre input-/cachefeltene; ulike telleskjema må ikke dobbeltsummeres. |
| Foreldresesjonen ved ny lesing | 751274 | 46941 | 14347456 | 0 | 78 API-kall. Inkluderer senere statusforespørsel i samme sesjon; historisk Codex/GLM blandet. |

Foreldreraden står som `openai-codex` / `subscription_included` / `cost_status=included`, med et lagret estimat på **0,9251764549 USD**, men `actual_cost_usd` mangler. Den raden alene dokumenterer ikke at alle kall var inkludert; loggen viser faktisk GLM-fallback. Ikke summer den ukritisk med andre kostnadsfelt eller merk estimatene som faktisk fakturert. Tidligere rapporterte kvotereset rundt 13:44 UTC er historisk informasjon, ikke en ny bekreftelse på dagens tilgjengelige kvote. Tom `ended_at` i databasen er heller ikke bevis på at en prosess fortsatt kjører.

## 11. Aktive prosesser og prosjektlåser

**Historisk avslutning:** ingen QEMU-, bygg-, installer- eller labprosesser ble funnet. Øktens kernel holdt prosjektets eksklusive `run.lock` under beskyttet arbeid og frigjorde den kl. **13:37:21 UTC**. En ikke-blokkerende tilgjengelighetsprobe lyktes etter frigivelse. Kontrollpunktets gamle `lock_owner_pid` er historisk metadata, ikke gjeldende eierskap.

**Kontrollert på nytt:**

- Ingen QEMU-, mkarchiso-, installer-, test-, review-dispatch- eller Wilsof-arbeiderprosess funnet i prosesskontrollen kl. 15:37:44 UTC. Tidligere registrert låseeier eksisterte ikke lenger.
- Eksklusiv ikke-blokkerende låsing lyktes før dokumentasjonsskriving. Den nåværende rapporteringskernelen holder en **egen midlertidig dokumentasjonslås** under commit/push for å unngå konkurrerende agentarbeid; ingen VM eller bakgrunnsarbeider startes av dette.
- Hermes-jobben «Wilsof GitHub Queue Check» finnes fortsatt, men er **enabled=false / paused**; workerens kontrollfil har **paused=true, stop_requested=false**. En gammel `next_run_at` er ikke bevis på aktivering.
- Hermes gateway/dashboard kjører fra før. Det er ikke det samme som en aktiv Wilsof-utviklingsjobb. Ingen tjenester, timere, scheduler eller arbeidere er startet eller endret av rapporteringen.
- Dokumentasjonslåsen skal frigjøres og tilgjengeligheten kontrolleres før endelig terminalkvittering; endelig read-back/publiseringskvittering og låsestatus bevares i det private rapporteringskontrollpunktet. Rapportens tidsstemplede opptak under skriving skal ikke forveksles med et på forhånd verifisert avslutningsresultat.

Ingen fremmede prosesser er stoppet, ingen arbeidslås er stjålet, og ingen andres worktrees er ryddet. Ingen fysisk disk-, USB- eller Proxmox-endring.

## 12. Neste anbefalte handling

**Neste utviklingsoppgave, kun etter separat gjenopptakingsgodkjenning:** implementer den avgrensede #34-sjekklisten for `arch-install-scripts`, resolver-postbetingelse, `install_package('/')` og miljøavgrenset ekte arch-chroot-regresjon. Bevar reviewets øvrige dekningsmerknader og alle sikkerhetsgrenser. Dette kan forberedes som en liten kilde-/testleveranse, men er ikke startet her.

**Forutsetning før det påfølgende bygget:** skaff dokumentert minst **25 GiB ledig på godkjent bygglagring**, uten å slette bevarte artefakter/testbevis eller endre fysiske disker/Proxmox uten særskilt tillatelse. Deretter: frys én gjennomgått kildecommit, bygg én ny versjonert intern ISO, registrer full proveniens, installer på **en ny disponibel virtuell disk**, boot uten ISO og verifiser vanlig passordinnlogging, apper, lås/feil passord/opplåsing og kontrollert avslutning. Den bevarte delvis installerte `internal1`-disken er ikke et blankt testmål.

#34 forblir åpen til relevante faktiske akseptansebevis finnes. PR #27 og #35 forblir draft; ingen main-merge, offentlig release eller fysisk aksept utledes. **Ingen neste utviklingsoppgave, scheduler eller bakgrunnsarbeider startes av denne rapporten.**
