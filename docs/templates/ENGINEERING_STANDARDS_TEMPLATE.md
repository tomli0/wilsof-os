# Engineering-standard — [PROSJEKTNAVN]

> Tilpasningsmal. Fyll ut prosjektprofilen og erstatt markørene før standarden vedtas. Malen er ikke dokumentasjon på implementerte kontroller, beståtte tester eller tillatelse til produksjonsendringer.

Formålet er forståelig kode, trygg endring og etterprøvbare leveranser. Bruk den minste prosessen som håndterer risikoen. Standarden gjelder mennesker og AI-agenter.

## Prosjektprofil — fylles ut først

| Felt | Prosjektets valg |
| --- | --- |
| Eier og godkjenningsvei | [ANSVARLIG / GODKJENNINGSKANAL] |
| Praktisk utviklingsveiledning | [LOKAL FIL ELLER LENKE] |
| Sikkerhetspolicy og privat rapportering | [LOKAL FIL ELLER KANAL] |
| Beslutningslogg / arkitektur | [STED] |
| Status og testbevis | [STED / FORMAT] |
| Støttede miljøer og leveranseartefakter | [UTVIKLING / TEST / PRODUKSJON / ARTEFAKTTYPE] |
| Autoritative valideringskommandoer | [KOMMANDOER ELLER ETT VEDLIKEHOLDT INNGANGSPUNKT] |
| Beskyttede grener og handlinger | [GREN-/MERGE-/DEPLOY-/DATA-/RELEASEGRENSER] |
| Tilstands- og hemmelighetsforvaltning | [EIER / LAGRING / TILGANG / OPPBEVARING] |
| Agentressurser | [MAKS AGENTER / SAMTIDIGE JOBBER / CPU / MINNE / TID / RETRIES] |
| Modell- og betalingsruter | [TILLATTE RUTER / FORBUDTE FALLBACKS] |
| Kostnadsramme og teknisk kontroll | [BELØP / VALUTA / PERIODE / SAMLET OMFANG / HÅNDHEVING / PÅFYLLINGSPOLICY] |
| Vedtak og neste vurderingsutløser | [GODKJENNING / DATO / KONKRET ENDRING SOM KREVER NY VURDERING] |

Tomt godkjennings- eller budsjettfelt gir ingen tillatelse. Bruk eksisterende prosjektveiledning som kilde til kommandoer og sikkerhetspolicy som kilde til sikkerhetsgrenser; ikke vedlikehold motstridende kopier. Avklar reell motstrid før den berørte operasjonen.

«SKAL» er et krav. «BØR» kan fravikes med en kort teknisk begrunnelse. Ingen tekst her overstyrer et uttrykkelig forbud eller gir tillatelse til irreversible handlinger.

## 1. Omfang og risikobasert kvalitet

Før arbeid: beskriv konkret problem, berørte brukere/grensesnitt, akseptansekriterier, hva som er utenfor omfanget, og feilens mulige konsekvenser.

| Risiko | Eksempel | Minimum før aksept |
| --- | --- | --- |
| Lav | Ren tekst-/presentasjonsrettelse uten endret atferd eller sikkerhetsråd | Faktasjekk og relevant tekst-/lenke-/diffkontroll |
| Middels | Vanlig atferds-, konfigurasjons- eller grensesnittendring | Fokuserte tester, feiltilfeller, statisk analyse og berørt integrasjon |
| Høy | Tilgang, irreversible dataendringer, migrasjon, oppdateringskjede | Negative tester, disponibel ende-til-ende-test og uavhengig gjennomgang |
| Kritisk | Mulig stort datatap eller alvorlig sikkerhetsbrudd | Stans berørt levering, bevar bevis og få eksplisitt risikobeslutning fra eier |

Tilpass eksemplene til prosjektet. Velg høyeste relevante risiko. Skill faktiske blokkere fra forbedringsforslag. Registrer sistnevnte separat i stedet for å utvide arbeidet uten sluttdato.

