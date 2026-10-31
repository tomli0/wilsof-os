# Wilsof OS — internal4-completion: stabilisering, defektutbedring og portvurdering, 2026-10-31

Status: **NOT READY — BLOCKERS REMAIN**. Alle i kilde håndterbare stabiliseringsfeil er utbedret og testet; fysiske porter og uavhengig gjennomgang gjenstår. Ingen internal4-ISO er bygget, og ingen bygging er autorisert.

Utviklingsperiode UTC: 2026-10-30 23:41 – 2026-10-31 00:45. Kildegren: `fix/internal4-completion`, stabelt på uendret `stabilization/internal4-20261030` @ `418a4ff8f5e50d79132aeb6a23d8064e5889c162`. Draft-PR: [#43](https://github.com/tomli0/wilsof-os/pull/43); PR #42 er uendret og OPEN/DRAFT.

## Bevisgrunnlag og avgrensning

- Baseline verifisert mot repo og maskin før endring: ren internal4-gren, 326 passed / 2 eksplisitte opt-in-skips, begge eksakte hoder CI success, `checkpoint.json`-tilstand `CLOSED_SOURCE_DRAFT_NO_INTERNAL4_ISO` med frigitt lås, scheduler `enabled=false/paused`, worker `paused=true`, 15 remote-refs uendrede, seks ISO-hasher kontrollert mot rapporterte verdier.
- Prosjektlås `~/.hermes/cron/wilsof-github-worker/lock/run.lock` er tatt og holdt av hele økten (flock eier PID 703852, inode 833227), arvet av begge QEMU-gjestene; kontrollfilenes hash verifisert uendret før/etter.
- Bevarte private røtter leses, aldri endret: internal3-recovery, internal4-20261030 (kilde/basis), QA-venv gjenbrukt tilsvarende requirements-dev.
- Ikke utført / ikke autorisert: ingen ISO-bygg, ingen USB-skriving, ingen fysisk disk/Proxmox-endring, ingen merge/release, ingen reaktivering av scheduler/worker, ingen betalt modell eller delegert reviewer, ingen leveransegren/main-endring, ingen driverinstallasjon på vert.

## 1. Fullførte milepæler

- **Baseline-gjenproduksjon**: full suite på uendret `418a4ff…`: 326 passed / 2 skips, JUnit `baseline.xml` null feil.
- **R2 direkte reprodusert og klassifisert som upstream-defekt**: to nye `hyprland-dialog` SIGSEGV i disponibel gjest (00:02:49, 00:10:22), stack `CWaylandBuffer → resizeSwapchain → configure`, identisk med dokumentert upstream [hyprtoolkit#144](https://github.com/hyprwm/hyprtoolkit/issues/144): når GBM/kms_swrast-allokering feiler returnerer `swapchain->next()` null som derefereres. Eksakt versjoner: hyprland-dialog 0.2.2-4, hyprtoolkit 0.6.0-1, aquamarine 0.15.1, mesa 26.2.6 under TCG virtio uten 3D. Upstream-fix [PR#130](https://github.com/hyprwm/hyprtoolkit/pull/130) er lukket automatisk uten merge (upstreams vouching-policy), dvs. ingen tilgjengelig oppstrøm-korreksjon. Ingen vendorpatch; coredump/journal oppbevart privat; ingen krasj skjult.
- **Hyprland 0.57 snarveier rettet**: Super+F (fullscreen), Super+Shift+pil (flytt) og Super+Ctrl+pil (resize) brukte fjernet `hyprctl dispatch …`-tekst som 0.57s Lua-IPC avviser (`expected a dispatcher (e.g. hl.dsp.window.close())`). Root cause bekreftet live: Super+F endret ingenting (`fullscreen: 0`), mens `hl.dsp.window.fullscreen()` fungerte (`fullscreen: 2`). Bindings endret til støttede `hl.dsp.window.fullscreen()`, `.move({direction=…})`, `.resize({x,y,relative=true})`; tast og layout uendret. RED→GREEN kontraktstest pluss real runtime-verifikasjon av fullscreen, floating og resize på faktisk klient.
- **BlueZ-leddet lukket i felles manifest**: `runtime/desktop-packages.txt` inneholdt bare `bluez-libs`; DMS snakker `org.bluez` over D-Bus som krever `bluez`-daemonen. Offisielt signert Arch-ekstra `bluez 5.87-2` lagt til i det delte live/installed-manifestet; `runtime/provision-target` enable `bluetooth.service`; `scripts/prepare-iso.py` gjenskaper BlueZ' oppstrøms enable-kontrakt (D-Bus-alias + bluetooth.target.wants). Ingen radio-påslåing, ingen tredjepartsdriver. Signert pakke verifisert i disponibel gjest (pacman -Qkk: 0 altered; alias opprettet; enhet korrekt inaktiv uten `/sys/class/bluetooth`).
- **QA-harness-feil rettet**: første native wallpaper-lifecycle-kjøring feilet 6+1 under tung TCG-skjermstlast (mock-DMS' 10s TimeoutStartSec); ny kjøring etter vanlig utlogging og uten skjerm/apper: **7/7 OK uendret test**. Separat påvist og rettet: tellerfiler ble skrevet in-place slik at `count()` kunne lese det tomme truncate/write-mellomrom (ValueError); begge syntetiske fixturer publiserer nå atomisk via sibling-rename. To deterministiske RED/GREEN-tester eksekverer genererte fixturer og forbyr in-place-skriving. Ingen timeout/assertion svekket; TCG-tidsouten er bevart som egen dokumentert observasjon.
- **CI-omfang**: `validate.yml` kjører på push-grenen `fix/internal4-completion` og PR-base `stabilization/internal4-20261030`; ingen eksisterende filter fjernet, ingen rettigheter endret.

## 2. Funn og utbedringer (egen gjennomgang — ikke uavhengig review)

Ingen uavhengig reviewer var tilgjengelig innenfor øktens grenser (ingen betalt review, ingen delegert kontekst, ingen duplisert agent). Egen gjennomgang gjennomfører hele kjeden; den er **ikke** en uavhengig gjennomgang, og det påstås ikke noe annet.

| ID | Alvorlighet | Bevis | Utbedring |
| --- | --- | --- | --- |
| Lua-dispatch | Høy (brukersnarvei død) | Live Super+F uten effekt; 0.57-IPC-feilmelding; test_hypr_config RED | Native dispatchers + kontraktstest; GREEN |
| BlueZ-manifest | Middels (funksjonstilstand feil) | `pacman -Q bluez` feilet; kun bluez-libs; DMS Bluetooth-detail krever org.bluez | Offisiell pakke i manifest + enable-kontrakt; testGREEN |
| Lifecycle-teller-race | Middels (QA-bevis kan feile) | `ValueError: invalid literal` i native kjøring; in-place write_text | Atomisk sibling-rename; 2 tester GREEN; native 7/7 OK |
| R1 | Høy | Se punkt 8 | Ingen; ikke løst, ikke feilaktig lukket |
| R2 | Høy | Direkte reprodusert; upstream #144 åpen, #130 lukket u-merged | Dokumentert; ingen vendorpatch |
| Tuigreet «F2 Change command»-visning | Lav | CMD-linje viser standard oppstrømsverdi etter valgt sesjon | Ingen endring; faktisk startet kommando verifisert fra `/etc/greetd/config.toml` og ps (`start-hyprland`) |

## 3. Kodekvalitet og sikkerhet

Endret filer (11): `config/hypr/wilsof.lua`, `runtime/desktop-packages.txt`, `runtime/provision-target`, `scripts/prepare-iso.py`, `tests/integration/wallpaper_lifecycle.py`, `tests/test_bluetooth_stack.py`, `tests/test_chroot_contract.py`, `tests/test_hypr_config.py`, `tests/test_lifecycle_fixture.py`, `tests/test_lua_dispatch_contract.py`, `.github/workflows/validate.yml`. Ingen berøring av ERASE-gate, blankhetskontroll, signaturnivå, autentisering, disk-validering eller godkjent design (UEFI-meny/splash/terminal/DMS-topbar/kontrollsenter/wallpaperassets/tiling uendret).

Sjekker kjørt på slutthead: full pytest 330 passed / 2 skips (17,6 s); opt-in native chroot-suite 2 passed (rootless Docker, eksisterende image-id, `--pull=never`, nettverk `none`, read-only root, ingen enheter); opt-in native wallpaper-lifecycle 7/7 OK i to separate kjøringer; ShellCheck begge dialekter; `git diff --check`; AST-parse av alle Python-filer inkl. bin/-skript; JSON-validering av alle repo-JSON; JSON-schemaplan-validering uendret.

## 4. Commits og CI

| Commit | Innhold | CI |
| --- | --- | --- |
| `9608f02…` | fix(hardware): bluez-pakke + enable-kontrakt + tester | push-run 41148790079 (f434263 base) success |
| `ed4ef22…` | fix(hyprland): native Lua-vindusdispatc | push-run 41149201175 success |
| `f434263…` | ci: valider isolert fullføringsgren | push 41148790079 + PR 41148790079-løp success |
| `d3ae6fc…` | test(qa): atomiske lifecycle-tellere | push 41150263025 + PR 41150268269 success |
| [denne rapporten + QA-JSON] | dokumentasjon på samme gren | kvitteres i Publiseringskvittering |

PR #43 er OPEN/DRAFT mot base `stabilization/internal4-20261030`; alle fire commits pushet; siste eksakte hoder begge grønne (push + PR). Rapport-head push og readback inngår i sluttkontrollpunktet.

## 5. ISO-filnavn, størrelse, SHA256 og plassering

**Internal4: ikke bygget. Null byggforsøk i denne økten.** Siste leveranse er fortsatt `wilsof-internal-2026.10.30-internal3-x86_64.iso`, 2548035584 byte, SHA256 `b3cf9726f2d55a7a0398aadeb327a839a5607a7dd7f5a10b9a862a5c1936dd1`, privat rot `internal-test-20261030-internal3/`. Alle seks ISO-hasher og alle 44 bevarte QA-filer (inkl. opprinnelige internal3-disker, firmware, private kontrollpunkter) er SHA256-fotografert før arbeid og verifisert uendret etter (se Publiseringskvittering). Denne økten er ren kildestabilisering; ingen av funnene er ISO-verifisert ennå.

## 6. Resultat fra full installasjon og QEMU-gjester

Én disponibel child-COW-overlay (`qemu-img create -b` mot bevart `source-qa.qcow2`, `qemu-img check` exit 0 før og etter), aldri originaldisken skrevet direkte, aldri ny installasjon, aldri parallelle tunge gjester. To sekvensielle QEMU-livstider på samme overlay, totalt tre ordinære tuigreet-innlogginger:

| Port | Resultat | Bevis |
| --- | --- | --- |
| UEFI disk-only boot (uten ISO), kald omstart | Bestått ×2 | frisk VARS-kopi, QMP-block-oversikt, `/dev/vda2` ext4-root begge ganger |
| Vanlig greeter-passordinnlogging | Bestått ×3 | PAM `session opened for user internal4qa(uid=1001)`; passordprompt visuelt verifisert før privat syntetisk input; root aldri brukt som autentiseringsbevis |
| Session wrapper | Bestått | `start-hyprland` → `Hyprland --watchdog-fd 4` alle tre; journalføring via systemd-cat; ingen oppstarts-advarsel/konsollbanner i renderingsvindu |
| DMS-kaldstart | Bestått | `ActiveState=active`, `NRestarts=0` ved alle målinger; DMS-READY i journal; ingen automatisk omstart observert |
| Skrivebord/DMS-flater | Bestått med TCG-notat | spotlight rendret (app-liste), profilvelger rendret (fire rader), kontrollsenter rendret (sidepanel + fliser), Power-meny rendret (fem valg + Hold to confirm 500 ms) — separate skjermbilder |
| Profilverk valg | Bestått | tastatur: CLEAN→(ned)→Enter→STUDY; STUDY→(ned)→Enter→STUDY-rebinding på logginn 2; mus: CLEAN-klikk; Escape bevarte lagret profil uten aktivering; `saved=applied` verifisert via faktisk helper-JSON etter hver aksjon |
| Vindussnarveier | Bestått | Super+1..9 (aktivworkspace id 1-9), Super+Shift+1..9 (flyttet klient til riktig workspace), fullscreen toggle, floating toggle, resize endret størrelse |
| Lås/opplåsing | Bestått | Super+L → faktisk `hyprlock` PID; normal opplåsingsflate rendret; korrekt passord → gjenopprettet skrivebord; avvist feil passord dokumentert tidligere i internal3/E2 |
| Utlogging/innlogging-syklus | Bestått ×2 | `hl.dsp.exit()` → greetd aktiv igjen, user-manager beholdt, ny PAM-innlogging OK |
| Vedvarenhet over omstart | Bestått | fil hash-identisk før/etter kald omstart; bluez-pakke og session-wrapper vedvarte; linger korrekt av |
| Avslutning | Bestått | begge gjester `powerdown` → QEMU exit 0, offline `qemu-img check` exit 0 begge, prosjektildisken/firmware hashuendret |

TCG-begrensning gjelder alt GUI-bevis: trege kaldrstarter (DMS `activating` i minutter), hyprctl-IPC kan time ut under skjermstlast, og syntetisk tastatur er ikke fysisk tastaturbevis. Super+Space forutsetter fylt spotlight; tidlig skjermbilde kan vise foregående flate.

## 7. Oppstart og passordinnlogging

Se punkt 6; ingen ny installasjon eller autologin-gren er berørt. `wilsof-session --diagnostics`-modus og `wilsof.diagnostics=1`-kernelparameter bevart uendret; normal ruting via `systemd-cat` beholdt.

## 8. Defektregister — R1–R5 og øvrig

| Defekt | Root cause | Fix | Tester | Status |
| --- | --- | --- | --- | --- |
| R1 DMS SIGKILL/exit137 ved kaldstart | **Ikke fastslått.** Tre kaldrstarter nå: NRestarts=0, ingen OOM/sigkill/killer-linjer i journal (`systemd-oomd` inaktiv), MemoryPeak 520–727 MB mot 6 GB gjesteminne, `MemoryMax=infinity`, OOMPolicy=stop. dux-go `supervise.go` håndterer kun mottatte signaler med `exitUI()`-LOS-OK-sti; historisk 137 kan ikke uten sitt eget kernel/coredump-bevis tilskrives OOM, systemd-tidsout eller agent-kill. | Ingen kodeendring; ingen spekulativ timeout/limit | 3 kaldstart-observasjoner + full journalarkiv privat | **OPEN — ikke reprodusert, årsak ukjent** |
| R2 hyprland-dialog/libhyprtoolkit SIGSEGV | Oppstrøms null-CWaylandBuffer når GBM-allokering feiler (hyprtoolkit#144); #130 lukket uten merge | Ingen vendorpatch; dokumentert + krasjbevis bevart | Direkte reprodusjon ×2, coredump-liste | **OPEN — upstream, ingen trygg korreksjon** |
| Wi-Fi | Ikke fastslått fysisk; NM/wpa_supplicant/linux-firmware er installert i både live og target | Ingen fysisk kodeendring | Manifest-/tjenesteverifisering i gjest | **PENDING fysisk diagnose** |
| Lyd | Ikke fastslått fysisk; SOF er nå eksplisitt i installert manifest | sof-firmware-paritet (internal4-arbeid) beholdt | Manifesttest | **PENDING fysisk diagnose** |
| Bluetooth | internal3 ISO manglet `bluez`-daemon; «No adapters» kunne ikke klassifisere fysisk adapter | `bluez 5.87-2` i felles manifest + enable-kontrakt; ingen radio-påslåing | Manifest/materialisering/provisioning-testGREEN; signert pakke + alias verifisert i gjest | **PENDING fysisk adapter/pairing** |
| Profilvelger-tastatur | Tidligere mislykket test kunne ikke bekrefte Down/Enter-studium; resultatene nå: gjentatt vellykket Down→Enter-aktivering, Escape-bevaring, mus-valg, highlight-verifisert i renderingsvindu | Ingen kodeendring (selector uendret); bevisprosedyren var feilen | 3 gjester med full lagret/aktivert-verifisering | **PASS i QEMU; fysisk tastatur fortsatt ikke verifisert** |
| Session-/provisioneringskjede | Selv-review fant ingen ny blocker; eksisterende guards (symlink-nekt, mount-krav, resolver-postcondition, exact-versjon, blankhet, ERASE, skjult passord) er intakte og testet | Ingen | 330/2 + native 2/2 + 7/7 | **Uavhengig review mangler — dokumentert begrensning** |
| R3 live gvfsd-fuse | Ikke re-observert | — | — | **OPEN, uendret** |
| R4 Tracker-varsel | Observert igjen i nautilus (ufølsom runtime-merknad) | Ingen | — | **OPEN, uendret** |
| R5 wallpaper-reaktivering | Drop-in + post-hook uendret; native lifecycle 7/7 OK etter atomic-count-fix | Harness-fix (teller-race) | 7/7 native ×2 | **PASS (harness); ISO-aksept gjenstår** |

## 9. Engineering-standard og dokumentasjons-PR

Risikobasert minsteendring, RED→GREEN for alle tre kodefiksene, atskilte modenhetsnivåer (implementert/testet i QEMU/integrert i manifest-kjede; **ikke ISO-verifisert, ikke fysisk verifisert**). #43 er OPEN/DRAFT; #42, #41, #38/#39/#40 og alle issues forblir åpne; ingenting lukket eller merget. `.github`-endringen utvider kun eksisterende validering.

## 10. Modelforbruk

Primærrute hele økten: `gpt-6.1-sol`/openai-codex, `subscription_included`, estimated 0 USD, `actual_cost_usd` ikke tilgjengelig (ikke en målt nullfaktura). Ingen OpenRouter-flyt, betalt review, delegert kontekst eller nøkkelpåfylling er bestilt eller utført; `config.yaml` hash verifisert uendret mot tidligere godkjent `ab41ee8f…`. Prosentbruken avbildes av øktens metadata-snapshot i privat kontrollpunkt.

## 11. Prosesser, lås og ressurser

Én hovedagent, ingen worker/scheduler aktivert, ingen parallelle tunge gjester (maks én live om gangen). Prosjektlås holdt kontinuerlig (PID 703852), arvet til begge QEMU-barn, frigis etter verifisert publisering med nonblocking-probe. Begge gjester exit 0; begge offline qcow2-sjekker exit 0; ingen mount-lekkasje; QA-linger korrekt avslått. Ledig lagring målt ved avslutning i Publiseringskvittering; ingen bevarte filer slettet eller overskrevet.

## 12. Neste anbefalte handling

**Ett manuelt steg: kjør den read-only fysiske internal3-diagnosen etter `docs/qa/2026-10-31-internal4-completion-physical.md`** (ett steg per kommando, eksakt SHA256-gated skripthenting, gjennomgå JSON før deling). Deretter kan eier vurdere: fysisk Wi-Fi/lyd/BT-resultat, ny fysisk tastaturaksept av profilvelgeren, og en separat uavhengig gjennomgang av session/provisioneringsgrensen — før eventuell særskilt autorisering av internal4-ISO-bygg. Ingenting starter automatisk.

## Releaseporter (vurdering)

| Port | Krav | Vurdering |
| --- | --- | --- |
| A Koderettighet | Tester grønne, CI grønn, ingen regresjon, dokumentert kildetilstand | **PASS** (330/2 lokalt; begge eksakte heads grønne; 4 commits dokumentert) |
| B Sesjonsstabilitet | Pålitelig innlogging/skrivebord; R1/R2 undersøkt; ingen ubehandlet blokkerende sesjonskrasj | **PASS med merknad** — innlogging×3, kaldstart×3 stabile; R1/R2 undersøkt og dokumentert, begge forblir åpne, ingen ny sesjonsblokker i Wilsof-koden |
| C Maskinvareberedskap | Firmware/manifest verifisert; diagnostikk validert; **fysiske resultater dokumentert** | **PENDING** — fysisk Wi-Fi/lyd/BT mangler; prosedyre levert |
| D Installasjon/provisionering | Installer validert; uavhengig gjennomgang **utført eller fravær dokumentert** | **PENDING** — uavhengig gjennomgang utført NEI; fravær dokumentert her; ny installasjon ikke kjørt i denne økten |
| E Artefakt-autorisasjon | Alle porter grønne + eksplisitt eierautorisasjon | **BLOCKED** |

## Konklusjon

**NOT READY — BLOCKERS REMAIN.** Gate C og D er PENDING, derfor er ingen ISO-bygging autorisert, og ingen ble kalt klar. Alt som trygt kunne utbedres i kilde er utbedret, testet og publisert som draft; de gjenværende blockerne krever fysisk maskinvare og en uavhengig reviewør.

## Publiseringskvittering

Fylles etter push/readback i privat kontrollpunkt og #16: slutthead, rapportlenke, PR/CI-kvittering, målt ledig plass og låsfrigivelse.