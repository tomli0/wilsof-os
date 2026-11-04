# Wilsof OS — integration2 final closeout, 2026-11-01

Status: **PASS innenfor avgrenset virtuell installasjons-/omstartsaksept. PENDING for release.**
Rapporterings-/nykontrollperiode: 2026-11-01 fra 23:25 UTC.
Gren: `feat/integration-20261101`. Testet ISO-kilde: `b755bfabf82ece67eea3d666ea94330ff95f738e`.
Leveranse: [draft-PR #47](https://github.com/tomli0/wilsof-os/pull/47), stablet på #46. [Status-issue #16](https://github.com/tomli0/wilsof-os/issues/16).

## Bevisgrunnlag og avgrensning

Tidligere fullført installasjon og GUI-aksept er bevart, ikke gjentatt. Privat `fresh-install/prog14.json` bekrefter installerens `RC=0`; målinspeksjonen bekrefter kildecommit og installert oppsett. Eierens gjenopptakingsgrunnlag og tidligere øktrapport bekrefter akseptmatrisen nedenfor. Nye kontroller gjelder bare disk-only kald omstart, fersk normal passordinnlogging, avgrenset hemmelighetsopprydding, bevaring, avslutning og publisering.

Ingen ny ISO, installasjon, funksjon, full testsuite, betalt review, fysisk disk/USB-operasjon, merge eller release. Private logger, transkripsjoner, testidentitet og VM-disker publiseres ikke. Bildene fra denne kontrollen beholdes privat.

## 1. Fullførte milepæler

Integration2 er bygget og installert på eksisterende disponibel 24 GiB-disk. Tidligere PASS: UEFI/live, uavhengig installert oppstart, passordinnlogging, Hyprland, DMS, Command Center, Shortcuts-modal, Ghostty, Nautilus og lås/opplåsing. Manglende omstartsbekreftelse er nå PASS ved ny kald oppstart av samme installasjon. Ingen aksept overføres til andre ISO-er eller fysisk maskinvare.

## 2. Claude QA-funn og utbedringer

Ingen ny uavhengig eller betalt QA i avslutningen. Tidligere review av eldre kilde er ikke review av integration2. Uavhengig review av denne integrasjonen gjenstår.

| Funn | Status | Oppfølging |
| --- | --- | --- |
| R1: historisk DMS-kaldstart med SIGKILL/automatisk omstart | Åpen; årsak ikke bevist løst | Bevar runtime-observasjonen; funksjonell PASS betyr ikke krasjfri runtime |
| R2: hyprland-dialog/libhyprtoolkit-krasj | Åpen | Ingen ny vendorpatch eller løst-påstand |

## 3. Kodekvalitet og sikkerhetsstatus

Tidligere kontrollpunkt oppgir **375 passed / 2 skipped**, ShellCheck ren på ISO-kilden; dette ble ikke kjørt på nytt. Integration1s manglende live-payload ble rettet i `b755bfabf82ece67eea3d666ea94330ff95f738e`: shortcuts-/appearance-verktøy, keybind-manifest og idle-lock-konfigurasjon. Integration1 beholdes som feilbevis, ikke akseptert kandidat.

Byggmanifestet dokumenterer et miljøavvik: `pacstrap`-PID-unshare ble deaktivert kun i den disponible byggeroten etter GPGME-feil; signaturkontroll ble ikke deaktivert. Dette er tidligere dokumentert byggbevis, ikke en ny diagnostisk reproduksjon.

`/tmp/install-transcript` var allerede fraværende etter kald omstart. Eksplisitt fjerning og fravær ble likevel bekreftet før avslutning. Avgrenset gjesteskann av 212 filer i `/tmp`, `/var/tmp`, `/root`, `/home` og `/var/log` fant ingen gjenværende kopi av testhemmeligheten og ingen ulesbare filer. Én testgenerert privat vertskopi ble sladdet; etterkontroll av 402 tekstfiler i øktens avgrensede bevisområde fant ingen treff. Separate private credential-filer beholdes. Dette er ikke forensisk sletting; historiske verktøy-/samtalelagre og ledige diskblokker er ikke undersøkt eller renset. Ingen hemmelighetsverdi eller rå transkripsjon publiseres.

## 4. Commits og CI-status

| Identitet | Rolle | Verifisert status |
| --- | --- | --- |
| `2122cd012a5edba30b0025cd68e2731b1d9e9a67` | Uendret stablet base #46 | Ingen merge |
| `b755bfabf82ece67eea3d666ea94330ff95f738e` | Eksakt integration2 ISO-kilde | Lokal suite historisk 375/2; `gh pr checks 47` rapporterte ingen sjekker ved avslutningskontrollen |
| Etterfølgende docs-commit | Kun denne rapporten og sanert kontrollpunkt | Fjern-head og begge blober skal leses tilbake før publiseringskvittering |

Ingen CI-grønn påstand uten rapporterte sjekker. Den rene dokumentasjonscommit-en bruker `[skip ci]` for ikke å gjenta fullførte tester i denne avslutningen. PR #47 var OPEN/DRAFT ved kontroll; ingen merge eller release. Publiseringscommit og endelig fjernstatus kvitteres i #16 og privat kontrollpunkt, uten selvrefererende commit-løkke.

## 5. ISO-filnavn, størrelse, SHA256 og plassering

| Felt | Verdi |
| --- | --- |
| Fil | `wilsof-internal-2026.11.01-integration2-x86_64.iso` |
| Kilde | `b755bfabf82ece67eea3d666ea94330ff95f738e` |
| Byte | `2549536768` |
| SHA256 | `cfe0571664b69b94bb8f2aebe0121704aa3e8feb063b11270fee227debc95eec` |
| Privat artefaktrot | `internal-test-20261101-integration2/` |
| Bygg | Bevart manifest: `build_exit=0`; ingen ombygging i avslutningen |

**49/49** bevarte artefakter var hash- og størrelsesidentiske mot tidligere manifest/kontrollpunkt: 47 historiske objekter pluss integration1 og integration2 ISO. **15/15** bevarte qcow2-filer bestod ikke-reparerende offline-sjekk. Originale QA-disker ble ikke tilkoblet eller modifisert. Den egne disponible installasjonsdisken ble kontrollert før og etter gjestekjøringen; sluttkontroll `qemu-img check` exit 0. Endelige disk-/firmware-hasher finnes kun i privat bevaringskvittering.

## 6. Resultat fra full installasjon

| Port | Status og bevisgrunnlag |
| --- | --- |
| UEFI, bootmeny, live-skrivebord og DMS | PASS, tidligere direkte kontrollpunkt |
| Diskvalg og blankhetssjekk | PASS, tidligere installasjonskontroll |
| Full fersk installasjon | PASS, installer `RC=0`, bevart sluttresultat |
| Disk-only oppstart uten ISO | PASS, tidligere og ny oppstart |
| Normal passordinnlogging | PASS, tidligere og fersk greetd/PAM-økt |
| Hyprland, DMS, Command Center, Shortcuts-modal | PASS, tidligere installert aksept; ny oppstart bekreftet Hyprland/DMS |
| Ghostty og Nautilus | PASS, tidligere installert aksept, ikke gjentatt |
| Lås/opplåsing | PASS, tidligere installert aksept, ikke gjentatt |
| Kald omstart og ny innlogging | PASS, denne avslutningen |
| Kontrollert avslutning | PASS, QGA powerdown, QEMU exit 0, ingen QEMU igjen, siste offline-sjekk 0 |

Ledig lagring 2026-11-01T23:35:22Z: **65223786496 byte = 60.744384765625 GiB**. Ingen bevarte artefakter ble ryddet bort.

## 7. Oppstart og passordinnlogging

Eksisterende `launch-disk.sh` startet den disponible installasjonen uten ISO, etter at fravær av konkurrerende QEMU var bekreftet. Gjesten startet fra `/dev/vda2` (ext4), ikke live-miljø. Greetd ba synlig om passord; vanlig tastaturinnlogging ga ny PAM-session **2026-11-01T23:29:39Z**. Session var active/Wayland, Hyprland og DMS aktive, og rendret skrivebord uten blokkerende dialog ble visuelt kontrollert. Installert `SOURCE_COMMIT` var eksakt ISO-kilde.

Dette er en **kald omstarts-/startup-test etter tidligere avslutning**, ikke en påstand om en ny `systemctl reboot`-syklus inne i samme QEMU-prosess. Tuigreet er fremdeles standard; ReGreet-kandidaten er ikke godkjent av denne innloggingen.

## 8. Gjenstående feil og begrensninger

**PENDING:** R1, R2, uavhengig review og fysiske maskinvaretester. Wi-Fi, lyd, Bluetooth, GPU/firmware/USB/Secure Boot, suspend/resume, fysisk tastaturruting og flerskjerm er ikke godkjent her. TCG-funksjonsaksept er ikke ytelsesaksept eller bevis på feilfri runtime. Ingen åpne feil lukkes av denne rapporten.

## 9. Engineering Standards og dokumentasjons-PR

Følger [rapporteringsstandarden](../development-reporting.md) og alle 12 rapportpunkter. Kun eksplisitte egne docs-filer stages på #47-grenen; andre worktrees og kildefiler beholdes. Rapporten er publisering på draft-gren, ikke merge. Sensitivt innhold, relative lenker og diff kontrolleres før push; eksakt fjern-head og dokumentblober kontrolleres etterpå. [Sanert kontrollpunkt](../checkpoints/integration2-final-closeout-20261101.md).

## 10. API-/modellforbruk der det kan dokumenteres

Denne avslutningen bruker hovedsesjonens `gpt-6.1-sol` / `openai-codex`. Ingen ny betalt reviewer, delegasjon, provider-budsjettprobe eller endring av modell-/betalingsoppsett. Fullstendige faktiske kostnader og samlede token-/kalltall er ikke målt her; ukjent er ikke null faktura. Tidligere økters forbruk tilskrives ikke denne avslutningen.

## 11. Aktive prosesser og prosjektlåser

Egen gjest ble avsluttet med QGA `guest-shutdown` powerdown. Den nøyaktige QEMU-prosessen er avsluttet med **exit 0**, og ny prosesskontroll fant ingen QEMU før offline sluttkontroll. Prosjektlåsen holdes gjennom publisering/read-back av den eksisterende, identifiserte øktholderen; deretter skal dokumentert normal avslutning brukes etter ny PID/starttid/kommando/fd/inode-eierskapskontroll, og tilgjengeligheten skal probes. Faktisk låsfrigivelse kvitteres i #16 og privat kontrollpunkt, ikke på forskudd.

Scheduler er disabled/paused og worker `paused=true`, `stop_requested=false`; ingenting reaktiveres.

## 12. Neste anbefalte handling

Uavhengig gjennomgang av integration2-kilden og denne dokumenterte evidensen før eventuell videre fysisk testbeslutning. R1/R2 og fysiske porter beholdes åpne. Ingen ny utvikling, ISO, installasjon, merge, release eller automatisk oppgave starter ved avslutningen.
