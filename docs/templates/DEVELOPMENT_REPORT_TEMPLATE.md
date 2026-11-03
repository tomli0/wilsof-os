# [Prosjekt] — sluttrapport [YYYY-MM-DD / avgrenset økt]

Status: [ferdig innenfor omfang / blokkert / kontrollert stopp; ikke full funksjonsaksept uten bevis].
Utviklingsperiode UTC: [start–slutt]. Rapporterings-/nykontrollperiode UTC: [tid].
Kildegren og eksakt commit: [verdier]. Status-issue: [lenke]. Dokumentasjons-/leveranse-PR: [lenke].

## Bevisgrunnlag og avgrensning

- Tidligere rapportert: [hvilke påstander og fra hvilken rapport].
- Historisk direkte verifisert: [lagrede kommando/resultater, eksakt testet revisjon/artefakt].
- Kontrollert på nytt: [konkrete lesinger, UTC-tidspunkt, begrensninger].
- Ikke utført / ikke autorisert: [kode, tester, bygg, VM, installasjon, QA, fysisk/infra, merge/release etter faktisk omfang].
- Private bevis: [logiske navn; ikke rålogger, hemmeligheter eller private serveropplysninger].

## 1. Fullførte milepæler

[Hva er faktisk levert? Skill fullført leveranse fra WIP, blokkering og gjenstående aksept.]

## 2. Claude QA-funn og utbedringer

[Bruk «ikke relevant / ingen ny QA» hvis dette ikke inngikk. Oppgi faktisk reviewer/rute, eksakt gjennomgått commit, avvik og kostnadsramme. Ikke bestill ny betalt review for å fylle rapporten.]

| ID | Alvorlighet | Konkret bevis | Bekreftet/avkreftet/ubekreftet | Utbedring eller åpen oppfølging |
| --- | --- | --- | --- | --- |
| [ID] | [nivå] | [fil/revisjon/resultat] | [status] | [commit/issue eller gjenstår] |

## 3. Kodekvalitet og sikkerhetsstatus

[Rotårsak, minste rettelse, tillitsgrenser, privilegier, input/symlenker, feil/cleanup, disk og autentisering der relevant. Testkommando, exitstatus og revisjon; ikke overfør historisk pass til nye bytes.]

## 4. Commits og CI-status

| Commit | Gren / endring | CI-kjøring og eksakt head | Faktisk resultat / nykontrolltid |
| --- | --- | --- | --- |
| [full SHA] | [rolle] | [direkte lenke / ingen rapporterte sjekker] | [bestått/feilet/ikke kjørt] |

[PR-/issue-state lest tilbake; merge/release separat. Oppgi workflowfiltre og manglende CI uten å kalle det grønt.]

## 5. ISO-filnavn, størrelse, SHA256 og plassering

[For annet sluttartefakt: samme proveniens. Ingen produsert fil = «ikke bygget», ikke et oppdiktet filnavn/hash.]

| Felt | Verdi og bevisstatus |
| --- | --- |
| Filnavn og faktisk kildecommit | [verdi] |
| Størrelse i byte | [verdi] |
| Full SHA256 | [verdi; faktisk kontrollert når?] |
| Plassering | [offentlig URL eller privat artefaktrot + relativt filnavn] |
| Aksept / tidligere artefakter | [uendret? hvilke kontroller er nye, hvilke er ikke gjentatt?] |

## 6. Resultat fra full installasjon

| Port | Bestått / feilet / ikke testet / ikke relevant | Eksakt bevis eller begrunnelse |
| --- | --- | --- |
| UEFI-oppstart fra ISO | [status] | [bevis] |
| Live-skrivebord | [status] | [bevis] |
| Diskvalg og sikkerhetskontroller | [status] | [bevis] |
| Full installasjon, installer exit 0 | [status] | [bevis; QEMU-exit er ikke installer-exit] |
| Disk-only boot uten ISO | [status] | [bevis] |
| Vanlig passordinnlogging | [status] | [bevis] |
| Installert skrivebord / apper | [status] | [bevis] |
| Lås, feil passord, korrekt opplåsing | [status] | [bevis] |
| Avslutning / opprydding | [status] | [faktisk prosessavslutning, eier/lås] |

Lagring ved [UTC]: [eksakt tilgjengelige byte], [GiB beregnet fra byte / 1073741824]. Krav: [byte/GiB], differanse: [byte]. Skill reell lagringsmangel fra en misvisende programfeil. [Inventerings-/tilgangsbegrensninger, ingen implisitt slettetillatelse.]

## 7. Oppstart og passordinnlogging

[Eksakt installert image/kilde. Ikke bruk root/runuser eller eldre innlogging som bevis for ny vanlig autentisering.]

## 8. Gjenstående feil og begrensninger

[Åpne issues og porter, emulator-/maskinvare-/fysisk klientbegrensninger, ukjente forhold, hva som krever eierens faktiske testing. Ikke lukk feil uten aksept.]

## 9. Engineering Standards og dokumentasjons-PR

[Relevante standarder, rapportmal, PR/base/head, faktisk tekst-/lenke-/diffkontroll og manglende uavhengig review. Skille publisert på gren fra merget.]

## 10. API-/modellforbruk der det kan dokumenteres

| Rolle / faktisk modell | Periode / omfang | Kall / tokenfelter / cache | Kostnad og bevisstatus |
| --- | --- | --- | --- |
| [verdi] | [avgrensning] | [tall eller ukjent] | [målt/estimert/ukjent; valuta; ikke dobbelttell] |

[Fallback-/kvoteavvik, håndhevet nøkkelgrense versus samlet prosjektbudsjett, actual_cost mangler?, senere samtale i samme sesjon?, ingen unødvendig providerprobe.]

## 11. Aktive prosesser og prosjektlåser

[Prosess-/supervisoreier og sjekket tidspunkt. Lås faktisk holdt av hvem eller tilgjengelig etter probe. Historisk PID/åpen DB-sesjon er ikke gjeldende prosess. Scheduler/job og worker-kontroll hver for seg; eksisterende gateway er ikke aktiv prosjektarbeider. Publiser ikke private tilgangsdetaljer.]

## 12. Neste anbefalte handling

[Én avgrenset neste utviklingsoppgave, forutsetninger/ressurser, nødvendig separat godkjenning, uutførte fysiske klientkontroller. Start ingenting automatisk.]

## Publiseringskvittering

[Etter faktisk push/read-back: eksakt commit og rapport-URL gis i status-issue og terminal; privat kontrollpunkt får endelig kommentar-ID, remote-verifikasjon og prosess-/låstilstand. Ikke oppgi antatt suksess på forhånd, og unngå selvrefererende commit-løkker. Ved blokkering: lokal absolutt rapportsti + konkret upublisert rest.]

Følg [fast rapporteringsstandard](../development-reporting.md): kontrollpunkt → full rapport → commit/push → status-issue → direkte terminal-lenke. Ingen scheduler eller bakgrunnsarbeider.