## 2. Kodekvalitet og vedlikehold

- Hold komponenter sammenhengende og grensesnitt, navn, input/output og eierskap tydelige.
- Bruk én kilde til sannhet for regler, skjemaer, konfigurasjon og genererte data.
- Lag den minste sammenhengende endringen; ikke bland urelatert opprydding eller nye funksjoner inn i rettelsen.
- Følg språkets og prosjektets formatterings-, type- og lintregler. Unngå skjult global tilstand og unødvendige abstraksjoner.
- Forklar ikke-opplagte begrensninger og hvorfor midlertidige løsninger finnes. Oppgi når de skal vurderes på nytt.
- Fjern utilsiktede endringer og midlertidig instrumentering før review. Endret atferd skal ha relevant test eller eksplisitt dokumentert valideringsbegrensning.

## 3. Arkitektur og tekniske beslutninger

Skill miljøer, privilegier, dataeiere og livssykluser. Spor produsenter og konsumenter før et grensesnitt endres. Kontroller at løsningen når den faktiske leveransekjeden, ikke bare én lokal kodegren.

Vesentlige valg skal kort dokumentere problem, valgt løsning, alternativer, konsekvenser, kompatibilitet og migrasjons-/reverseringsbehov. Bruk prosjektets eksisterende beslutningslogg. For små endringer er en kort begrunnelse i PR-en tilstrekkelig; ikke krev egne dokumenter uten behov.

## 4. Secure-by-design

- Identifiser tillitsgrenser og relevante trusler før privilegier, dataflyt eller eksterne avhengigheter endres.
- Valider ubetrodd input ved grensen: type, format, tillatte verdier, størrelse og identitet etter behov. Avvis tvetydige eller farlige mål.
- Kontroller mål og forutsetninger igjen umiddelbart før irreversible handlinger; vurder samtidighet og endring mellom kontroll og bruk.
- Gi prosesser, brukere, CI og nøkler bare nødvendig tilgang. Skill brukergrensesnitt fra privilegert utførelse.
- Hold hemmeligheter og private artefakter utenfor Git, argv, logger, skjermbilder og distribusjoner. Bruk godkjent hemmelighetslager og syntetiske testdata.
- Ikke svekk autentisering, validering eller signaturkrav for å få et grønt resultat. En diagnostisk omgåelse skal aldri skjules som en vanlig rettelse.
- Følg privat rapporteringsvei ved alvorlige funn. Ikke roter hemmeligheter, slett bevis eller skriv om historie uten koordinert godkjenning.

## 5. Feil, logging og gjenoppretting

Skill forventet fravær, kansellering, feil og ukjent utfall. Ikke rapporter suksess etter delvis feil. Oppgi hva som kan være endret og neste trygge handling.

Sett tidsfrister og endelige retrygrenser. Timeout skal etterfølges av tilstandsavklaring, ikke automatisk duplisering av operasjonen. Cleanup og låseierskap må dekke avbrudd og unntak, ikke bare normal avslutning.

Logger bør vise tidspunkt, operasjon, revisjon, ikke-hemmelig målidentitet og faktisk feil-/exitstatus. Vurder persondata, hemmeligheter og oppbevaring før bevis deles.

Beskriv gjenoppretting på riktig nivå. En backup er ikke nødvendigvis transaksjonell rollback; en kopi er ikke nødvendigvis en konsistent snapshot. Test den konkrete gjenopprettingsflyten på disponibelt materiale når den inngår i akseptansen. Ikke skjul reparasjon eller reinstallasjon som et ordinært teststeg.

## 6. Tester og statisk analyse

