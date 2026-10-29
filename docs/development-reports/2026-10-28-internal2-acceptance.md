# Wilsof OS — internal2: bygg og virtuell funksjonsaksept

**Resultat: én internal2-ISO er bygget, installert med dokumentert installer-exit 0 og testet gjennom alle 13 avtalte funksjonelle VM-porter. Oppstarts-/grafikkmerknadene nedenfor er ikke fjernet eller omdefinert til en feilfri runtime.** Ingen produksjonskode er endret i oppgaven. Ingen merge eller offentlig release.

Utvikling/test UTC: **28. oktober 2026, 22:16–23:50**. Rapportering starter etter dette. Gren: `integration/internal-iso-20261026`, [draft-PR #27](https://github.com/tomli0/wilsof-os/pull/27), [installer-issue #34](https://github.com/tomli0/wilsof-os/issues/34), [permanent dashboard #16](https://github.com/tomli0/wilsof-os/issues/16).

Eksakt frosset ISO-kilde: **`f7c39451e2ff00ae28b6eb2a1809b17ae29072fe`**. Produksjonskoden er identisk med den sist uavhengig gjennomgåtte **`f628884b314dd13c3bf9d7059eee2fefec1b3400`**; senere kildehistorikk før bygg inneholder bare QA-/rapportdokumentasjon.

[Strukturert, sanert bevisoversikt med 13 porter, tidsstempler, hashes og ni faktiske skjermbilder](../qa/2026-10-28-internal2-acceptance.json). [Gjenopptakingskontrollpunkt](../checkpoints/internal2-acceptance-20261028.md).

## Bevisgrunnlag og avgrensning

- Den oppgitte [siste Claude-rapporten](2026-10-28-final-claude-qa-f628884.md), GitHub-innhold ved eksakt commit, PR-/issue-tråder, CI, worktrees, lås, pausekontroller, eksisterende artefakter og faktisk lagring ble rekonstruert før bygg.
- Nytt direkte bevis: signaturverifisert, ny Arch-byggerot; ett fullbygg; inspeksjon av den ferdige ISO-ens immutable root; én ny disponibel virtuell disk; faktisk interaktiv PTY-installasjon; separat disk-only-oppstart; ordinær greeterautentisering; renderte apper og tekstlagring; ekte lås, PAM-avvisning og korrekt opplåsing; kontrollerte avslutninger og offline qcow2-kontroller.
- Tidligere native-regresjoner og Claude-review er historiske bevis for identifisert kode, ikke nye kjøringer i denne oppgaven. Eksakt kilde-CI ble lest tilbake med logg og resultat.
- Automatiserte struktur-/prosess-/PTY-/QMP-resultater holdes atskilt fra visuelt inspiserte QEMU-framebufferbilder. Ingen fysisk skjerm, tastatur, USB, firmware, GPU, Wi-Fi, lyd eller suspend er testet.
- Private logger, testhemmelighet, testdisk, firmware og krasjbevis ligger i den varige bevisgruppen `internal2-20261028/`, adskilt fra ISO-bunten. Ingen rå samtaler, credentials, VM-disk eller krasjdump publiseres i Git.

## 1. Fullførte milepæler

1. Kildegrunnlaget er frosset og kontrollert mot den eksisterende reviewen.
2. `wilsof-internal-2026.10.28-internal2-x86_64.iso` er produsert med **bygg-exit 0**, i **ett fullbygg, null ombygginger**.
3. Den faktiske ISO-en er startet via UEFI og installert på en **ny, selvstendig 24 GiB qcow2**, ikke internal1-disken eller en overlay over den.
4. Installasjonen er avsluttet med **installer-exit 0**, deretter er målsystemet verifisert og installasjonsgjesten avsluttet.
5. Samme vellykket installerte disk er startet med **ingen ISO tilkoblet** og ferske UEFI-variabler. Vanlig passordinnlogging, apper, lås og ekte opplåsing er gjennomført.
6. Begge QEMU-livsløp er avsluttet kontrollert. Siste offline diskkontroll og uendret ISO-hash er bekreftet.

Dette er funksjonell virtuell aksept med eksplisitte merknader, ikke en generell stabilitetssertifisering eller fysisk installasjonstillatelse.

## 2. Claude QA-funn og utbedringer

Ingen ny Claude-review, delegert utviklingsagent eller betalt reviewrunde ble startet. Det var ingen ny sikkerhetskritisk produksjonsendring som krevde dette.

Siste eksisterende Claude Sonnet 4.6-review gjelder `f628884`: **`no_blocking_findings`**, 0 critical/high/medium, 3 low og 2 info. Originale funn og separate vurderinger er bevart i [QA-resultatet](../qa/2026-10-28-claude-f628884.json): QA01 er valgfri lesbarhet; QA02s substring-påstand er konkret avkreftet; QA03 er en valgfri testassert; QA04/QA05 er tilsiktet eller allerede dokumentert atferd. Ingen funn er slettet for å få grønn status.

Følgende installergrunnlag er kontrollert i frosset kilde og faktiske bildebytes:

| Krav | Verifikasjon |
| --- | --- |
| `b3b8e74ea5e6b8513d9bfde27b7d672921a43839` inkludert | Ancestry og relevant produksjonskode kontrollert. Eksternt mål bruker `arch-chroot -r TARGET ...`; allerede forberedt `/` kjører direkte. |
| `f628884b314dd13c3bf9d7059eee2fefec1b3400` inkludert | Kilde-/testendringene finnes; ingen senere produksjonsdiff. |
| Eksplisitt `arch-install-scripts` | Pakkeliste, bygg-gate med baseline >=31, `vercmp` og reell `arch-chroot -r -h`; faktisk ISO/live-versjon **32-1**. |
| Resolver-postbetingelse | Eksakt `runtime/provision-target` er inkludert; faktisk installert resolver-lenke er bevart etter provisioning. |
| Issue #34-regresjoner | Full `/`-gren, negative kontrakter og opt-in native-test finnes i kilden. Tidligere native-resultat: **2 passed**, ikke kjørt på nytt her. |

Nye runtime-observasjoner R1–R5 beskrives i seksjon 8. De er ikke tilskrevet eller avvist av en review som fant sted før ISO-testen.

## 3. Kodekvalitet, sikkerhet og byggemetode

Byggeroten ble opprettet på nytt fra **Arch bootstrap 2026.10.01**, SHA256 `0c9c97b7a58a8a023c9e07f84cb307a9e8006e65d8fc4c17b83ddc8010b45c10`. GPG ga GOODSIG/VALIDSIG for `3E80CA1A8B89F69CBA57D98A76A5EF9054449A5C`; WKD-nøkkelen ble sammenholdt med Archs offisielle utviklerkatalog. Ingen pensjonert byggerot ble kjørt eller brukt som intakt miljø.

Bygget fulgte materialiserings-/Archiso-flyten i `scripts/build-iso.sh` og `docs/internal-test-runbook.md`: ren `git archive`, eksakt `SOURCE_COMMIT`, read-only kilde og verifisert lokal pakke, `prepare-iso.py`, `boot-profile.py` og **Archiso 91-1 / `mkarchiso -v -r`** med nye, separate work/profile/output-stier. Den konkrete kommando-/miljøloggen er bevart privat.

Den dokumenterte miljøforutsetningen fra tidligere CheckSpace-feilsøking ble etablert **før** mkarchiso: den nye image-roten ble bind-mountet til seg selv bare i det private mount-namespace-et. Derfor ble materialiseringskommandoene utført eksplisitt før mkarchiso i stedet for å gjenta en allerede kjent manglende-mountpoint-feil gjennom wrapperen. Ingen repo-kode, signaturregel eller sikkerhetstest ble endret. Upstreams releng-pacman.conf ble ikke svekket; det installerte målsystemets `CheckSpace` og Required-signaturpolicy er kontrollert aktive. Work beholdes fordi det var opprettet for denne mountpoint-forutsetningen.

Isolasjonen brukte private mount/PID/proc/dev/run-grenser, read-only sysfs og et minimalt `/dev` uten fysiske blokknoder. Ingen hjemmekatalog, SSH-/API-legitimasjon eller fysisk disk ble bundet inn. En transient scope begrenset bygget til TasksMax 1800 og MemoryMax 8G under eksisterende foreldregrense; ingen global verts-/Proxmox-innstilling ble endret.

En ugyldig speiladresse ga HTTP404 under bootstrap-forberedelsen og ble konkret korrigert **før første fullbygg**. Selve fullbygget feilet ikke. Ingen signatur-/integritetsomgåelse, deaktivert sikkerhetstest eller ny Hypridle-pakkebygging ble brukt.

Immutable-audit bekrefter eksakt kilde og installerpayload, låst root, uinitialisert maskinidentitet, ingen innebygd live-konto, forventede root-eide kjørbare entrypoints, fravær av private filnavntreff og uendret pakke-/binærpinne. Dette er en avgrenset inkluderings-/identitetskontroll, ikke en full sikkerhetssertifisering.

## 4. Commits og CI-status

| Commit | Rolle | Kontrollert resultat |
| --- | --- | --- |
| `b3b8e74ea5e6b8513d9bfde27b7d672921a43839` | Opprinnelig API-mount-/chroot-rettelse | Inkludert i frosset kilde. |
| `f628884b314dd13c3bf9d7059eee2fefec1b3400` | A–D-gater og kontrakttester, sist reviewet produksjonskode | Eksakt-head check `test`: success; historisk native 2 passed. |
| `f7c39451e2ff00ae28b6eb2a1809b17ae29072fe` | Frosset faktisk ISO-kilde | [CI 40777612201](https://github.com/tomli0/wilsof-os/actions/runs/40777612201), head kontrollert eksakt: **completed/success**, `test` success, **201 passed / 1 skipped**. |
| Påfølgende dokumentasjonscommit | Denne rapporten, sanert evidens, skjermbilder og kontrollpunkt | Eksakt publiserings-SHA, fjern-read-back og den nye head-CI kvitteres på #27/#34/#16 etter faktisk push. Ingen antatt selvrefererende SHA. |

Kilde-CI kjørte pytest, JSON-validering, ShellCheck med separate sh/bash-dialekter og `git diff --check`. Den ene opt-in native-testskippen er ikke omdefinert til pass. Ingen workflow eller test er endret. Eksisterende suites er ikke repetert lokalt bare for presentasjon.

Integrasjons-worktree var rent før frys. Åtte registrerte worktrees ble inventert; ingen annen arbeidsstrøm ble sjekket ut, slettet eller redigert. PR #27 forblir draft/umerget; main og andre PR-er er ikke endret av leveransen.

## 5. ISO-identitet og bevaring

| Felt | Faktisk verdi |
| --- | --- |
| Filnavn | **`wilsof-internal-2026.10.28-internal2-x86_64.iso`** |
| Kildecommit | **`f7c39451e2ff00ae28b6eb2a1809b17ae29072fe`** |
| Størrelse | **2546053120 byte** |
| SHA256 | **`dc4bfb3944767e743f858880d32b0d1179b5a6c629e5cfed68410e3a73a4f8d1`** |
| Lagring | Privat intern artefaktgruppe `internal-test-20261028-internal2/`; ISO, `SHA256SUMS` og separat manifest. Eksakt lokal sti gis privat til eier. |
| Byggresultat | **Exit 0, ett fullbygg, null ombygginger.** Navnet følger eksisterende `WILSOF_ISO_VERSION`; intet navneavvik. |
| Siste uavhengige checksum | Etter siste gjesteavslutning, **2026-10-28T23:50:22Z**, identisk med før runtime-test. |

Den gjenbrukte, verifiserte Hypridle-pakken er `hypridle-0.1.8-2.1-x86_64.pkg.tar.zst`, pakke-SHA256 `3182ffaa24b0382c39614c460e15f90ff730d7da4f60378123d9b3df09c01d04`, binær-SHA256 `3b5b36e21cb88e2939ed42f5d1a87c8b05f3c95876703545dd74dd280ee7fdd9`. Begge er kontrollert i bilde/installerte bytes.

Alle **fire tidligere ISO-er** er hashet på nytt og samsvarer med bevaringsmanifestet, inkludert den feilede internal1. Alle **24 varige** tidligere artefakt-/kontrollpunktstier i den relevante inventarseleksjonen finnes. To allerede manglende midlertidige scratch-kopier av eldre firmware ble oppdaget ved inventar; SHA256-identiske kopier finnes fortsatt i eksisterende backup og er kontrollert. De ble ikke slettet av denne oppgaven. Ingen ISO, gammel testdisk, firmware eller kontrollpunkt er ryddet bort.

## 6. Installasjon og full akseptansematrise

| Nr. | Avtalt port | Resultat og bevisart |
| --- | --- | --- |
| 1 | UEFI-oppstart fra faktisk ISO | **Bestått**, automatisert: 64-bit UEFI, faktisk ISO-live-root på read-only squashfs, korrekt kilde. |
| 2 | Normal live-desktop | **Bestått med merknad R3**, faktisk visuelt inspisert panel/skrivebord etter kald TCG-oppstart. Tidlige svarte bilder var ikke pass. |
| 3 | Installerens diskvalg og sikkerhetsbekreftelse | **Bestått**, ekte syntetisk PTY: sole ny `WILSOF-INTERNAL2-NEW`, 25769803776 byte, blank/umontert uten signaturer før start; faktisk full-null-/identitetsvern og eksakt `ERASE /dev/vda`. |
| 4 | Avsluttet installasjon, exit 0 | **Bestått**, dokumentert **installer PID 1578, exit 0**; driver også exit 0, 5/5 prompter, completion-message, ingen timeout eller plaintext-passord i terminalutskriften. |
| 5 | Verifisert installert system | **Bestått**, struktur-/sikkerhetskontroller og `findmnt --verify` uten feil/advarsler. |
| 6 | Avsluttet installasjonsgjest | **Bestått**, rent umontert mål, kontrollert guest-powerdown, QEMU-exit 0, offline qcow2 check exit 0. |
| 7 | Disk-only boot uten ISO | **Bestått**, nye launch-argv og QMP block-backends uten ISO. Faktisk `/dev/vda2` ext4 som `/`, ESP på `/boot`, ingen Archiso-live-root. Ferske UEFI-variabler. |
| 8 | Vanlig passordinnlogging | **Bestått**, visuelt bekreftet username-/password-prompt; privat QMP-tastaturinput; greetd/PAM åpnet UID1000-økt. Ingen root/runuser-omgåelse. |
| 9 | Skrivebord og grunnleggende apper | **Bestått med R1/R2/R4/R5**, faktisk renderte Ghostty, Firefox, Nautilus og Text Editor; syntetisk tastaturredigering/Ctrl+S og fil-read-back. |
| 10 | Lås av økt | **Bestått**, én faktisk Super+L, Hyprlock PID2125 og visuelt klar merket passordflate. |
| 11 | Avvisning av feil passord | **Bestått**, PAM `authentication failure` kl.23:45:54; samme Hyprlock PID levde videre. Senere skjermdump viser fortsatt låseflate, ikke en vedvarende synlig feilmelding. |
| 12 | Riktig passord låser opp | **Bestått**, privat ordinær passordinput; locker avsluttet, original compositor PID757 og app-PID1400/1436/1715/1999 beholdt; visuelt gjenopprettet tekstredigerer. Ingen kill av locker eller administrativ logout. |
| 13 | Kontrollert avslutning | **Bestått**, normal guest-powerdown, QEMU-exit 0, offline check exit 0 og uendret ISO-hash. |

Installasjonens faktiske periode: **22:36:02–23:25:23 UTC**, omtrent **49,34 minutter** under TCG. Ingen suksess ble erklært mens den fortsatt kjørte.

Målverifikasjonen bekrefter UEFI fallback-/loaderfiler, korrekt kilde, UID1000 med initialisert passordhash, låst root, fravær av live-konto/live-sudoers/autologin, intakt `/etc/mtab`, bevart resolver, aktive pakkekontroller og korrekt Hypridle-binær. Hemmelige hashverdier publiseres ikke.

Ved normal unmount holdt bare målets Pacman-gpg-agent roten åpen. `fuser` identifiserte den eksakte target-spesifikke agenten; `gpgconf --homedir /mnt/wilsof/etc/pacman.d/gnupg --kill gpg-agent` stoppet bare denne, deretter lyktes vanlig unmount. Ingen force/lazy-unmount. Blokkskrivningstall var stabile før nedstenging. Dette er dokumentert opprydding, ikke en ny installerrettelse eller falsk installasjonsfeil.

Ledig plass før byggforberedelse **22:18:47 UTC**: **128296656896 byte (119,485569 GiB)**, over 25 GiB-kravet. Etter bevaring av ny byggerot, ISO-kopier, disk og bevis **23:51:35 UTC**: **106667229184 byte (99,341599 GiB)**. GiB er beregnet som byte/1073741824. Ingen diskutvidelse, LVM-/partisjons-/reserveblokk- eller Proxmox-endring er utført.

## 7. Diskoppstart, autentisering og faktisk GUI

Installerte firmwarevariabler er ferske, mens firmware fra installasjonsgjesten er bevart separat. Disk-only-gjesten hadde kun firmware og den nye vellykket installerte disken som innsatte block-backends; emulerte tomme CD-/SD-enheter er ikke en tilkoblet ISO. Root-/boot-mounts er kontrollert innenfra gjesten, uavhengig av argv.

Vanlig greeter-PAM åpnet brukerøkten **23:31:10 UTC**. User-manager-/QGA-prober etterpå er diagnostikk, ikke erstatning for denne innloggingen. Apper ble startet gjennom den ekte bruker-manageren med ordinære binærer; deres prosess-/compositorklasser er sammenholdt med faktiske bilder. Ingen renderer- eller sandbox-overrides ble funnet i de kontrollerte app-prosessene. QEMU bruker **TCG, Nehalem, 2 vCPU og 6144 MiB**, et eksplisitt emulatorvalg, ikke fysisk GPU-/ytelsesaksept.

Visuelle bevis:

- [Live-skrivebord](../qa/internal2-20261028/live-desktop.png) og [disk-only-greeter](../qa/internal2-20261028/disk-only-greeter.png).
- [Terminal med UID1000 og faktisk shell](../qa/internal2-20261028/terminal.png).
- [Firefox med rendret lokal HTML/CSS](../qa/internal2-20261028/firefox-local-fixture.png): dette er ikke Internet-/TLS-test. DNS-oppslag av archlinux.org lyktes separat.
- [Nautilus med faktiske lokale filer](../qa/internal2-20261028/files.png) og [Text Editor med testtekst](../qa/internal2-20261028/editor.png). Kald app-rendering krevde venting; tomme tidlige bilder ble ikke akseptert.
- [Hyprlock klar](../qa/internal2-20261028/lock.png), [låseflaten beholdt etter PAM-avvisning](../qa/internal2-20261028/wrong-password-lock-retained.png), [opprinnelig økt gjenopprettet med lagret tekst](../qa/internal2-20261028/unlocked-original-session.png).

Lås ble bedt om kl.23:44:27; ferdig passordflate ble observert ved den første kontrollen etter omtrent 30 sekunder. Dette er en øvre observasjonsgrense, ikke nøyaktig låse-/renderlatens. Automatisk femminutters idle-lås, suspend/resume og fysisk input er ikke testet. `LockedHint=no` i logind ble ikke brukt som bevis for lås; faktisk session-lock/PAM-flate og ekte opplåsing er grunnlaget.

## 8. Feil, funn og gjenværende begrensninger

| ID | Konkret observasjon | Vurdering og avgrensning |
| --- | --- | --- |
| R1 | Første installerte DMS-UI PID827 ble drept med SIGKILL, parent816 sluttet med status137. Systemd restartet automatisk til parent1097/UI1103. | **Bekreftet recovered cold-start-hendelse; rotårsak/killer ukjent.** Ingen kernel-OOM-melding, rikelig tilgjengelig RAM, MemoryMax=infinity og effektiv TimeoutStartSec=300. Ikke feilaktig tilskrevet OOM eller 90s upstream-timeout. Ingen manuell restart/reparasjon. NRestarts var fortsatt1 ved siste kontroll, og økten/apptestene/lås fungerte etterpå. Ikke en ren oppstartspåstand. |
| R2 | `hyprland-dialog` PID1906 SIGSEGV i `libhyprtoolkit` `CWaylandBuffer`, mens den skulle vise «Application Not Responding» for kald Nautilus. | **Bekreftet hjelpedialogkrasj**, ikke Nautilus-, Hyprland- eller Hyprlock-krasj. Nautilus rendret deretter normale lokale filer. Stack og dump bevart. Mekanismen i bufferopprettelse er observert; full upstream-rotårsak/TCG-sammenheng ikke fastslått. Ingen spekulativ patch eller rendererunntak. |
| R3 | Live `gvfsd-fuse` SIGSEGV under tidlig provisioning. | **Bekreftet live-hjelpekrasj**; live-desktop ble funksjonell. Det installerte livsløpet viste ikke denne dumpen. Ingen påstand om helt krasjfri runtime. |
| R4 | Nautilus logget utilgjengelig Tracker-indexer. | Lokale mapper/filer rendret. Både system- og user-failed-unit-listene var tomme ved siste kontroll. Universell søke-/indekseringsaksept hevdes ikke. |
| R5 | Installert skrivebordsbakgrunn vist under aksepten var upstream DMS-artwork, ikke akseptert som WS-wallpaper-/persistensbevis. | Kosmetisk/egen tidligere port; skjermbildene viser faktisk tilstand. Merket Hyprlock-logo/bakgrunn er visuelt bekreftet. Ingen manuell etterreparasjon for å fremstille image-bytes som riktige. |

Disse funnene er åpne merknader på integrasjons-/dashboard-sporet, ikke «fikset» av installasjonsaksepten. Ingen bekreftet kildefeil ble rettet i dette oppdraget, og ingen ny regresjons-/review-/byggsyklus ble startet på en ubekreftet årsak.

Full pakkeoppgradering, konfigurasjonsbevaring/manuell gjenoppretting, femminutters idle-lås og tidligere bredere #30/#31-porter er **ikke** gjennomført for denne ISO-en. De er ikke lukket gjennom gjenbruk av eldre image-bevis. Ingen fysisk USB-/PC-/UEFI-/Secure Boot-/GPU-/Wi-Fi-/lyd-/suspendaksept. Denne ISO-en er intern, ikke offentlig distribusjon eller en generell stabilitets-/sikkerhetsgaranti.

## 9. Engineering Standards og publiseringskvalitet

Oppgaven følger [Engineering Standards fra PR #35 ved a78d887](https://github.com/tomli0/wilsof-os/blob/a78d88790754886750bb1a5f93dd33cb257cc47e/docs/ENGINEERING_STANDARDS.md), rapporteringsstandarden og 12-punktsmalen derfra. PR #35 og worktree-et er ikke endret eller merget.

Høyrisikogrenser er beholdt: faktisk identifisert ny virtuell disk, umiddelbar blankhets-/identitetskontroll, eksakt bekreftelse, skjult passord, original feilstatus, ingen fysisk blokkenhet, minste privilegium i installert økt og bevarte tidligere bevis. Native pakke, source-review, CI, faktisk ISO, GUI og fysisk klient er separate bevisnivåer.

Denne leveransens Git-diff er dokumentasjon, sanert JSON og gjennomgåtte GUI-bilder. Relative lenker, JSON, sensitive mønstre og diff kontrolleres før eksplisitt staging. Bare egne filer committes. Ingen ny uavhengig review er nødvendig for uendret produksjonskode; ingen slik review påstås for rapportteksten.

## 10. API-/modellforbruk der det kan dokumenteres

Eksisterende konfigurasjon er uendret: primær **gpt-6.1-sol / openai-codex**, automatisk fallback **z-ai/glm-5.3 / OpenRouter**, review **Claude Sonnet 4.6**. Konfigurasjonens SHA256 er sammenlignet før/etter. Ingen modellruting, kredittgrense, tjeneste eller påfylling er endret.

Read-only session-/model-usage-snapshot **23:51:35 UTC**, før rapport-/publiseringskall:

| Rolle | Faktisk registrert rute | Observerte kall / metadata |
| --- | --- | --- |
| Primærøkt | gpt-6.1-sol, openai-codex | **115** kall; billing_mode=subscription_included, cost_status=included, estimated_cost_usd=0. Aggregate actual_cost_usd mangler. |
| GUI-vision | gpt-6.1-sol, openai-codex | **17** kall; lagrede kostnadsfelt0, men separat cost_status mangler. Ikke en ny betalt reviewrute. |
| Tittel | gpt-6.1-sol, openai-codex | **1** kall, lagrede kostnadsfelt0. |
| Ny Claude/delegering/fallback i oppgaven | Ingen registrert i dette snapshot-et | **0** nye slike runder. Tidligere 0,303399 USD-Claude-review tilhører forrige oppdrag, ikke internal2-byggingen. |

Token-/cachefeltene er bevart separat i JSON uten dobbeltsummering. Tallene er et tidsstemplet snapshot, ikke hele sluttregningen eller en påstand om at en revisorgodkjent faktura er0 USD. Senere rapportering øker samtalens kall. Ingen provider-budsjettprobe eller ny betalt modellrunde ble startet for å produsere kostnadstall.

## 11. Prosesser, prosjektlås og scheduler

Den eksisterende prosjektlåsen ble tatt eksklusivt før beskyttet arbeid, med eier **PID155847**. Konkurrerende nonblocking-probe ga busy mens oppgaven holdt låsen. Låsen er holdt gjennom bygg, installasjon, begge VM-livsløp og dokumentasjonspublisering; QEMU arvet samme lock-FD slik at disksikkerheten ikke var avhengig av at en samtaletur fortsatte.

Byggprosessen og QEMU **PID177158 / PID181302** er faktisk avsluttet med exit0. Ingen ekstra QEMU-gjest eller parallell utviklingsagent er startet. Kontroller før rapportskriving fant ingen gjenværende QEMU, mkarchiso, pacman eller pacstrap. Bare oppgavens egen public-key-fetch-gpg-agent og target-spesifikke gpg-agent ble avsluttet; ikke fremmede agenter. Endelig låsfrigivelse og konkurrerende tilgjengelighetsprobe skjer først etter publisering og prosesskontroll og kvitteres i #16 og privat kontrollpunkt.

Wilsof-jobb **`8df95a6101e7`** er fortsatt **enabled=false/paused**; worker **paused=true, stop_requested=false**. Ingen scheduler/worker er startet eller resumert. Ingen fysisk disk/USB, Proxmox-endring, merge til main/arch-install eller offentlig release.

Siste offline disk-SHA256: `f28d75d3cfc9845424519922e1eba6ff73eff1a1f5aab8492d4326245b229b6e`. Installasjonsfirmware er bevart uendret; disk-only-firmware er bevart separat. Private installer-/runtime-arkiver er kontrollert mot SHA256 etter overføring. Testhemmeligheten ligger separat, privat, og følger ikke ISO-bunten.

## 12. Neste anbefalte milepæl

**Ingen ny oppgave startes.** Eier kan godkjenne en avgrenset **fysisk USB live-test av nøyaktig samme SHA256** på en dedikert test-PC, med eksisterende runbook, sikker målidentifikasjon og uten automatisk fysisk installasjon. R1–R5 må følge kandidaten og vurderes før bredere stabilitets-/releasepåstander; eventuelt videre runtime-feilsøk må være en egen avgrenset oppgave, ikke skjult viderearbeid her.

PR #27 beholdes draft/umerget og #34 beholdes åpen med den nye virtuelle akseptansen dokumentert. Permanente #16 og andre åpne porter lukkes ikke. Fysisk installasjon, større runtime-endringer og offentlig release krever separate beslutninger.

## Publiseringskvittering

Denne fullrapporten, strukturert evidens, ni sanerte faktiske skjermbilder og kontrollpunkt committes/pushes til integrasjonsgrenen. Eksakt rapport-URL ved publiseringscommit, remote-blob/read-back, head-CI og faktisk sluttstatus for låsen kvitteres etter push i #27/#34/#16 og terminalen. Ingen antatt push-/CI-/låsfrigivelsessuksess legges inn på forhånd, og ISO-kilden endres ikke til den senere dokumentasjonscommit-en.
