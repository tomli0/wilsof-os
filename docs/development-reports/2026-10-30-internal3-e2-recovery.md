# Wilsof OS — internal3 E2-gjenoppretting og ISO-aksept, 2026-10-30

Status: internal3 levert innenfor omfang — E2 rotårsaksrettet, én ferdig ISO, full UEFI-installasjon og virtuell funksjonsaksept; resterende begrensninger eksplisitt (TCG-emulering, R1/R2-runtime-notater, fysiske klientporter).
Utviklingsperiode UTC: 10:09–12:35. Rapporteringsperiode UTC: 12:35–13:05.
Kildegren: `integration/internal3-20261030`. Status-issue: [#16](https://github.com/tomli0/wilsof-os/issues/16). Leveranse-PR: draft [#41](https://github.com/tomli0/wilsof-os/pull/41).

## Bevisgrunnlag og avgrensning

- Tidligere rapportert: kontrollert stopp «CONTROLLED_STOP_BLOCKED_BEFORE_INTERNAL3_ISO» i privat kontrollpunkt og [forrige rapport](2026-10-30-internal3-integration.md): to bygg exit 1 (PID-grense, deretter E2 bind-mount-EBUSY), null ISO, F aldri startet.
- Historisk direkte verifisert: bevart fryst kilde `448e0190e786475f083abdce223b3b24dc2a85ef` (git archive byte-identisk med `frozen-source.tar`, alle 41 payload-oppføringer hashlike), profil/work/SquashFS (sha256 `6f5c4f92…dcf7`) og 16 ferdige run-once-markører fra resume-forsøket.
- Kontrollert på nytt: ingen aktive bygg-/QEMU-prosesser eller private mounts ved start; prosjektlås ledig; scheduler `enabled=false/paused`, worker `paused=true`; 5 tidligere ISO-er hashuendrede; 14 remote-refs uendrede; frisk OpenRouter-nøkkelmåling.
- Ikke utført / ikke autorisert: ingen fysisk disk/USB, Proxmox, merge til main, offentlig release, M3/M4, dashboard/Kanban, reaktivering av scheduler/worker, svekket signatur-/CheckSpace-/autentiseringskontroll, rekursiv cleanup av monterte kataloger, lazy/force-unmount, nye pakker eller ny uavhengig betalt review.
- Private bevis: QA-gruppen `internal3-20261030/recovery/` (launcher-, build-, installer-, live- og installed-VM-kvitteringer, sanert PTY-logg, JUnit, ISO-layout, immutable-audit, budsjettmålinger); syntetisk QA-legitimasjon og VM-disker holdes private, mode 600/700.

## 1. Fullførte milepæler

- **E2 rotårsak avklart og rettet (minste rettelse):** bygg-wrapperen `scripts/build-iso.sh` utelater nå `mkarchiso -r` og bevarer namespace-eid work/profile. Rotårsak: Archiso 91s `-r` fjerner `${work_dir}/${arch}/airootfs` rekursivt i starten av `_build_iso_image` (før xorriso); resume-grenen i det private oppsettet selv-binder airootfs for nested pacman CheckSpace og unmounter aldri innenfor navnerommet, så `rm` får `Device or resource busy` før ISO-opprettelse. Sekundært: run-once-markøren `base._make_work_dir` hopper over upstreams nullstilling av `-r`-flagget ved eksisterende work, så resume var aldri trygg med `-r`. Ingen installasjon i selve wrapperen endret; løsningen ligger i bygg-wrapperens cleanup-kontrakt, ikke i privat oppsett-isolasjon som ble bevart uendret.
- **E2 reprodusert disponibelt:** i et nytt privat mount/PID-navnerom ga `rmdir` på en kjent tom selv-bind `Device or resource busy`; deretter kjørte den faktisk installerte mkarchiso ISO-funksjonen med ekte xorriso uten cleanup: exit 0, sentinel bevart, ingen host-mount-lekkasje, ingen rekursiv sletting kjørt (`tests/integration/archiso_cleanup_lab.py`, resultat-JSON bevart).
- **Regresjonstest:** `tests/test_iso_cleanup_contract.py` — faktisk RED mot uendret wrapper (assertet fravær av `-r`), GREEN etter rettelse. Full suite **312 passed / 2 eksplisitte opt-in-skips**; ShellCheck (sh/bash-dialekter) og `git diff --check` bestått.
- **Én ferdig internal3-ISO:** mkarchiso-finalisering av bevart kilde/profil/SquashFS uten ny pakketransaksjon (bygg-attempt 3 totalt, men null nye pakkebygg; de to historiske kallene exit 1 bevart ulåst). Bygg-exit 0, xorriso fullførte, work beholdt som bevis.
- **Full F-port på ny disponibel virtuell disk:** faktisk interaktiv installer exit 0 (5/5 prompts, skjult passord aldri i klartekst), 25/25 målkontroller, kontrollert live-nedstenging med ren unmount, disk-only UEFI-boot uten ISO, vanlig greeter-passordinnlogging, fire renderte apper, fire profiler satt/verifisert, launcher+Esk-kontrakt, lås med PAM-avvist feil passord og — etter dokumentert pam_faillock-vindu — korrekt opplåsing.

## 2. Claude QA-funn og utbedringer

Ingen ny uavhengig Claude-/annen modellreview bestilt eller utført i denne økten; primæragentens egen gjennomgang er ikke uavhengig review. E2-funnet er egen systematisk feilsøking med reproduserbar disposibel lab, ikke modell-QA.

| ID | Alvorlighet | Konkret bevis | Bekreftet/avkreftet/ubekreftet | Utbedring eller åpen oppfølging |
| --- | --- | --- | --- | --- |
| E2 | Blokkering (bygg) | `rm: cannot remove '/export/work-internal3/x86_64/airootfs': Device or resource busy` i bevart resume-logg; self-bind i `arch-runner.sh`; `_build_iso_image`-kilde lest i installert Archiso 91; disponibel rmdir/xorriso-lab | Bekreftet | `a952e80…` utelater `-r`; cleanup-kontrakt dokumentert i runbook/iso.md; separat eksakt-sti-cleanup krever verifisert prosessavslutning og mount-sjekk |
| pam_faillock-auditvarsel | Lav | `pam_faillock(hyprlock:auth): Error sending audit message: Operation not permitted` i gjest under TCG | Ubekreftet (antatt navneroms-/emuleringsartefakt) | Registrert; ingen kodeendring; følges ved fysisk test |

## 3. Kodekvalitet og sikkerhetsstatus

- Endringen er fem filer: `scripts/build-iso.sh` (ett flagg + kommentar), regresjonstest, native lab (opt-in, aldri i CI), runbook- og iso.md-dokumentasjon av mount-livssykluskontrakten. Ingen produksjons-/installerkode endret.
- Tillitsgrenser uendret: CheckSpace, SigLevel Required, ERASE-bekreftelse, umiddelbar mål-reprobe, skjult passord-input, privat mount/PID-namespace med read-only kilde, ingen hjem/credentials/fysiske blokkenheter bundet inn. Ingen `-r`-erstatning med rekursiv sletting; senere cleanup krever verifisert prosessavslutning + mount-sjekk + separat autorisering.
- Tester: `python -m pytest -q` → 312 passed / 2 skips (16,6 s), JUnit null failures; `shellcheck` reelle dialekter bestått; `git diff --check` rent. Kommando/exitstatus/commit registrert i kvitteringer.
- Immutable ISO-audit 55/55: nøyaktig payload-oppsett (41 filer + SOURCE_COMMIT byte-identiske), hjelper-/plugin-bytes, root-owned executable-moduser, låst root, ingen live-/QA-/utviklerkonto, `machine-id` «uninitialized», ingen private filnavn, verifisert Hypridle-binær/pakke-pin, og ISO-embedded SquashFS byte-identisk med den bevarte (sha256 like).

## 4. Commits og CI-status

| Commit | Gren / endring | CI-kjøring og eksakt head | Faktisk resultat / nykontrolltid |
| --- | --- | --- | --- |
| `a952e8092114ecf05c508074d844d93836a1246c` | E2-fix + regresjon + lab + dokumentasjon | push [41039790179](https://github.com/tomli0/wilsof-os/actions/runs/41039790179), PR [41039797887](https://github.com/tomli0/wilsof-os/actions/runs/41039797887) | Begge completed/success på eksakt head; logger bekrefter 312 passed/2 skips; alle 5 filer byte-lest tilbake fra remote 10:18–10:19Z |
| [denne rapporten] | kun dokumentasjon/kontrollpunkt/QA-JSON på samme gren | kvitteres etter push | se Publiseringskvittering |

Draft #41 OPEN/umerget; base `integration/internal-iso-20261026` uendret. Workflowfiltre uendret (kandidatens push-gren + integrasjons-PR-base). Kilde-PR-heads #38/#39/#40 uendrede.

## 5. ISO-filnavn, størrelse, SHA256 og plassering

| Felt | Verdi og bevisstatus |
| --- | --- |
| Filnavn og faktisk kildecommit | `wilsof-internal-2026.10.30-internal3-x86_64.iso`; bygd fra fryst kilde `448e0190e786475f083abdce223b3b24dc2a85ef` (byte-verifisert mot `frozen-source.tar` og payload-manifest ved 10:15Z) |
| Størrelse i byte | 2548035584 |
| Full SHA256 | `b3cf9726f2d55a7a0398aadeb6327a839a5607a7dd7f5a10b9a862a5c1936dd1` (målt ved kopiering 10:31Z; manifest + SHA256SUMS vedlagt) |
| Plassering | privat artefaktrot `/home/tommy_ai/wilsof-assets/internal-test-20261030-internal3/` med `manifest.json` og `SHA256SUMS` |
| Aksept / tidligere artefakter | Alle fem tidligere ISO-er (inkl. internal2, 2546053120 byte, `dc4bfb39…`) hashuendrede; bevart del-SquashFS fra de historiske exit 1-kallene beholdt som feilbevis, ikke aksept |

Byggmetode: samme verifiserte prepare-/boot-profile-flyt, Archiso 91-1 i fersk isolert Arch-rot, privat mount/PID-namespace, `mkarchiso -v` (uten `-r`) på eksisterende verifiserte work/markører; ingen ny pakketransaksjon, ingen ombygging av ferdig ISO.

## 6. Resultat fra full installasjon

| Port | Bestått / feilet / ikke testet / ikke relevant | Eksakt bevis eller begrunnelse |
| --- | --- | --- |
| UEFI-oppstart fra ISO | Bestått | `test -d /sys/firmware/efi` i live-gjest; systemd-boot-oppsett i build-logg; UEFI-firmwarevarianter ferske |
| Live-skrivebord | Bestått (treg TCG-kaldstart notert) | wilsof-live-setup active/exited 0; rendret live-skrivebord med bar og wallpaper; DMS NRestarts=1 under kaldstart beholdt som observasjon |
| Diskvalg og sikkerhetskontroller | Bestått | ny 24GiB qcow2 uten backingfil, fersk firmware; lsblk/wipef/signaturfrihet verifisert; installers egne blankhets-/ERASE-/reprobe-gater uendret og utløst |
| Full installasjon, installer exit 0 | Bestått | PTY-driver mot faktisk `/usr/local/bin/wilsof-install`: 5/5 prompts, `Installation completed`, ingen klartekst-passord, ingen timeout; arkivert transkript privat |
| Installert målverifikasjon | Bestått | 25/25 kontroller (`verify-target.py`): låst root, vanlig greeter uten autologin, resolver/mtab, CheckSpace/SigLevel, hypridle-pin, profil-/plugin-/helper-bytes nøyaktige |
| Disk-only boot uten ISO | Bestått | query-block viser kun pflash+disk (ingen ISO); `/dev/vda2`-root; ingen live-mount |
| Vanlig passordinnlogging | Bestått | tuigreet brukernavn- og passordprompt observert; PAM-økt `wilsofqa` uid 1000 Wayland; ikke root/runuser |
| Installert skrivebord / apper | Bestått | rendret skrivebord med bar + godkjent wallpaper-posthook exit 0; fire faktisk renderte klienter (Nautilus, Ghostty, Firefox mot lokalt fixture, Text Editor) med geometri/tilstand registrert |
| Profiler / launcher / Esk | Bestått med avgrensning | fire profiler satt og verifisert via reell økt (`saved=applied` for development→everyday→study→clean; ingen feil); launcher åpnet visuelt med fremhevet rad og pikselverifisert radmarkering; Esk-kontrakt bestått (selector lukket, tilstand uendret). Piletast-Enter-valg i launcher var upålitelig under TCG-last (spotlight-fokus) og er verifisert via støttet hjelper i stedet — merket som emulatorbegrensning |
| Lås, feil passord, korrekt opplåsing | Bestått | hyprlock engasjert (hypridle-styrt); feil passord kontrollavvist av PAM (`authentication failure` + pam_faillock-utestengelse); korrekt opplåsing etter dokumentert utestengelsesvindu: `auth: authenticated for hyprlock` → `Unlocking session` → locker-exit, DMS aktiv, gjenopprettet skrivebordsramme 99 % endret fra låstflate (12:25:03Z) |
| Avslutning / opprydding | Bestått | begge gjester kontrollert avsluttet exit 0 (live 11:21Z, installed 12:26Z); supervisor-barn alle exit 0; offline qcow2-sjekk exit 0 (`Image end offset: 6074662912`); installert disk sha256 `7659e4b6…285b` og VARS `66c7f510…4d36` arkivert |

Lagring ved 12:26:51Z: 89392742400 byte = 83,253479004 GiB. Krav 26843545600 byte (25 GiB) oppfylt hele økten; differanse +62549166560 byte; ingen artefakter slettet.

## 7. Oppstart og passordinnlogging

Installert image: internal3-ISO over (kilde `448e019…`). Disk-only UEFI-boot uten ISO verifisert via QMP block-inventar. Vanlig greeterinnlogging: brukernavn `wilsofqa` tastet syntetisk, passordprompt observert før privat syntetisk passord ble levert via QEMU-input; `pam_unix(greetd:session): session opened for user wilsofqa(uid=1000)` i journal; Wayland-sesjon klasse `user`, aktiv. Root forblir låst; ingen autologin. Lås via hypridle-styrt hyprlock; feil passord kontrollavvist (`authentication failure` + pam_faillock); korrekt opplåsing etter dokumentert utestengelsesvindu. Syntetisk input er ikke fysisk tastaturbevis.

## 8. Gjenstående feil og begrensninger

- R1 (DMS-kaldstart-SIGKILL) og R2 (hyprland-dialog/libhyprtoolkit-coredump) observeres fortsatt: tre nye hyprland-dialog-coredumps under tung TCG-appstart i denne økten; ingen ny rotårsak hevdet. R3 (live gvfsd-fuse) ikke re-observert i de nye gjestene, men heller ikke «løst». R4 (Tracker-varsel) uendret. R5-wallpaper består installert (posthook exit 0, godkjent bilde aktivt); #37 forblir åpen.
- TCG-only-bevis: ingen ytelse, responstid, fysisk Super-ruting, flerskjerm, GPU/Wi-Fi/lyd/suspend/USB-transport eller Secure Boot. Piletast-Enter-valg i launcher upålitelig under emulering.
- pam_faillock-utestengelse + `audit message: Operation not permitted` i TCG registrert; ingen kodeendring.
- Fysisk USB-testklarhet: **CONDITIONAL GO** — ISO, installasjon, disk-only-login, profiler, apper, wallpaper og lås/opplåsing er virtuelt verifisert; eierens fysiske USB-boot-/spare-PC-sjekk kan gjennomføres etter runbook, med R1/R2-notat og med clear forventning om at emuleringsbevis ikke overføres til maskinvare.

## 9. Engineering Standards og dokumentasjon-PR

Risikobasert avgrensning fulgt (middels: bygg-wrapper/UI-flyt; ingen høyrisiko-installerendring). RED→GREEN-regresjon, faktisk CI på eksakt head, byte-lesning av alle endrede fjernfiler, modenhetsnivåer holdt atskilt (implementert/testet/integrert/ISO-verifisert; fysisk verifisert gjenværende). Rapportmal og rapporteringsstandard fulgt; denne rapporten + kontrollpunkt-snapshot + sanert QA-JSON committes på `integration/internal3-20261030` (publisert på gren, ikke merget). Draft #41 forblir åpen til eiergjennomgang; ingen issue lukket.

## 10. API-/modellforbruk der det kan dokumenteres

| Rolle / faktisk modell | Periode / omfang | Kall / tokenfelter / cache | Kostnad og bevisstatus |
| --- | --- | --- | --- |
| Primær GPT-6.1-sol / openai-codex (subscription_included) | 10:09Z frem til primærkvote | økt-snapshot ved 12:00Z: 144 API-kall, input 553852, output 61512, cache-read 32407616 | estimated 1,17082784 USD, actual_cost_usd mangler (ikke nullfaktura); subscription_included |
| Fallback GLM / OpenRouter (konfigurert rute, uendret) | resten av gjenopprettingsøkten (primærkvote brukt underveis) | delt nøkkelteller 48,328455501 → 49,451597213 USD (10:15Z→12:00Z) | observert delta 1,123141712 USD på delt nøkkel; ikke eksakt øktattribusjon eller faktura |
| Andre sesjoner | ingen | ingen andre sesjoner i state.db etter 10:09Z | ikke relevant |

Ingen betalt review bestilt; config.yaml sha256 uendret (`ab41ee8f…`); nøkkellimit 100 USD håndhevet av provider; ingen påfylling/retry-omgåelse. Senere rapporteringskall inngår ikke i de målte periodene.

## 11. Aktive prosesser og prosjektlåser

Ved rapportslutt (12:35Z): alle tre supervisor-barn (finalisering, live-gjest, installed-gjest) verifisert exit 0; offline qcow2-sjekk exit 0 på disponibel installert disk; gjenopprettingssupervisor (PID 505468) frigjorde prosjektlåsen etter publisering med bekreftet nonblocking-probe (se publiseringskvittering); scheduler `enabled=false/paused`, worker `paused=true/stop_requested=false`; eksisterende Hermes-gateway/dashboard er ikke prosjektarbeidere.

## 12. Neste anbefalte handling

Ingen ny utviklingsoppgave starter automatisk. Ved ny eierautorisjon: eierens fysiske USB-boot-/spare-PC-sjekk per [runbook](../internal-test-runbook.md) med CONDITIONAL GO-forutsetningene (R1/R2-notat, ingen ytelsesaksept), eller separat besluttet oppfølging av R2-coredumps. Eventuell cleanup av bevart build-work krever verifisert prosessavslutning, mount-sjekk og eksakt-sti-tilbud.

## Publiseringskvittering

Rapport, sanert QA-JSON og kontrollpunktsdokument er commitet/pushet på `integration/internal3-20261030` sammen med den eksisterende E2-fixen; eksakt publisert commit, CI-kvittering, #16/#41-sluttkommentarer og endelig lås-/prosessenhet er ført i privat kontrollpunkt og i terminalens sluttlenke. Ingen merge, release eller fysisk handling iverksettes.