- Etabler en målrettet reproduksjon/regresjon som kan oppdage den aktuelle feilen. Registrer feil før rettelse og bestått etter rettelse når mulig; oppgi en reell begrensning hvis dette ikke kan gjøres.
- Test suksess og relevante feiltilfeller: ugyldig input, kansellering, manglende avhengighet, delvis feil, samtidighet og cleanup.
- Bruk mocks og midlertidig tilstand der virkelige operasjoner ville være farlige, men ikke la mocks erstatte nødvendig integrasjons- eller runtime-test.
- Kjør relevante fokuserte tester, full berørt suite, linter/type-/konfigurasjonskontroller og diffkontroll fra det autoritative prosjektinngangspunktet.
- Registrer eksakt kommando, revisjon og faktisk resultat. Et endret testharness skal kjøres før gamle resultater tilskrives den nye versjonen.
- Et verktøy eller en sanitizer som ikke startet, er ikke en bestått sjekk. Manglende CI er ikke grønn CI.
- Dokumentasjonsarbeid kan forberedes i en draft-PR med relevante dokumentkontroller. Eventuelle øvrige prosjektkrav før aksept består; merk ukjørte og ikke relevante sjekker tydelig med begrunnelse.

## 7. Avhengigheter, lisensiering og supply chain

Bruk primærkilder for aktuelle versjoner, API-er og sikkerhetsvarsler. Registrer kilder, låste versjoner/commits, patcher, checksums/signaturer og relevante lisenskrav. Bevar opphavsrett og assetproveniens. Offentlig kildekode betyr ikke automatisk en lisens til videre distribusjon.

Vurder nye avhengigheters behov, vedlikehold, tilgang og angrepsflate. Skill identitetskontroll med en checksum fra tillit til utgiveren. Ikke omgå signaturverifikasjon eller bruk en ubegrunnet nedgradering for å skjule feil.

Ved egen pakke eller native patch: skill kildetest, faktisk pakkebygg, inspeksjon av pakket binær, runtime og sluttartefakt. Gjenbruk verifiserte artefakter når inngangene er uendret.

## 8. Installasjon, autentisering, migrasjon og oppdatering

Tilpass denne seksjonen til faktisk produkt. Merk irrelevante deler med begrunnelse; ikke oppfinn installasjons- eller rollbackgarantier.

- Installasjon/migrasjon skal ha eksplisitt mål, støttede forutsetninger, datatapsvarsel, egnet bekreftelse og kontroll rett før irreversibel utførelse.
- Test bare på disponibel, uttrykkelig autorisert tilstand. Dokumentasjon eller en tidligere godkjenning av et annet mål gir ingen ny operativ tillatelse.
- Ikke distribuer faste utviklerpassord, privilegerte nøkler eller utilsiktet maskinidentitet. Autentisering skal følge den godkjente system-/identitetsløsningen.
- Bevis vanlig autentisering og avvisning av ugyldige opplysninger når det kreves. Administrativ tilgang, drept prosess eller tvungen avslutning er ikke bevis på normal innlogging eller opplåsing.
- Skill binær-/pakkeoppdatering fra brukerdata og konfigurasjon. Vurder varsler, kompatibilitet og foreslått transaksjon før bekreftelse.
- Bevar personlige innstillinger og endre bare eide data. Test migrasjon, backup og konkret gjenoppretting der relevant.
- Valider en ny prosess/økt etter relevante oppdateringer. En gammel kjørende prosess beviser ikke en oppgradert binær. Rapporter no-op-oppdateringer som no-op.

## 9. Review og AI-basert QA

Forfatteren skal gjennomgå egen diff før ekstern review. Høy risiko krever uavhengig gjennomgang før aksept; eventuelle strengere menneskelige godkjenninger i sikkerhetspolicyen gjelder fortsatt. Egenvurdering må ikke kalles uavhengig review.

Gi revieweren et begrenset mandat med akseptansekriterier, eksakt revisjon/diff, faktiske testresultater og kjente begrensninger. Be om konkrete feil, sikkerhetsfunn, manglende bevis og vurdering av blokkere, ikke en generell kvalitetsros.

