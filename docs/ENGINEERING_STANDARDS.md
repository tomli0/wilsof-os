# Engineering-standard for Wilsof OS

Denne standarden beskriver hvordan endringer skal avgrenses, implementeres, gjennomgås og dokumenteres. Målet er færre feil og tryggere leveranser, ikke flere prosesser. Kravene gjelder mennesker og utviklingsagenter. En liten dokumentasjonsrettelse trenger ikke samme bevis som en installerendring.

## 1. Virkeområde og forholdet til eksisterende dokumentasjon

- [CONTRIBUTING.md](../CONTRIBUTING.md) er prosjektets praktiske arbeidsveiledning og kilde til konkrete valideringskommandoer.
- [Quality audit](quality-audit.md) er en datert vurdering med avgrensede funn, ikke et løfte om nåværende kvalitet.
- [Security boundaries](security.md) definerer trusselmodell, sikkerhetsrapportering og interne/offentlige utgivelsesporter. Disse kravene gjelder fortsatt.
- [Installerarkitektur](installer-architecture.md), [installer-runtime](installer-runtime.md) og [intern testrunbook](internal-test-runbook.md) konkretiserer implementasjon og autorisert testing.
- [Status](status.md), [kontrollpunkter](checkpoints/) og den aktuelle issue-/PR-tråden viser faktisk fremdrift og begrensninger. Denne standarden er ikke et nytt statusdashboard.

«SKAL» er et krav. «BØR» er et utgangspunkt som kan fravikes med en kort teknisk begrunnelse. Ved motstrid skal arbeidet stanses ved den berørte grensen og avklaringen dokumenteres; en agent skal ikke velge den mest tillatende teksten. Historiske revisjoner, diskgrenser og testresultater skal ikke omskrives til påstander om dagens installer. Gjeldende oppdrag gir operativt omfang, men denne teksten gir aldri i seg selv tillatelse til privilegerte handlinger.

Den teknologiuavhengige [malen](templates/ENGINEERING_STANDARDS_TEMPLATE.md) kan brukes i andre prosjekter. Wilsof-spesifikke pakker, grenser og godkjenninger skal ikke kopieres ukritisk.

## 2. Risikobasert og avgrenset arbeid

Før endringen skal forfatteren identifisere berørt brukerflyt, tillitsgrense, feilkonsekvens og minste tilstrekkelige validering.

| Risiko | Eksempler | Minste relevante bevis |
| --- | --- | --- |
| Lav | Dokumentasjon, interne navn uten atferdsendring | Faktasjekk, lokale lenker, diffkontroll og begrunnet avgrensning av øvrige sjekker |
| Middels | Launcher, konfigurasjonsoppdatering, brukergrensesnitt | Fokuserte tester, relevante negative tilfeller, statisk analyse og berørt runtime-flyt |
| Høy | Diskvalg, privilegier, autentisering, pakke-/oppdateringskjede | Gjennomgang av hele tillitsgrensen, negative tester, disponibel runtime-test og uavhengig gjennomgang før aksept |
| Kritisk | Mulig datatap, sikkerhetsomgåelse eller hemmelighetslekkasje | Stans berørt levering, bevar bevis og få eksplisitt beslutning fra eier før videre risikofylt handling |

Bruk den høyeste relevante risikoen. Dokumentasjon som instruerer om formatering eller endrer sikkerhetskrav er ikke automatisk lav risiko. Omfang og akseptansekriterier skal være små nok til å avslutte. Nye funn som ikke blokkerer leveransen skal registreres separat, ikke gjøres til en endeløs forbedringsrunde.

## 3. Kodekvalitet, lesbarhet og vedlikehold

