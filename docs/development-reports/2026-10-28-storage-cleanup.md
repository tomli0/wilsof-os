# Wilsof OS — trygg lagringsopprydding, 28. oktober 2026

**Resultat: minimumskravet 25 GiB er oppfylt.** Kontrollert 2026-10-28T18:23:22+00:00: **26981191680 tilgjengelige byte = 25.128193 GiB** på eksisterende byggfilsystem `/`. Ønsket 30 GiB er ikke nådd; marginen over minimum er bare omtrent 0,128 GiB. Ingen ISO, VM eller installasjon er startet.

## 1. Opprinnelig diskbruk og årsak

Ved kontrollpunkt 2026-10-28T17:53:14.674386+00:00: total **103240073216 byte**, brukt **92899934208 byte**, tilgjengelig **5588594688 byte (5.204784 GiB)**. `df -h` viser fortsatt omtrent **97 GiB kapasitet**, ikke 97 GiB ledig. Filsystemet har ikke krympet; det er fylt av QA-disker, ISO-kopier, materialiserte Arch-røtter/pakkecache og en omfattende Hermes-backup.

`df`, `lsblk`, `findmnt` og privilegert `pvs/vgs/lvs` ble lest. VM-disken er 107374182400 byte; eksisterende LVM-PV/LV er 105222504448 byte. **Volumgruppen har 0 ledige byte.** Bare eksisterende root og boot er permanente diskfilsystemer; ingen separat tilgjengelig byggdisk ble funnet. Ingen LV-, filsystem-, partisjons- eller VM-diskutvidelse er utført.

Privilegert `du -x` og filinventar uten tilgangsfeil viste blant annet:

| Område før opprydding | Allokerte byte / observasjon |
| --- | --- |
| Hjemmekatalog samlet | 84740096000 |
| Varig Wilsof QA-/bygg-/diskhistorikk | omtrent 40290 millioner |
| Distribuerbare interne ISO-bunter | 10162987008 |
| Hermes-backup, separat måling | 18330103808 |
| Aktiv Hermes-rot, separat måling | omtrent 18336 millioner |
| Rootless Docker | 4404383744; ett image, to stoppede containere, ingen volumer/byggcache |
| `/usr` / `/var` | 3307343872 / 550682624 |
| Aktiv `/swap.img` | 4294967296 logiske byte; bevart |

Inventaret omfatter 730581 filstier / 679551 unike fil-inoder i hjemmekatalogen. Separate `du`-målinger kan dobbelttelle hardlenker mellom kataloger og skal ikke summeres som fysisk diskbruk. Også ext4s eksisterende reserverte friområde på 4751544320 byte er bevart; reserveinnstillingene er ikke senket for å fremstille plassmålet som løst.

## 2. Klassifisering, hva som ble ryddet og hvorfor

| Klasse | Behandling |
| --- | --- |
| **A — kritisk** | Alle ISO-er, qcow2-disker og baser, firmware, Git-data/kildekode, bevis, logger/kontrollpunkter, databaser, API-/autentiseringskonfigurasjon og aktive Hermes-avhengigheter ble bevart. |
| **B — reproduserbart mellomprodukt** | Bare en kontrollert fil-liste av pakkeregistrert, inaktivt Arch-innhold, installerte standardmanualer, ferdigbyggets SFS/initramfs-duplikater og SHA256-identiske kompilerte backupkopier ble fjernet. |
| **C — ubrukt cache** | Utvalgte nedlastede Pacman-pakkearkiver, SHA512-verifiserte npm-cacheblobber og regenererbar Python-bytecode i den inaktive backupen. Pakkedatabaser, npm-indekser, Git-cache og aktive installasjoner ble ikke ryddet. |
| **D — ukjent/avhengighetsbundet** | Øvrig backup, Docker-image/containerlag, ukjent cache, firmware-/Hypridle-arkiver og alt uten en positivt verifisert begrunnelse ble beholdt. |