AI-review er beslutningsstøtte, ikke attestering. Verifiser funn og påståtte resultater i faktisk kilde, eksekvering eller ekstern tilstand. Bruk bare godkjente modell-/kostnadsruter. Sett et maksimalt antall review-/rettelsesrunder i prosjektprofilen; ved gjentatt feil skal årsak og omfang revurderes, ikke bare modellen prøves igjen.

## 10. Bygg, sporbarhet og testbevis

Bygg fra en ren, identifisert revisjon med eksplisitte innganger og kjent miljø. Registrer verktøy-/avhengighetsversjoner, patcher, kommando, exitstatus og begrensninger. Ikke eksponer vertens hemmeligheter eller private data til byggerøtter.

Et leveransemanifest bør minst angi versjon/filnavn, kildecommit, størrelse, digest, lagringssted og akseptstatus. Bevar tidligere relevante artefakter og bevis. Ikke overskriv testgrunnlaget uten en dokumentert beslutning.

Sporbarhet er ikke bit-for-bit reproduserbarhet. Sistnevnte krever faktisk sammenligning av uavhengige bygg med dokumenterte innganger. Ikke utfør ekstra kostbare bygg uten relevant akseptkrav og autorisasjon.

Knytt testbevis til eksakt kilde, artefakt, miljø og tidspunkt. Bruk utfallene **bestått**, **feilet**, **ikke testet** og **ikke relevant — begrunnelse**. Skill normal utførelse fra diagnostiske omveier. Les eksterne skriv tilbake fra det eksakte målet før suksess rapporteres.

### Modenhetsord — tilpasses leveransen

| Betegnelse | Påkrevd bevis | Ingen automatisk slutning om |
| --- | --- | --- |
| Implementert | Kildeendring med kjent revisjon og intensjon | Beståtte tester eller runtime |
| Testet | Navngitte tester, utfall og eksakt miljø/revisjon | Integrasjon eller full aksept |
| Integrert | Endringen finnes i identifisert konsument/integrasjon | Innhold i et eldre distribuert artefakt |
| Sluttartefakt-verifisert | De faktiske leveransebytene og relevante ende-til-ende-porter er testet | Uprøvde fysiske klienter eller produksjonsmiljøer |
| Fysisk-/målmiljø-verifisert | Direkte observasjon på oppgitt maskin/klient/miljø | Generell støtte for uprøvde miljøer |

For ISO-prosjekter brukes eksplisitt **ISO-verifisert** om fjerde rad. For andre prosjekter velges presis betegnelse, eksempelvis installasjonspakke, container eller publisert tjenesterevisjon. Ikke påstå fysisk verifikasjon der begrepet ikke er relevant.

## 11. Kontrollert AI-agentarbeid

- Gjenopprett kontrollpunkt, kilde-/oppgavestatus, aktive prosesser, worktrees og låser før arbeid. Gjenbruk gyldige bevis; ikke start dupliserte bygg eller tester.
- Følg prosjektprofilens maksimum for agenter, samtidige jobber, tid, minne, CPU og retries. Delegasjon krever konkret behov og avgrenset leveranse.
- Arbeid i avsluttbare milepæler. Lag kontrollpunkt før kostbare eller irreversible operasjoner; commit/push ferdig arbeid og bevar WIP eksplisitt.
- Verifiser at eventuell betalt modell er konfigurert og tilgjengelig, og at tekniske kostnadssperrer, samlet perioderamme og påfyllingspolicy oppfyller prosjektprofilen. Ta høyde for flere nøkler/ruter og valuta. En prompt eller et antatt agentbudsjett er ikke teknisk håndheving.
- Hvis kontrollene ikke kan verifiseres, skal betalt bruk/fallback ikke benyttes. Bruk bare uttrykkelig godkjent inkludert/lokal rute, eller stopp. Dokumenter gjeldende oppsett før en autorisert konfigurasjonsendring.
- Ved lav kvote/rate limit: ikke start ny milepæl. Bevar en liten trygg arbeidsenhet, checkpoint og stopp; ikke start endeløse retries eller skjult betalt fallback.
- Prosesser og tilstandsendrende jobber skal ha kjent eier/supervisor. En beskyttende lås skal holdes til faktisk avslutning er verifisert, også når samtalen stopper.
- Kontrollpunkt ved avbrudd skal angi identiteter, mål, artefakter, logger, tilstand, låseier og neste trygge handling. Aldri frigi et aktivt mål for en ny arbeidstaker.
- Endre ikke scheduler, tilgang, beskyttede grener, produksjon, fysisk maskinvare eller publisering uten særskilt tillatelse. Stopp ved ferdig oppdrag; ikke utvid det til nye funksjoner.