- Kode SKAL ha tydelig ansvar, forståelige navn og eksplisitte innganger, utganger og eierskap. Unngå skjult global tilstand og ubegrunnede abstraksjoner.
- Bruk én kilde til sannhet for snarveier, pakkemanifester, standardinnstillinger og sikkerhetsregler. Genererte filer skal ha en kjent kilde og oppdateringsvei.
- Endringen SKAL være den minste sammenhengende rettelsen. Ikke bland feilretting med generell opprydding, nye funksjoner eller urelaterte avhengighetsoppgraderinger.
- Kommentarer BØR forklare hvorfor en sikkerhetsgrense eller uvanlig løsning finnes, ikke gjenta koden. Midlertidige omveier skal ha begrunnelse og et konkret kriterium for ny vurdering.
- Shellkode SKAL bruke riktig deklarert dialekt, sitere ekspansjoner og bevare feilstatus. Ikke bygg kjørbar kode av uvaliderte strenger eller bruk `eval` som snarvei.
- Endret atferd SKAL ha en relevant test. Ubrukte grener, midlertidig instrumentering og utilsiktede filendringer skal fjernes før review.

## 4. Systemarkitektur og beslutninger

Hold live-miljø, installert system, utviklingsvert og automatisering atskilt. UI- og øktkode skal som hovedregel kjøre som vanlig bruker; privilegerte operasjoner skal ligge bak små, eksplisitte grensesnitt.

En vesentlig beslutning SKAL kort beskrive problem, valgte løsning, relevante alternativer, sikkerhets-/driftskonsekvenser og reverserings- eller migrasjonsbehov. Bruk eksisterende [beslutningslogg](beslutningslogg.md); en kort seksjon i en PR er tilstrekkelig for små valg. Ikke krev et separat arkitekturdokument for enhver funksjon.

Før et eksisterende grensesnitt endres skal produsenter, konsumenter og versjonsavhengigheter undersøkes. Følg hele kjeden fra brukerhandling til installert fil/tjeneste. En lokal rettelse som ikke når ISO-en eller det installerte systemet er ikke integrert levering.

## 5. Secure-by-design og inputvalidering

- Valider ubetrodde data ved grensen: filnavn, symlenker, enhetsmetadata, miljøvariabler, JSON, CLI-argumenter, pakkesvar og innhold fra GitHub.
- Bruk tillatte verdier og kanonisk identitet der det er praktisk. Avvis tvetydige eller farlige mål. Kontroller tilstanden igjen umiddelbart før irreversible operasjoner.
- Minste privilegium SKAL gjelde både prosess, filrettigheter, sudo-regler, CI-token og API-nøkkel. Ikke erstatt en smal tillatelse med generell root- eller passordfri tilgang.
- Hemmeligheter skal ikke ligge i Git, kommandolinjeargumenter, logger, testbevis eller distribuerte image-filer. Syntetiske QA-opplysninger og VM-disker skal holdes privat og atskilt fra leveransen.
- Byggerøtter skal ikke få vertens hjemmekatalog, legitimasjon eller fysiske blokkenheter. Bildet skal kontrolleres for utilsiktede kontoer, nøkler, tjenester og maskinidentitet.
- En midlertidig diagnostisk omgåelse er ikke en produksjonsrettelse. Ikke svekk signatur-, autentiserings- eller målvalidering for å få grønn test.

Følg den eksisterende private rapporteringsveien ved alvorlige sikkerhetsfunn. Ikke publiser hemmeligheter eller utnyttelsesdetaljer som del av vanlig feilsøking.

## 6. Feilhåndtering, logging og gjenoppretting

Operasjoner SKAL skille mellom forventet fravær, avbrudd og faktisk feil. Ikke returner suksess etter delvis feil. Brukeren skal få vite hva som feilet, om tilstanden kan være delvis endret, og hva som er trygg neste handling.

Arbeid skal ha begrensede tidsfrister og retries. Timeout betyr at utfallet er ukjent inntil eksisterende prosess og mål er undersøkt; det gir ikke tillatelse til å starte en duplikatoperasjon.

Logger BØR inneholde tidspunkt, operasjon, revisjon og relevant, ikke-hemmelig målidentitet. Bevar exitkode og den første konkrete feilen. Rålogger, krasjdumper og skjermbilder skal vurderes for sensitive data før deling.

