# Wilsof OS — accept-completion: Command Center-aksept, F1-låserettingsfiks, Terminal Idle og ReGreet-evaluering, 2026-10-31

Status: **LEVERT SOM DRAFT — IKKE FULL AKSEPT**. Command Center-akseptmatrisen er fullført med rendret QEMU-bevis; den kritiske F1-sårbarheten (modal beholder tastaturfokus over låst skjerm) er fikset og live-verifisert i gjest; Terminal Idle (3/5/10 min) er implementert og delvis live-verifisert; ReGreet er implementert som kandidat, men forblir ikke-default fordi innlevering til GTK-feltet ikke kunne verifiseres sikkert under TCG. Ingen ISO bygget; ingen merge/release.

Utviklingsperiode UTC: 2026-10-31 ~09:10–11:4x (gjenopptagelse av design-desktop-økten fra checkpoint `phase2-progress.json`). Status-issue: #16. Draft-PR: **#46** (`feat/accept-completion-20261031`, stablet på #45).

Kildegren: `feat/accept-completion-20261031` slutt-head `708ce796ca333855a0ecc3934ee31f89dde340d8` (3 commits over #45-head 6c740f0: `a42e462` F1-fiks, `9250842` Terminal Idle, `708ce79` ReGreet — amendet etter evalueringen). Basis PR #44/#45 uendrede; ingenting merget.

## 1. Gjenopptagelse og tilstandsverifikasjon

- QEMU-gjest fra design-økten var allerede avsluttet; ny disponibel child-COW-overlay (`accept-completion-20261031/vm/disk.qcow2`) opprettet over design-desktop-øktens overlay (kjede: source-qa.qcow2 → internal3-new-24g.qcow2 → internal4-completion vm-boot1 → design-desktop → denne). Originaldiskene aldri skrevet direkte; offline `qemu-img check` exit 0 før hver oppstart.
- Prosjektlås tatt med holdere (PID 749951, inode 833227) og holdt hele økten; scheduler `enabled=false/paused` og worker uendret.
- Bevaring verifisert ved øktstart: **47/47 SHA256 manifest uendret**; ISO `b3cf9726f2d55a7a0398aadeb3287a839a5607a7dd7f5a10b9a862a5c1936dd1` uendret.
- Kildegren `6c740f0` deployet i gjesten (sha256 `08c973b2…`, digest verifisert i gjest) via `install-user-config.sh`; personlige DMS-innstillinger bevart; NRestarts=0.
- Senere i økten: F1-fiks + M4 deployet fra `a42e462`/`f345745`-trær med digest-verifikasjon (samme installerprosedyre).

## 2. Command Center-akseptmatrise (fullført — rendret QEMU-bevis)

| # | Akseptpunkt | Resultat | Bevis |
|---|---|---|---|
| 1 | Musklikk-aktivering | **PASS** | Peker verifisert `hyprctl cursorpos` 639,288; klikk på Terminal-raden aktiverte nøyaktig den klikkede raden (ikke tastaturvalgt rad); Ghostty PID 1820 startet og ble activewindow (skjermbilder 13) |
| 2 | Tastatur- og musfokus | **PASS** | Super+Space åpner; tekst når søkefeltet; klikk på modal-krom stjeler ikke fokus (spørring fortsatt «terminal»); klikk i søkefeltet + skriving fungerer (14/15) |
| 3 | Fokusrestaurering ved lukking | **PASS** | Etter Esc: activewindow tilbake til `com.mitchellh.ghostty` (16) |
| 4 | Gjentatt åpne/lukke | **PASS m/ forbehold** | IPC-sykluser deterministiske; tastatursti 4/6 åpninger under TCG (2 syntetiske tastetap ført ærlig, ingen feil modal observert); Esc lukker 7/7; DMS NRestarts=0 gjennom hele økten |
| 5 | Power-meny og bekreftelse | **PASS** | CC Power-raden åpner `dms:power-menu` (layer-bevis + rendret skjermbilde 31/32 med hover på utloggingsknapp); kort hold → hint + ingen eksekvering (27); full hold (Enter >2s, tastaturrepetisjon driver TCG-eventløken) → **utlogging eksekvert faktisk**, greeter returnerte (41) |
| 6 | Søkeresultat-valgkonsistens | **PASS** | «fire» → valg 0 «browser»; pil ned → valg 1 «app:firefox»; Enter aktiverte nøyaktig valgt rad; Firefox prosess startet og mappet (46–51) |
| 7 | Ghostty horisontale/vertikale splits | **PASS** | `ctrl+shift+o` (right): 2 bash-barn + **divider-kolonne x=959 i #434346 over full høyde** (57); `ctrl+shift+e` (down): 3 bash-barn + **horisontal divider y=420** (58); innhold i begge halvdeler stabilt |
| 8 | Søkelatens (3 lag målt separat) | **MÅLT** | Hjelper: host 42–45 ms (median 43,5 ms mot 6000-oppføringsfixture; **150 ms-mål oppnådd på hjelperlaget på host**), gjest/TCG 1720–4575 ms; DMS-integrasjon (`usefulResultsMs`): 298–9642 ms TCG; ende-til-ende (inkl. rendring): 14–39 s TCG-øvre grense. **150 ms er IKKE oppnådd i QEMU/TCG** — målertall er TCG-dominerte og ført ærlig |

Ikke utført: ISO-bygg, merge, fysisk maskinvare, uavhengig review (egen gjennomgang kun).

## 3. F1 — kritisk funn og fiks (RED→GREEN)

**Funn:** En åpen Command Center-modal beholdt tastaturgrabben over en aktiv hyprlock; passordtastetrykk landet i søkefeltet, og hyprlock autentiserte ikke før modalen ble lukket med Esc (bevis: 09/60–63, statusquery inneholdt passordtekst). Utløst av IPC-åpning mens låst + potensielt ved låsing med modal åpen.

**Fiks (commit `a42e462`):** modal lukkes øyeblikkelig når logind rapporterer sesjonen låst (`SessionService.onSessionLocked` → `lockdown()`); `open()`/`toggle()`/`search()` nekter å åpne mens låst (egen IPC-markør `WILSOF_COMMAND_CENTER_LOCKED`); `wilsof-search` behandler markøren som håndtert uten Spotlight-fallback (samme grab-problem); `wilsof-lock` reflekterer låsen i logind (`loginctl lock-session`/`unlock-session` rundt hyprlock) slik at DMS observerer den.

**Live-verifisering i gjest:** låst sesjon → wrapper stille/rc 0 uten fallback-kall, modal forblir lukket; feil passord avvist; riktig passord låser opp; **query tom etter opplocking — null tastelekkasje**. Tre nye regresjonstester (RED før fiks, GREEN etter): markørkontrakt, logind-tilstand rundt hyprlock, QML-låsekontrakt.

## 4. M4 — Wilsof Terminal Idle (commit `9250842`)

Policy i `config/hypr/hypridle.conf`: **180 s → `wilsof-idle`** (Terminal Idle-flaten: samme PAM-Hyprlock med godkjent presentasjon — flat `#090F14`, sentrert `[ W S ]`, `SYSTEM IDLE_`, animasjoner av; `config/hypr/hyprlock-idle.conf`); **300 s → `wilsof-lock`** (sikker re-låsing; dedup no-op mens låst); **600 s → `hyprctl dispatch dpms off`** med `on-resume` dpms on. Ingen ny daemon; hypridle forblir eneste idle-autoritet og hyprlock eneste låseflate (iht. screensaver-beslutningsdokumentet: ingen ulåst fullskjerm-idleflate).

**Gjesteverifisering:**
- Manuell `wilsof-idle`: engasjerte, **rendret eksakt per spesifikasjon** (#090F14 = 1 012 368 px ~99 % av skjermen; WS-mark 8 832 px; caption til stede; skjermbilde 68), feil passord avvist, opplocking OK (69/70).
- **Automatisk 180 s-tier verifisert live**: etter 3 min uten inndata engasjerte hypridle → `hyprlock -c /home/designqa/.config/hypr/hyprlock-idle.conf` observert som prosessargument; tastatur eiet av låsen (vellykket PAM-opplåsing). Rendret skjermbilde av den automatiske engasjeringen mangler (TCG-rammestall) — rendret bevis kommer fra den manuelle syklusen med samme wrapper/presentasjon.
- Probe-eksperiment: fersk hypridle + 20 s-lytter fyrte korrekt (marker-fil) — idle-mekanismen bekreftet uavhengig av konfigurasjon.
- **Suspend/resume: IKKE verifisert** — `systemctl suspend` returnerte rc 0, men gjesten kilte fast i TCG-resume (QGA utilgjengelig >12 min, skjerm svart); gjesten måtte kaldstartes på den disponible overlayen. before_sleep-låsingen (samme kommando som verifisert Super+L) kunne ikke observeres post-resume. Ført som TCG-blokkering; fysisk suspend/resume forblir PENDING.
- 600 s dpms-tier: konfigurasjonsverifisert (samme lyttermekanisme som 180 s-tieren som er live-verifisert); tidsgrensen ikke ventet ut i gjest (budsjett), kommandoen er standard hyprctl-dpms.
- Idle-inhibitor-test ikke utført i gjest (budsjett); forblir åpent punkt.

## 5. M3 — grafisk Wilsof login / ReGreet (commit `708ce79`, amendet)

**Implementert i kilde:** `greetd-regreet` + `cage` provisjonert i `install-arch-test-vm.sh`; godkjent bakgrunn (`Mørk geometrisk bakgrunn med isblått WS-monogram.png`) installeres som `/etc/greetd/wilsof-greeter-bg.png`; `config/greetd/regreet.toml` med mørk GTK og ingen autologin; greetd beholder PAM.

**Evaluering i disponibel gjest (greetd-regreet 0.5.0-1, cage 0.3.1-1):**
- Greeter rendret (bakgrunn + GTK-boks, skjermbilder 77–80) og PAM-innleveringer nådde greetd.
- **Feilautentisering:** to AUTH_ERR-forsøk holdt brukeren korrekt ved greeteren.
- **Blokkeringer (avgjørende):** greeteren krasjet én gang under TCG og ble respawnet av greetd (11:05:45); tastetrykk og klikk nådde ikke GTK-entrien pålitelig (skrift endret 0 piksler; innleveringene brukte et uforklart forhåndsfylt brukernavn «internal4qa») — full login kunne ikke verifiseres sikkert.
- **Beslutning iht. oppdragets sikkerhetsregel:** tuigreet forblir default (både i gjest og kilde); ReGreet er dokumentert én-linjes opt-in. Konfigurasjonen i gjesten ble tilbakeført til systemets originale `tuigreet --time --cmd /usr/local/bin/wilsof-session` (merket: det installerte systemet bruker `wilsof-session`-wrapperen, ikke rå `Hyprland` — repoets VM-script beholder `--cmd Hyprland` som opprinnelig).
- **Fallback re-verifisert ende-til-ende:** reboot → tuigreet → designqa-login → Hyprland-sesjon (skjermbilder 88–91 + PAM-journal).

## 6. Commits og CI

| Commit | Innhold |
|---|---|
| `a42e462` | fix(command-center): lukk og nevt modal under låst sesjon (F1) — 5 filer, 3 nye tester |
| `9250842` | feat(idle): Terminal Idle 3/5/10-minutterspolicy — 6 filer, 5 nye tester + oppdatert legacy-kontrakt |
| `708ce79` | feat(login): provisjon ReGreet som grafisk kandidat; tuigreet default — 3 filer, 2 nye tester |

Lokalt på eksakt slutt-head: **354 passed / 2 opt-in skips** (baseline 345/2 på 6c740f0); ShellCheck (sh) rene; TOML/JSON-syntaks validert. CI-lesback på PR #46 føres i publiseringkvitteringen under.

## 7. ISO-filnavn, størrelse, SHA256 og plassering

**Ikke bygget. Null byggforsøk.** Uendret leveranse: `wilsof-internal-2026.10.30-internal3-x86_64.iso`, 2 548 035 584 byte, SHA256 `b3cf9726f2d55a7a0398aadeb3287a839a5607a7dd7f5a10b9a862a5c1936dd1`, privat rot `~/wilsof-assets/internal-test-20261030-internal3/` — reverifisert uendret ved øktstart (se punkt 1) og i avslutningskontrollen.

## 8. QEMU-gjester denne økten

- Gjest 1 (PID 750811/750821): cold UEFI-boot, designqa-login, full akseptmatrise T1–T8, F1-fix-deploy + live-verifisering, M4-deploy + manuell/automatisk idle-verifisering. Avsluttet via `-no-reboot`-exit etter `system_reset` (gjenoppretting fra suspend-kile).
- Gjest 2 (PID 761667): cold boot etter suspend-kilen; ReGreet-evaluering (T5-avhengig reboot inngikk her).
- Gjest 3 (PID 762933): reboot til tuigreet-fallback + pålogging-verifisering.
- Alle tre kjørte på samme disponible overlay; originaldisker/firmware aldri skrevet; nye serial-/socketstier per oppstart (serial.log, serial2.log, serial3.log) slik at tidligere bevis ikke overskrives. Skjermbilder 01–91 + status-JSON lagret privat.

## 9. Gjenstående feil, begrensninger og uferdige punkter

- **R1** (DMS SIGKILL-årsak ukjent) og **R2** (hyprtoolkit#144): uendrede, åpne.
- **Suspend/resume under TCG:** gjesten kilte fast i resume (gjest 1); krever ny TCG-økt eller fysisk verifisering. before_sleep-låsing ikke observerbar post-resume.
- **ReGreet:** input-levering til GTK-entrien under TCG ikke verifiserbar (greeter-krasj + tastetrykk nådde ikke feltet); opt-in frem til verifisert. Fysisk verifisering av greeter gjenstår.
- **600 s dpms-tier og inhibitor-test:** konfigurasjonsverifisert, ikke tidsubventet i gjest (budsjett).
- TCG-begrensninger gjelder alle GUI-bevis: eventløke krever inndatadrevne rammer (fades/hold-timere), hyprctl-IPC-timeouter, 2/6 syntetiske Super+Space-tap, trege kaldstarter. Fysisk Wi-Fi/lyd/mikrofon/BT/flerskjerm/tastatur: **PENDING** (eierens fysiske klient).
- M5 (Appearance/snarvei-editor) påbegyntes ikke denne økten (fasesekvens fulgte oppdraget; budsjett bundet til aksept + F1 + M3/M4).

## 10. Engineering standard og dokumentasjon

Risikobasert minsteendring; RED→GREEN for alle kodeendringer (6 nye tester + 1 oppdatert legacy-kontrakt, alle RED før implementering); eksplisitt distribusjon uten glob (idle-filer lagt til installerens eksplisitte liste); personlige settings/seed-once-filer uendret; beskyttede stier uendret. Uavhengig review: **IKKE UTFØRT** (egen gjennomgang kun, ført ærlig).

## 11. API-/modellforbruk

Hovedagent z-ai/glm-5.3 (openrouter), hele økten; se session metadata. Ingen betalt review, ingen delegerte barn, ingen nøkkelpåfylling. OpenRouter-nøkkelbudsjett ved øktstart: $48,31 resterende (månedlig, resetser 2026-11-01).

## 12. Aktive prosesser og prosjektlås

Ved rapportering: QEMU-gjest 3 (PID 762933) **aktiv**; prosjektlås **holdt** av holder PID 749951 (inode 833227). Begge planlagt kontrollert avsluttet/frigitt i avslutningssekvensen like etter at denne rapporten er pushet og #16-kvittering er ført — endelig tilstand føres i publiseringkvitteringen.

## 13. Neste anbefalte handling

1. CI på PR #46 grønn + eierreview av F1-fiksen (sikkerhetsrelevant).
2. Fysisk klient: verifiser Terminal Idle-tierene (3/5/10), Super+Space/L på fysisk tastatur, suspend/resume og greeter på reell maskinvare.
3. ReGreet-input-utforskning på ny TCG-gjest eller fysisk klient før eventuell default-bytte.
4. Deretter M5 (Appearance/snarveier, gjenbruk av DMS-flater).

## Publiseringskvittering

Etter push/read-back føres her: PR #46-URL, CI-lesback, #16-kommentar-ID, målt ledig plass, og endelig lås-/prosesstilstand.