Før sletting ble prosjektets eksisterende eksklusive lås tatt uten venting. Prosessers cwd/root/exe, åpne filer, memory maps og mount-navnerom ble kontrollert mot målene; ingen aktive holdere eller QEMU-/bygg-/installerprosesser ble funnet. Et kontrollpunkt og en komprimert liste med **hver absolutt sti, inode, størrelse og begrunnelse** ble lagret privat før den første slettingen. Manifestets SHA256 er `3f2b393fd28aa25f018169d0129633a28a1584644923e2462dc0888957e97d96`.

Det ble utført **205487 individuelle `unlink`-operasjoner**, ikke `rm -rf`, rekursiv tre-sletting, Docker-prune eller generell cache-rensing. Hver fil måtte fortsatt ha forventet inode/størrelse/mtime og usymlinket forelder. Ingen katalog ble slettet. Pakkepayload ble kontrollert mot bevarte Pacman-filmanifester; kildesuffikser, databaser/SQLite-magi, diskformater, firmware, signeringsnøkler og ukjent tekst ble ekskludert. Bare konkret identifiserte standardmanualer ble unntatt fra den konservative tekstbevaringen.

Følgende er **utvalgte filer under stiene**, ikke hele slettede kataloger. Aliasene betyr `H=$HOME/.hermes`, `B=$HOME/.hermes-backup-20261028-130005`, `Q=$HOME/.local/state/wilsof-qa`. Den private fil-for-fil-listen er autoritativ. Tabellens blokkbyte er summert per filsti og **ikke** fysisk frigjort kapasitet ved hardlenker.

| Eksakt rot for utvalgte filer | Fjernede filstier | Summert allokering, byte |
| --- | ---: | ---: |
| `B/cache/scratch/wilsof-hypridle-verify-20261027/root` | 15876 | 2686844928 |
| `B/cache/scratch/wilsof-build-20261026/root` | 15265 | 2270781440 |
| `Q/session-20261028/build-export/work-20261028/x86_64/airootfs` | 63922 | 3528654848 |
| `Q/pacman-chroot-fix-20261028/test-root` | 63922 | 3528650752 |
| `H/cache/scratch/wilsof-hypridle-verify-20261027/root` | 15877 | 2687008768 |
| `H/cache/scratch/wilsof-build-20261026/root` | 15266 | 2270941184 |
| `B/tools` | 26 | 1386848256 |
| `Q/session-20261028/build-export/work-20261028/iso/arch/x86_64` | 1 | 1994211328 |
| `Q/session-20261028/build-export/work-20261028/iso/arch/boot/x86_64` | 1 | 251936768 |
| `Q/session-20261028/build-export/work-20261028/x86_64/boot` | 1 | 251936768 |
| `B/installs` | 165 | 390107136 |
| `B/cache/uv/archive-v0` | 55 | 130035712 |
| `B/hermes-agent/node_modules` | 9 | 101171200 |
| `B/tools/chromium-1208` | 226 | 76972032 |
| `B` | 14161 | 197316608 |
| `$HOME/.npm/_cacache/content-v2/sha512` | 714 | 195182592 |

SFS-filen og begge genererte initramfs-filene ble først hashet mot sine konkrete ISO-dataextents i bevart `internal1`; byteinnholdet er identisk. Initramfs-filene er cpio-arkiver, **ikke** testdisker eller firmware. Kompilerte backupfiler/ressurser ble SHA256-sammenlignet med de tilsvarende aktive filene som beholdes. npm-blobbenes SHA512 stemte med deres innholdsadresser.

**Konsekvens:** De seks ryddede gamle Arch-/lab-røttene er nå pensjonerte mellomprodukter, ikke fungerende chroot-/byggemiljøer. Den gamle Hermes-backupen er heller ikke lenger en komplett, direkte kjørbar runtime-backup. Databaser, konfigurasjon og kilde er bevart som proveniens, men betyr ikke at pakkeinnhold fortsatt er intakt. Ny bruk krever kontrollert rematerialisering fra gjennomgåtte innganger. Backupen er merket med dette, og de eksakte pensjonerte røttene står i kontrollpunktet. Aktiv Hermes-installasjon er urørt.

## 3. Frigjort kapasitet