En gjenopprettingspåstand SKAL være presis:

- En filbackup gir manuell gjenoppretting av den filen, ikke transaksjonell rollback.
- En avbrutt installasjon kan ha endret disken; ikke lov automatisk tilbakeføring.
- Ikke reparer, slett eller gjeninstaller som et skjult teststeg.
- Dokumenter hva som er prøvd, hva som er bevart og hva som ennå ikke er testet. Gjenoppretting skal testes på disponibelt materiale når den inngår i akseptansen.

## 7. Tester, statisk analyse og regresjonskontroll

En feilretting SKAL starte med en konkret reproduksjon eller en test som kan oppdage den aktuelle feilen. Registrer at testen faktisk feiler av riktig grunn før rettelsen, og består etterpå når dette er praktisk mulig. Hvis en deterministisk reproduksjon ikke er tilgjengelig, dokumenter begrensningen og bruk direkte runtime-bevis; ikke fabriker en grønn test.

Test både suksess og relevante feiltilfeller: ugyldige input, avvist mål, kansellering, manglende avhengighet, delvis feil og livssyklus/cleanup. Bruk midlertidige kataloger og mocks for destruktive enhetstester. Mocks erstatter ikke nødvendig test i disponibel maskinvare.

Kjør de relevante kommandoene i `CONTRIBUTING.md`. Ved kodeendringer skal fokuserte tester, full relevant suite, korrekt ShellCheck-dialekt, konfigurasjonsvalidering og diffkontroll inngå før aksept. Dokumenter kommando, exitstatus og testet revisjon. Dokumentasjonsarbeid kan forberedes i en draft-PR med tekst-/lenke-/diffkontroll; eventuelle påkrevde øvrige sjekker skal stå som ikke kjørt eller ikke relevante med begrunnelse, ikke som bestått. Dette opphever ikke gjeldende review- eller CI-krav før godkjenning.

Et hentet eller tilpasset testharness er WIP inntil det konkrete inngangspunktet er kjørt. Sanitizer som feiler ved oppstart eller adressekartlegging er en ufullført sjekk, ikke fravær av feil. CI gjelder bare kommandoene og den eksakte commit-en den faktisk kjørte.

## 8. Avhengigheter, lisensiering og supply chain

- Bruk offisielle primærkilder for API-er, utgivelsesendringer og sikkerhetsvarsler. Verifiser aktuelle versjoner fremfor å stole på modellhukommelse.
- Registrer avhengighetskilde, versjon/commit, lokale patcher og pakkeidentitet. Kontroller signaturer og checksums; en egen checksum dokumenterer identitet, ikke tillit til en ukjent utgiver.
- En lokal native patch krever separate bevis for kildetest/harness, full native pakkebygging, den pakkede binæren, reell runtime-livssyklus og eventuell ISO-integrasjon. Ingen av disse portene kan erstattes med en annen.
- Gjenbruk et verifisert byggeartefakt når inngangene er uendret. Ikke bygg en stor avhengighet på nytt bare for å gjenta et allerede bestått steg.
- Bevar relevante opphavsretts- og lisensmerknader. Kontroller om distribusjon, patcher og inkluderte assets er tillatt. Ikke anta at prosjektet gir en lisens bare fordi kildekoden er offentlig; manglende prosjektlisens må avklares før en lisenspåstand eller offentlig distribusjon.
- Nye avhengigheter skal ha et konkret behov og en vurdering av vedlikehold, privilegier og angrepsflate. Kritiske advisories skal vurderes før relevant bygg/oppgradering.

## 9. Sikker installasjon, autentisering og oppdatering

### Installasjon

Gjeldende runtime-implementasjon og runbook er autoritative for støttede valg; gamle audits av andre installere skal ikke brukes som dagens parameterliste. Målidentitet, kapasitet, bruk/mounts, partisjoner/signaturer og blankhet skal valideres etter gjeldende kontrakt. Vis eksplisitt mål, datatapsvarsel og pakke-/layoutplan; krev en entydig bekreftelse og kontroller målet igjen før formatering. Passord skal behandles via skjult input og aldri serialiseres i planen.