## 12. Definition of Ready

- [ ] Problem, akseptansekriterier og avgrensning er konkrete.
- [ ] Riktig kilde/worktree, eksisterende bevis og aktive prosesser/låser er avklart.
- [ ] Risiko, tillitsgrenser, godkjenninger og nødvendige tilganger/avhengigheter er kjent.
- [ ] Test-/reviewplan og tekniske ressurs-/kostnadsrammer er realistiske.
- [ ] Trygt avbrudd og gjenopptaking er definert for tilstandsendrende arbeid.

Manglende nødvendige forutsetninger skal rapporteres som blokkering, ikke erstattes med gjetning eller fabrikerte resultater.

## 13. Definition of Done

Leveransen er ferdig innenfor sitt erklærte omfang når kriteriene er verifisert, relevante sjekker og reviewkrav er oppfylt, dokumentasjon og testbevis stemmer, endringer er lagret/pushet til riktig gren og prosesser/låser/artefakter har kjent tilstand.

Skill kode-/dokumentasjonsleveranse fra funksjonsaksept, merge, deployment, publisering og fysisk/målmiljøaksept. En PR som er opprettet, men venter på review, skal merkes slik. Ikke lukk en større oppgave fordi bare én delport er bestått.

## Praktisk PR-sjekkliste

- [ ] Problem, omfang, akseptansekriterier og risiko er oppgitt; ingen urelaterte endringer.
- [ ] Base/head, kilde-/artefaktidentitet og berørt konsument er kjent; andre arbeidstakeres WIP er bevart.
- [ ] Relevante arkitekturvalg, input-/tilgangsgrenser, feilstatus og cleanup er gjennomgått.
- [ ] Ingen hemmeligheter, private artefakter, farlige standardvalg eller svekkede kontroller er lagt til.
- [ ] Avhengigheter, advisories, patcher og lisens-/assetkrav er vurdert der relevant.
- [ ] Reproduksjon/regresjon, negative tilfeller og relevante valideringskommandoer har faktiske resultater.
- [ ] CI gjelder eksakt head; feilede, manglende, ukjørte og ikke relevante sjekker er eksplisitte.
- [ ] Nødvendig uavhengig review er utført eller står som ventende; funn er ikke omgått.
- [ ] Implementert, testet, integrert, sluttartefakt-verifisert og fysisk-/målmiljø-verifisert er skilt.
- [ ] Oppdatering, bevaring og konkret gjenoppretting er dokumentert når relevant; ingen falsk rollbackgaranti.
- [ ] Kjent risiko, begrensninger, bevissted og eventuell videre eier er dokumentert.
- [ ] Ressurs-/modellbruk, prosesser, låser og kontrollpunkt har avklart tilstand.
- [ ] Ingen merge, deployment, release, oppgavelukking eller fysisk handling gjøres uten nødvendig godkjenning.

Ved gjenbruk: behold prosjektets eksisterende styrende dokumenter, tilpass feltene én gang og gjennomfør bare relevante kontroller. Ikke legg til nye skjemaer, verktøy eller møter uten at de løser et konkret problem.