| Målepunkt | Tilgjengelige byte |
| --- | ---: |
| Innledende kontrollpunkt | 5588594688 |
| Umiddelbart før selve filoppryddingen | 5558743040 |
| Umiddelbart etter selve filoppryddingen | 26981306368 |

**Observert frigjøring under selve oppryddingen: 21422563328 byte = 19.951317 GiB.** Netto økning fra innledende kontrollpunkt til dette etterpunktet er 21392711680 byte. Forskjellen skyldes blant annet ny, varig revisjonsdokumentasjon og samtidig vanlig system-/agentlogging. Filsti-allokering på 21948600320 byte er ikke brukt som påstand om faktisk frigjøring; hardlenker er hensyntatt.

## 4. Tilgjengelig plass etterpå

Ny kontroll etter bevaringsverifikasjon, **2026-10-28T18:23:22+00:00**:

- Total: 103240073216 byte; brukt: 71507337216 byte.
- **Tilgjengelig: 26981191680 byte (25.128193 GiB).**
- Minstekrav: 26843545600 byte (25 GiB), **oppfylt**.
- Ønsket sikkerhetsmargin: 32212254720 byte (30 GiB), **ikke oppfylt**.

`df -h` avrunder dette til omtrent 26G tilgjengelig. Bruk det eksakte tidsstemplede bytetallet, ikke avrundingen, ved neste beslutning. Ledig plass må måles på nytt rett før et senere bygg.

## 5. Hva som er bevart og verifisert

- Alle **11 eksisterende ISO-filstier**, **7 qcow2-filer**, **18 `.fd`-firmwarefiler**, øvrige firmware-/EFI-filer, kilde, bevis og Git-data er beholdt. Fire ISO-versjoner finnes fortsatt; kopier/hardlenker er ikke slettet bare fordi de er duplikater.
- **663 SHA256-kontroller** av bevarte artefakt-/bevisfiler og aktive originaler til fjernede backupkopier matchet før/etter. Databaser ble bevart; den levende Hermes-databasen ble kontrollert lesende med `PRAGMA quick_check` → `ok`, ikke fremstilt som byte-uendret mens agenten logger.
- `qemu-img info --backing-chain` ble lest før/etter, uten gjestestart. Begge avhengighetskjedene er uendret: `qa-overlay.qcow2` → `wilsof-disposable-install.qcow2`; og `regression.qcow2` → `issue31-overlay.qcow2` → `candidate2-install.qcow2`. Alle øvrige baser og deres metadata er også bevart.
- Alle **8 registrerte Git-worktrees** hadde uendret head/status etter oppryddingen, før rapportfilen ble lagt til. `git fsck --full --no-dangling` gikk med exit 0. Bare denne rapporten skal committes på dokumentasjonsgrenen; integrasjon står på `9aebacd`.
- `hermes --version` og `hermes config check` gikk med exit 0. Aktiv CLI, verktøy, venv-er og API-konfigurasjon er beholdt. Ingen modellforespørsel eller ny betalt QA ble brukt som funksjonssjekk.
- Rootless Docker beholder samme image og begge stoppede containere; ingen volumer var oppført. System-Dockers lille `hello-world`-image ble heller ikke fjernet.
- Sammenligning av alle opprinnelige filstier avdekket også uavhengig scratch-/runtime-churn utenfor slettelisten: én gammel prosjekt-resumehelper og tre midlertidige shell-/HTTP-cachefiler manglet. Helperen ble straks gjenopprettet fra en eksisterende backup med samme opprinnelige størrelse/mtime og SHA256-verifisert mot backupen. Bare de tre uttrykkelig identifiserte, flyktige cachefilene manglet ved ny kontroll. Årsaken er ikke sikkert tilskrevet; ingen av disse fire var med i slettemanifestet. Dette avviket er dokumentert privat, ikke skjult som en feilfri totalinventarsammenligning.

## 6. Gjenstående lagringsproblemer og grenser

