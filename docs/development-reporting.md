# Fast rapporteringsstandard for Wilsof OS

Denne standarden gjelder normal avslutning av fremtidige Hermes-økter i Wilsof OS: fullført milepæl, dokumentert blokkering, kontrollert stopp, kvote-/API-stopp og dokumentasjonsoppdrag. Rapportering er del av leveransen, ikke et valgfritt svar som bare finnes i terminalhistorikken. Den gir aldri i seg selv tillatelse til utvikling, tester, betalt QA, VM-/ISO-/installeroperasjoner, fysisk disk/USB, Proxmox, merge eller release.

## Obligatorisk avslutning, i denne rekkefølgen

1. **Oppdatert kontrollpunkt.** Registrer faktisk omfang, eksakt kilde-/artefaktidentitet, ferdig/WIP/ikke testet, bevissted, aktive prosesser/eierskap, låser, scheduler/worker-pause, lagring i byte med UTC-tidspunkt, modell-/kostnadsstatus og én neste trygg handling. Bevar private detaljer lokalt; legg en sanert gjenopptakingsreferanse under `docs/checkpoints/` når relevant. Bevar tidligere bevis. En levende beskyttet prosess beholder sin eier/lås til faktisk avslutning er verifisert.
2. **Fullstendig Markdown-rapport.** Opprett eller oppdater `docs/development-reports/YYYY-MM-DD-<avgrenset-okt>.md` fra [malen](templates/DEVELOPMENT_REPORT_TEMPLATE.md). Behold alle 12 punktene; bruk «ikke relevant» med grunn i stedet for å utelate. Skill tidligere rapportert, historisk direkte verifisert og kontrollert på nytt med dato/klokkeslett. Ikke kjør en test på nytt bare for å fylle rapporten. Tilsvarende «ingen rapporterte CI-sjekker», «ikke kjørt», «feilet» og «bestått» må holdes atskilt.
3. **Commit og push til autorisert GitHub-gren.** Les først status, diff, branch/head/base, remote og konkurrerende worktrees. Bruk eksisterende dokumentasjonsgren eller en ny isolert gren etter omfanget. Kontroller fakta, relative lenker, diff og sensitivt innhold; stage bare egne eksplisitte filer. Ikke bruk bred staging, force-push, main-merge eller opprydding i andres arbeid. Les fjernreferansen og rapportfilen tilbake ved eksakt publisert commit; sammenlign innhold eller Git-blobidentitet. Publisering er ikke bekreftet av push-exit alene.
4. **Oppdater relevant status-issue.** Bruk #16 som permanent Wilsof-dashboard og relevant feil/arbeidsissue ved behov. Les hele gjeldende kropp og kommentarer først. Publiser et kort, ikke-duplisert sammendrag med direkte lenke til fullrapporten, eksakt commit, blokkering og neste anbefalte oppgave. Rett eventuelt bare en klart avgrenset foreldet toppstatus; bevar historikk, åpne feil og andre agenters innhold. Les den eksakte kommentaren/oppdateringen tilbake og kontroller at issue fortsatt har riktig åpen/lukket status. Ikke lukk en feil uten faktisk akseptansebevis.
5. **Direkte GitHub-lenke i terminalen.** Avslutt med fungerende rapportlenke, kort prosjektstatus, tidsstemplet tilgjengelig diskplass i byte og neste anbefalte oppgave. Oppgi relevant dokumentasjons-PR/commit og gjenstående fysiske klienttester når relevant. Slutt, uten å starte neste oppgave.

Privat kontrollpunkt får deretter publiseringskvitteringen: commit, rapport-URL, statuskommentarens URL/ID, faktisk read-back og endelig prosess-/låstilstand. Ikke lag et uendelig selvrefererende commit-løp for å legge en commit-hash inn i den samme commit-en. Git-historikken, issue-kvitteringen og det private kontrollpunktet dokumenterer avslutningen.

## Ingen scheduler eller nye arbeidere

Prosedyren utføres synkront av den aktive agenten som del av normal avslutning. Ikke opprett eller aktiver cronjob, scheduler, bakgrunnsarbeider, plugin, hook eller ny betalt modellrunde for å håndheve rapporteringen. Eksisterende pausekontroller og kostnadsgrenser skal være uendret. En issue-oppdatering eller «neste oppgave» er ikke utførelsesgodkjenning. Prosedyren er instruksjons-/dokumentasjonsbasert, ikke en automatisk bakgrunnstjeneste.

## Følsomt innhold og bevis

Publiser sanerte, presise resultater og lenker til eksakte offentlige repo-commits/CI-kjøringer. Ikke publiser rå samtalelogger, SQLite-dumper, autentisering, API-nøkler, passord, cookies, private SSH-/server-/nettverksopplysninger, VM-disker eller testhemmeligheter. Bruk logiske private bevisnavn og ikke vertsadresser eller tilgangsstier. Full lokal artefaktsti kan gis privat til eier; GitHub-rapporten kan oppgi privat artefaktrot og relativt filnavn uten vertsidentitet.

Kostnader skal skilles som dokumentert providerforbruk, estimat eller ukjent. En cache-/tokenteller eller blandet foreldresesjon er ikke faktura. En nøkkelgrense er ikke automatisk samlet prosjektbudsjett. Ikke kontakt en provider eller betal for nye bevis i et rent rapporteringsoppdrag.

## Hvis publisering er blokkert

Ved manglende GitHub-tilgang, nettverk eller autorisasjon: bevar komplett rapport og kontrollpunkt lokalt, med absolutt lokal filsti, konkret feil og hva som ikke er publisert. Ikke påstå at rapporten er på GitHub, ikke lag en antatt URL som suksesskvittering, og ikke opprett en scheduler for senere forsøk. Avslutt med blokkeringen og trygg neste manuelle beslutning. Rapporteringsforpliktelsen faller ikke bort, men publisering kan ikke erklæres ferdig før read-back.

## Forholdet til øvrige dokumenter

[Engineering Standards](ENGINEERING_STANDARDS.md), [CONTRIBUTING](../CONTRIBUTING.md), aktuell oppdragsavgrensning og sikkerhetsgrenser består. Prosjektets `.hermes.md` peker hit for økter startet i en checkout som inneholder instruksjonen. Publisering på en dokumentasjonsgren betyr ikke at filene allerede er flettet inn i andre grener/worktrees; agenten må ved gjenoppretting følge den publiserte standarden uten å merge eller overskrive en annen arbeidsstrøm.