Agenttester skal bare bruke en ny, dedikert virtuell disk som er eksplisitt innenfor oppdraget. Fysiske disker, USB-skriving og Proxmox-endringer krever særskilt tillatelse; en dokumentert fremgangsmåte er ikke slik tillatelse.

### Autentisering og økt

Skille live-evaluering fra installert brukerkonto. En uttrykkelig ulåst live-økt skal ikke fremstilles som sikker arbeidsplass. Installerte passord, PAM-policy og maskinidentitet skal være systemets ansvar, ikke fast innebygde utviklerverdier.

Vanlig greeterinnlogging, reell avvisning av feil passord, ekte opplåsing og gjenopprettet økt må observeres direkte når de inngår i akseptansen. Root-tilgang, `runuser`, avsluttet locker eller administrativ logout er ikke bevis på autentisering. Mål automatisk låsing uten å sende ny input under idle-intervallet; funksjon, oppstartstid og grafisk rendering skal rapporteres separat.

### Oppdateringer og bevaring

Separer full pakkeoppgradering fra Wilsof-konfigurasjonsoppdatering. Les relevante upstream-varsler og foreslått transaksjon/replacements før bekreftelse. Ikke bruk en delvis Arch-oppgradering som løsning. Rapporter en vellykket no-op som no-op.

Personlige innstillinger skal bevares, bare eide filer endres, og backups/manual recovery testes når flyten berøres. Etter en relevant binær- eller øktendring skal en ny autentisert økt testes; den gamle prosessen beviser ikke den oppgraderte pakken. Registrer immutable image-kilde og eventuell separat lokal utbedringskilde hver for seg.

## 10. Uavhengig gjennomgang og AI-basert QA

Forfatteren skal først gjøre egen diffgjennomgang. Endringer med høy risiko krever uavhengig gjennomgang av hele den relevante kjeden før aksept. En separat reviewer kan være et menneske eller en uavhengig AI-kontekst innenfor godkjent modell-/kostnadsramme; egenvurdering skal aldri merkes som uavhengig review. Kravet om uavhengig menneskelig sikkerhetsgjennomgang før offentlig distribusjon i `security.md` består.

Revieweren skal få avgrenset oppdrag: akseptansekriterier, eksakt diff/revisjon, faktiske tester, kjente begrensninger og ønsket vurdering av konkrete blokkere. Skill funn fra forslag. Maksimalt to planlagte review-/rettelsesrunder før omfang, arkitektur eller ekstern blokkering revurderes. Flere modeller er ikke i seg selv mer kvalitet.

AI-svar, agentoppsummeringer og «success» fra et skrivekall er ikke bevis alene. Kontroller filer, eksekvering og eksakt ekstern måltilstand. Uløste funn skal ikke skjules, automatisk lukkes eller omgås for å få merge. En dokumentasjons-PR kan stå som draft mens uavhengig review mangler.

## 11. Bygg, sporbarhet og testbevis

Bygg fra en ren, identifisert kilderevisjon og et eksplisitt payload-/pakkemanifest. Registrer verktøyversjoner, miljø, avhengigheter, patcher, byggkommando, exitstatus og relevante begrensninger. Bevar tidligere artefakter; en ny versjon skal ikke overskrive kjent testgrunnlag.

For en intern ISO skal minst følgende følge som separat manifest/checksum og dokumentasjon: versjon/filnavn, kildecommit, størrelse i bytes, SHA256, lagringssted, inkluderingskontroll og teststatus. Private QA-disker og legitimasjon skal ikke inngå i den distribuerbare bunten.

Sporbart eller gjentakbart bygg er ikke automatisk bit-for-bit reproduserbart. Sistnevnte krever faktisk sammenligning av uavhengige bygg med dokumenterte innganger; ikke gjør ekstra kostbare bygg uten at den porten er nødvendig og autorisert.