Minimumet er nå nådd, men marginen over 25 GiB er liten. Det gjenstår omtrent 4,87 GiB til foretrukket 30 GiB. Videre opprydding i ukjente data, bevarte ISO-/disk-/firmwarefiler, avhengighetsbundne Docker-lag eller aktive Hermes-komponenter ble derfor ikke forsøkt. Volumgruppen har ingen ledig kapasitet, og ingen ekstra eksisterende disk er tilgjengelig. En eventuell senere større lagringsløsning krever egen godkjenning; ingen Proxmox-, partisjons-, VM-disk- eller reserveblokkendring er gjort.

Ryddede mellomprodukter må ikke gjenbrukes som komplette miljøer. Bruk en ren, gjennomgått kildeeksport ved et senere autorisert bygg. Bevarte ISO-/installasjonsresultater er fortsatt historiske bevis: `internal1` feilet installasjon og inneholder ikke `b3b8e74`; lagringsoppryddingen lukker ikke #34 eller bekrefter normal innlogging/fysisk klientaksept.

## 7. Kan neste ISO-bygg starte?

**Lagringsporten på minst 25 GiB: JA, ved den dokumenterte målingen.** Foretrukket 30 GiB: NEI. Dette er ikke en byggeordre eller full produktaksept. #34s avgrensede avhengighets-/regresjonssjekkliste, gjennomgått kildefrysing og ny kontroll av lagring/prosesser/låser må fortsatt være oppfylt før et senere, separat godkjent bygg.

Ingen ISO-bygging, QEMU-installasjon, appkodeendring, merge eller release er utført. Scheduler og workere forblir pauset. Den eide vedlikeholdslåsen holdes gjennom dokumentasjon/publisering og frigjøres med tilgjengelighetskontroll før terminalkvitteringen. Publiseringscommit, issue-URL og endelig lås-/diskstatus føres i det private kontrollpunktet, uten en selvrefererende commit-løkke.

## Kort normal avslutningsprotokoll

De sju bestilte rapportpunktene over dekker også prosjektets [faste rapporteringsstandard](../development-reporting.md):

| Standardens 12 felt | Denne økten |
| --- | --- |
| 1. Milepæler | Undersøkelse, klassifisering, filvis opprydding og bevaringsverifikasjon fullført. |
| 2. Claude QA | Ikke relevant; ingen ny review eller betalt QA. |
| 3. Kvalitet/sikkerhet | Forhåndsmanifest, eksklusiv lås, aktive referanser, katalog-/magi-/hashkontroll og gjenopprettet scratch-helper. |
| 4. Commits/CI | Kun dokumentasjonsrapport på eksisterende draft-PR #35; ingen nye applikasjonstester/CI-runder bestilt. Publiseringscommit verifiseres og lenkes fra #16. |
| 5. ISO-identitet | Bevarte `internal1`: 2545111040 byte, SHA256 `ab78770ce5c4c5fe8b7b913263ade47e4f2d8830a4ffbb6a38c935c9e9a45e83`; ingen ny ISO. |
| 6. Installasjon | Ikke utført. |
| 7. Boot/passord | Ikke utført. |
| 8. Begrensninger | 30 GiB ikke nådd; pensjonerte røtter kan ikke kjøres direkte; #34-/fysiske porter gjenstår. |
| 9. Standard/dokumentasjon | Denne rapporten og privat oppdatert kontrollpunkt; tidligere [fullrapport](2026-10-28-autonomous-session.md) er bevart. |
| 10. Modell/API | Ingen ny betalt tjeneste, separat QA-runde eller modellkonfigurasjonsendring. Ikke påstått en isolert fakturakostnad for hovedsamtalen. |
| 11. Prosesser/låser | Ingen gjest/bygg/installer; egne låser respektert, Wilsof-jobb og worker pauset. Sluttkvittering lagres etter publisering. |
| 12. Neste handling | Stopp her; ved separat gjenopptaking: #34-forbyggsjekkliste og fersk lagringsmåling, ikke automatisk bygg. |

Privat revisjonsgrunnlag: `Q/storage-cleanup-20261028/` med checkpoint, komprimert inventar, eierskaps-/slettemanifest, sletteloggen, bevaringskontroller og kontrollskript. Ingen rå samtaler, databasedumper, API-nøkler eller private serveropplysninger er publisert.