Bevis skal knyttes til eksakt kilde, pakke, artefakt og runtime-miljø. Bruk «bestått», «feilet», «ikke testet» eller «ikke relevant – begrunnelse». Oppgi kommando/resultat og varig bevissted; dato, screenshot, prosess-/øktidentitet og renderer-/VM-begrensning der det er relevant. En stale frame eller en vellykket IPC-kvittering alene beviser ikke riktig skjermbilde.

### Modenhetsnivåer skal holdes atskilt

| Betegnelse | Hva som må være dokumentert | Hva det ikke beviser |
| --- | --- | --- |
| Implementert | Identifisert kildeendring med tilsiktet atferd | At testen eller runtime-flyten består |
| Testet | Navngitte tester og utfall for en eksakt revisjon og et konkret miljø | Automatisk integrasjon eller full funksjonsaksept |
| Integrert | Endringen finnes i identifisert integrasjon/konsument, med kontroll av grensesnitt | At en eldre ISO inneholder endringen |
| ISO-verifisert | Eksakt ferdig ISO og dens relevante oppstart/installasjon/oppdatering-/øktporter er testet | Fysisk USB-, firmware-, GPU- eller klientaksept |
| Fysisk verifisert | Datert test på oppgitt fysisk maskin/klient og konkrete kriterier | Generell støtte for uprøvd maskinvare |

Dette er separate egenskaper, ikke automatisk videreføring av et «pass». En bygget, men ikke ferdig testet ISO skal merkes slik. Et emulatorarbeidsrundt eller en lokal source-fix skal merkes eksplisitt og ikke tilskrives uendrede image-bytes.

## 12. Kontrollert agentarbeid og ressursgrenser

- Gjenopprett siste kontrollpunkt, GitHub-status, grener/worktrees, prosesser og låser før arbeid. Ikke gjenta ferdige porter eller start dupliserte bygg/installasjoner.
- Bruk én hovedagent og normalt høyst én aktiv QEMU-testgjest. Delegasjon skal ha konkret teknisk behov, eget avgrenset resultat og en godkjent modellrute; ikke start parallelle undersøkelser som standard.
- Følg det aktuelle oppdragets kvote-, tids-, minne-, prosess- og kostnadsgrenser. I den nåværende Wilsof-rammen er betalt bruk begrenset til samlet maksimalt 300 NOK per kalendermåned, ikke per agent eller nøkkel. Dette er et tak, ikke en bestilling av betalt bruk.
- Inkludert Codex er primærvalg. OpenRouter-ruter kan bare brukes etter verifisert modelltilgjengelighet, håndhevet nøkkelgrense, deaktivert automatisk påfylling og en samlet kontroll som holder månedsrammen, også når valuta eller flere nøkler spiller inn. Kan kontrollene ikke dokumenteres, bruk kun inkludert rute og stopp ved kvotegrensen. Ikke anta at Hermes alene håndhever budsjettet.
- Dokumenter nåværende modell-/fallbackoppsett før en autorisert endring. Ingen annen betalt modell, skjult fallback eller ubegrenset retry. Rapportert forbruk skal skille målte verdier, estimater og ukjente kostnader.
- Arbeid i sekvensielle milepæler. Lag kontrollpunkt før kostbare eller irreversible operasjoner, og commit/push ferdige endringer etter milepælen. Skill ferdig arbeid fra eksplisitt bevart WIP.
- Ved lav kvote eller HTTP429: ikke start ny milepæl. Avslutt bare en liten trygg enhet, bevar tilstand, og stopp kontrollert. Ikke søk betalt omvei uten de verifiserte sperrene.
- En levende gjest/byggeprosess skal ha en identifisert supervisor/eier og en lås som varer like lenge som beskyttet arbeid. En samtale som slutter frigjør ikke en disk. Ikke frigi låsen før faktisk prosessavslutning er verifisert.
- Ved avbrudd skal kontrollpunktet angi prosess-/supervisoridentitet, disk/artefakt, logg-/socketstier, tilstand, låseier og eksakt neste trygge handling. Bevar volatile bevis før kontrollert nedstenging når det er trygt.
- Ikke aktiver scheduler/workere, endre Proxmox, merge til `main`/`arch-install` eller publiser release uten særskilt godkjenning. Når oppdraget er ferdig eller innsnevres, stopp utvidelsen; ikke start en ny forbedringsrunde.

## 13. Definition of Ready

Arbeidet er klart når det har:

1. Et konkret problem og avgrensede akseptansekriterier, inkludert hva som ikke skal gjøres.
2. Kjent kildegren/worktree, relevante eksisterende bevis og ingen uavklart konflikt med aktive prosesser/låser.
3. Avklarte tillitsgrenser, godkjenninger, risiko og nødvendige avhengigheter/tilganger.
4. En realistisk test-/reviewplan og avsatte ressurs-/kostnadsrammer.
5. Et trygt avbrudds- og gjenopptakingspunkt for arbeid som kan endre ekstern tilstand.

En manglende, nødvendig forutsetning skal merkes som blokkering. Den skal ikke fylles med gjetning eller falske testdata.

## 14. Definition of Done

En avgrenset leveranse er ferdig når akseptansekriteriene i oppdraget er oppfylt og verifisert, relevante sjekker og reviewkrav er oppfylt, sporbarhet/bevis og dokumentasjon stemmer, ferdige endringer er committet/pushet til riktig gren, og prosesser/artefakter/låser har avklart tilstand.

En kildeleveranse eller dokumentasjons-PR kan være ferdig innenfor sitt omfang uten at hele funksjonen er fysisk akseptert. Det skal fremgå. «PR opprettet» er ikke «review godkjent», «CI grønn» er ikke «ISO verifisert», og «milepæl fullført» er ikke automatisk «issue kan lukkes». Merge, offentlig release og fysisk test er egne beslutninger. Gjenstående relevante porter hindrer at den bredere funksjonen markeres Done.

## 15. Praktisk PR-sjekkliste

Kopier bare relevante punkter til PR-en, men behold utelatelser med kort begrunnelse. Ikke merk ukjørte sjekker som bestått.

- [ ] Problem/issue, omfang, risiko og akseptansekriterier er tydelige; ingen urelaterte endringer.
- [ ] Riktig base/head og eksakt kilde-/artefaktidentitet er oppgitt; andre worktrees/WIP er bevart.
- [ ] Hele berørte runtime-/installasjonskjeden og arkitekturvalgene er gjennomgått.
- [ ] Input, symlenker, målidentitet, privilegier, kansellering og feilstatus er håndtert der relevant.
- [ ] Ingen hemmeligheter, private QA-artefakter, destruktive standardvalg eller svekkede sikkerhetskontroller er lagt til.
- [ ] Avhengigheter, lokale patcher, aktuelle advisories og lisens-/assetkrav er vurdert der relevant.
- [ ] Reproduksjon/regresjon, negative tester og relevante `CONTRIBUTING.md`-sjekker er dokumentert med faktisk resultat.
- [ ] CI er lest tilbake for korrekt head; manglende, feilede og ikke relevante sjekker er oppgitt.
- [ ] Relevant uavhengig review er utført, eller PR står uttrykkelig som ventende draft; funn er ikke skjult.
- [ ] Implementert/testet/integrert/ISO-verifisert/fysisk verifisert er skilt; ingen overført aksept fra eldre artefakt.
- [ ] Personlige innstillinger, backup og konkret gjenoppretting er verifisert når oppdateringsflyten berøres; ingen falsk rollbackpåstand.
- [ ] Dokumentasjon, testbegrensninger og åpne feil stemmer med faktisk leveranse.
- [ ] Gjeldende prosess-/låseier, ressurs-/modellbruk og kontrollpunkt er dokumentert; automatisering er ikke aktivert utilsiktet.
- [ ] PR-en ber ikke implisitt om merge, release, issue-lukking eller fysisk handling uten godkjenning.
