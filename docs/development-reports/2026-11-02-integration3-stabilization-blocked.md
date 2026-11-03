# Integration3 — implementerte rettelser, avvist AS-02-kandidat og sikker stopp

Dato: 2026-11-02 UTC. **BLOCKED / ikke deployer / ingen ny ISO.**

## 1. Milepæler og verifisert utgangspunkt

Arbeidsgren: `integration/integration3-20261102`, isolert worktree fra PR #47 ved `0abf4a51af2338f14c691c2d325d6abfa2c8a410`. GitHub bekreftet #47, #48 og #49 som åpne draft-PR-er, uten merge. #48: `26cf38457efb170d587bd6e1f0b6f353c92fab5c`; #49: `a28d4678bbbaa091337fdab2b331a1b9e56b7e4d`. Review 3/4/5 og Phase 1/1B ble lest; Phase 1B ved `f55162ad60fe4748375b684785a930d87d283a81` var en betinget arkitekturanbefaling, ikke native akseptanse.

PR #48s implementeringscommit ble cherry-picket til `c7b2618`. AS-01/AS-03-implementeringen fra `e8d7d10` ble vurdert separat og cherry-picket til `a14c087`: eksplisitt idle-payload, privat session/compositor-identitet, atomisk flock, beholdt inode og descriptor-arv til locker. Dette var ikke merge av hele #49, og løfter ikke AS-02-blokkeringen. Native descriptor-retensjon etter supervisor-død og flere samtidige reelle brukerøkter er fortsatt uverifisert.

## 2. QA, funn og gjennomført remediation

Implementert med egne observerte RED→GREEN-regresjoner:

- DI-01 (`a1a4e66`): manglende Wilsof-pluginoppføringer migreres uavhengig. Eksplisitt `enabled=false` og andre pluginverdier beholdes. Oppgraderingsfixture: først 2 feil/1 pass, deretter 3 pass. En eldre fullsuite-kontrakt som krevde hele pluginfilen byte-uendret ble oppdatert til den nye migrasjonskontrakten: eksisterende verdier bevares, opprinnelige bytes finnes i backup, og andre kjøring er byte-idempotent. Ingen disable-beskyttelse ble fjernet.
- DI-02 (`d9ea463`): reset validerer hele den foreslåtte effektive snarveimappen før noen av de to filene skrives. Den dokumenterte Command Center/lock-kollisjonen ga først feil i regresjonstesten; etter rettelsen passerte 14 relevante tester. Kollisjon avvises med RC=65, begge eksisterende filer er byte-uendret, koordinert reset av alle virker.
- DI-03 (`065cf40`): appearance reset endrer bare `currentThemeName`, `customThemeFile`, `wallpaperFillMode` og `barConfigs`. Andre DMS-verdier, inkludert autentiseringsvalg, personlig lockerkommando og ikke-utseenderelaterte launcher/power-valg bevares. Backup beholdes; tidsstempelet har mikrosekunder. Først reprodusert tap av preferanser, deretter 10 relevante pass.
- DI-04 (`853f719`): identiske Wilsof-hjelperbytes med ødelagt executable-mode repareres. Mode-reparasjonen er avgrenset til eide, udelte regulære managed helperfiler; personlige konfigurasjonsfiler chmod-es ikke. Først reprodusert 0644-drift, deretter 14 relevante pass.
- PI-04 (`6740e3b`): work, det faktisk avledede profile-navnet og output kontrolleres parvis etter kanonisering før mkdir. Likhet, nesting og symlink-aliaser avvises. Først 3 feil/3 pass, deretter 6 pass.

PI-01 (nøyaktig full pakketransaksjon i cache-preflight), PI-02 (frosset pakke-/verktøy-/profilgrunnlag og deterministisk metadata) og PI-03 (komplett dokumentert byggekommando) er **ikke rettet**. Implementeringsarbeidet stoppet ved den native sikkerhetsregresjonen nedenfor; ingen ufullstendig preflight ble brukt til å bygge.

## 3. Kvalitet og sikkerhet — faktisk AS-02-resultat

Den enkleste Phase 1B-kandidaten ble implementert i `306e964`: ingen syntetisk `loginctl lock-session` i direkte wrapperstart, ingen sticky DMS-Boolean som Command Center-autorisasjon, fortsatt kosmetisk lukking/søkekansellering og avbrutte deferred About/Shortcuts-opens. AS-03-guard og Hyprlock/PAM ble beholdt. Nye callback-/wrappertester feilet først og passerte deretter; 75 fokuserte tester passerte. Det var **ikke** bevis på compositor-isolasjon.

**Den virkelige QEMU-testen avviste kandidaten.** Testet kandidatkilde: `6740e3bec97df5b1e9b7d818dae7705ab01b409a`, bevart på `experiment/integration3-as02-native-rejected-20261102`.

- Hyprland `0.57.0-1`, faktisk commit `0aa6745f705f2c4b0a5004eb019ef76e5bbdb426`; Hyprlock `0.9.6-3`; Quickshell `0.3.2-1`; Dux/DMS `2.0.0-1`; Hypridle `0.1.8-2.1`.
- Dette er ikke identisk Hyprland-kilde med Phase 1Bs nyere inspiserte `e0e9c843...`. Upstream kildeanalyse ble ikke overført som installert sikkerhetsbevis.
- 19:31:07: Hypridle journalførte «Wayland session got locked».
- 19:31:14: Hyprlock journalførte `onLockLocked called`.
- 19:31:40–19:31:51: IPC lukket og åpnet Command Center på nytt med søket `lockedactivation`.
- Deretter genererte QMP nye tastetrykk med den ufarlige kontrollstrengen `notauthorizedinput` og Return.
- 19:32:01–19:32:06: Command Centers faktiske status hadde søket `lockedactivationnotauthorizedinput`. Den samme Hyprlock-prosessen levde, uten journalført autentisert release. Låseskjermen var fortsatt visuelt presentert. Effektiv `session_lock_xray=false`.

Dette er et observert brudd på den nødvendige post-acquisition inputisolasjonen i den testede stakken, ikke bare treg rendering eller tapte syntetiske tastetrykk: kontrollteksten ble faktisk mottatt av feil klient. Den eksakte native rotårsaken er **ikke** etablert; vi påstår ikke at alle overflater eller Hyprland-versjoner har samme feil. Ingen virkelig testpassord ble skrevet etter at denne feilen ble observert.

Kandidaten ble derfor reversert i sin helhet i `264fe33`, inkludert dens endrede testkontrakter. Den historiske forsøksgrenen beholder både kode og tester; tester ble ikke svekket for å godkjenne kandidaten. Integration3 har igjen forhåndsgatene/F1-beskyttelsen fra #49. Det betyr også at #49s uavklarte normale unlock/shell-state-resynkronisering fortsatt finnes. **Ingen av disse tilstandene er deploy-godkjent.** Ingen ny autorisasjonsprotokoll, unlock-bridge, forceunlock eller deaktivert autentisering ble lagt til.

Uavhengig ny sikkerhetsreview: **ikke utført**. Eier forbød nye agenter og betalte tjenester; samme agents adversarielle testing er ikke uavhengig review. Den avdekket likevel en konkret stopper som krever separat uavhengig vurdering før senere akseptanse.

## 4. Commits, kildeverifikasjon og CI

Endelig testet kilde etter revert og den oppdaterte migrasjonsregresjonen: `54ea75b0d361ebdd5912499836e116a8f242561e`. Senere rapport-/evidenscommits er ikke ISO-kilde eller nye runtime-pass.

- Full pytest: **460 pass / 2 skip**, 24,17 sekunder. Første fullkjøring: 459 pass / 1 feil / 2 skip; feilen var den eksplisitt oppdaterte DI-01-migrasjonskontrakten beskrevet over.
- Skip: opt-in rootless native arch-chroot-lab og opt-in native wallpaper/user-manager-lifecycle. Ingen av disse ble feilaktig rapportert som kjørt.
- Begge foreskrevne ShellCheck-grupper, inkludert den nye delte wrapperens shell-kallere: RC=0.
- JSON: 15 filer; Python AST: 73 filer; shell-syntaks: 17 filer; JavaScript `node --check`: 2 filer; eksplisitt payload-manifest: 57 eksisterende, unike, ikke-symlinkede filer. `git diff --check`: RC=0.
- Installer-/konto-/mount-, auth/session-, provisioning-, payload-, package-integrity- og build-kontrakter inngår i fullsuite. Dette er kilde-/fixturetester, ikke signaturkontroll av en ny reell pakketransaksjon.
- QML: kildekontraktene inngår i pytest; forsøkskandidaten ble faktisk lastet som DMS-plugin i gjesten. Separat full `qmllint` med oppløste DMS/Quickshell-importer ble ikke kjørt; hostverktøyet var ikke tilgjengelig. JavaScript-callbacktester er ikke en Qt-/compositor-test.
- GitHub CI-status hentes ved publisering og står i draft-PR. Lokal grønn suite er ikke en påstand om GitHub CI-pass.

## 5. ISO-identitet, størrelse og proveniens

**Ingen Integration3-ISO ble bygget. Ingen nye pakker ble bygget/installert på verten.** Native sikkerhetsgate feilet før build; PI-01/02/03 er fortsatt åpne. Signaturkontroll ble ikke endret eller omgått.

Bevart Integration2:

- `wilsof-internal-2026.11.01-integration2-x86_64.iso`
- 2 549 536 768 bytes.
- SHA256 `cfe0571664b69b94bb8f2aebe0121704aa3e8feb063b11270fee227debc95eec`.
- Opprinnelig ISO-kilde `b755bfabf82ece67eea3d666ea94330ff95f738e`.
- Lokal artefaktkatalog: `wilsof-assets/internal-test-20261101-integration2/` under eierens hjemmekatalog.

52/52 registrerte historiske hash-sammenligninger samsvarte, inkludert original installert disk/firmware før og etter COW-testen. Alle 8 ISO-stier under artefaktroten er med og samsvarer med tidligere registrerte hasher. Dette er et avgrenset manifest, ikke en påstand om alle mulige eksterne lagringssteder. En etterfølgende redundant full artefaktskanning traff 180-sekunders tool-timeout etter at 52/52-resultatet var lagret; ISO-inventaret ble fullført fra de allerede verifiserte resultatene uten å starte nye tester.

## 6. Installasjonsresultater

Ingen ny installasjon eller destruktiv lagringstest etter AS-02-stopp. Historisk Integration2 RC=0 er ikke overført til Integration3. Ingen fysiske disker/USB-enheter, originale QA-disker eller Proxmox-innstillinger ble endret. Gjesten brukte en ny qcow2 COW over den hash-verifiserte historiske installerte disken og egne kopier av firmwarevariabler.

## 7. Boot, passord og native akseptanse

Gjesten var én QEMU 8.2.2 TCG/q35, Nehalem, 2 vCPU og 6144 MiB. Disk-only UEFI-oppstart av COW-fixturen og vanlig greetd/PAM-passordinnlogging til Hyprland ble observert. Feil opprinnelig fixturebruker/passord og ratebegrensning ga først innloggingsfeil; bare testkontoens passord i den disponible overlayen ble rotert, og fixture-faillock ble nullstilt før den vellykkede ordinære innloggingen. Dette er testoppsett, ikke en produktfeil eller auth-bypass.

| Krav | Faktisk resultat på forsøkskandidaten |
| --- | --- |
| Normal lock/unlock | Første syklus: `onLockLocked`, eksplisitt `auth: authenticated for hyprlock`, deretter native release og locker-exit. Funksjonelt pass, ikke full timing-/isolasjonspass. |
| Feil passord | PAM avviste det, locker ble værende, CC-query var uendret. |
| Gjentatt lock / cooperative contention | Andre wrapperlås ble anskaffet; samtidig idle-wrapper rapporterte busy, ikke sikret suksess. |
| Umiddelbar relock | Ikke sertifisert; andre syklus var ikke en tidskritisk umiddelbar relock. |
| CC åpen før låsing | Første syklus tok låsen og mottok feil/riktig passord uten endring av den eksisterende CC-queryen. |
| CC aktivert mens låst | **FAIL: ny tastaturinput ble mottatt av CC.** |
| Forsinket unlock-notifikasjon | Kun callback-/kildekontrakt, ingen native pass. |
| DMS-restart | Ikke kjørt etter fail-fast-stopp. |
| Locker-crash | Ikke kjørt etter fail-fast-stopp. Tidlig fallback-frame ved kald TCG-lås ble ikke kalt prosesskrasj; locker levde og låseframe kom senere. |
| IPC disconnect | Ikke kjørt etter fail-fast-stopp. |
| Ekstern Hyprlock | Ikke kjørt etter fail-fast-stopp. |
| Suspend/resume | Ikke kjørt. Fysisk gate består. |

Ingen full ny akseptanse av Ghostty/Nautilus, appearance/snarveier i GUI, Terminal Idle, logout/login, cold reboot eller installert livsløp. Første post-unlock Super+Space-aktivering åpnet CC, men umiddelbar kontrolltekst ble ikke observert i queryen; derfor ingen full keyboard-liveness-pass. Desktopoppgraderings-/bevaringsfikser er fixtureverifisert, ikke sertifisert som komplette dynamiske upgrade-fixturer.

Se [maskinlesbar avvisning](../qa/integration3-20261102/native-lock-rejection.json), [native lock-frame](../qa/integration3-20261102/native-lock.png), [feil passord-frame](../qa/integration3-20261102/wrong-password.png) og [frame under inputlekkasjen](../qa/integration3-20261102/activation-while-locked.png). At siste bilde viser låseskjermen er ikke bevis på korrekt keyboard-routing.

## 8. Åpne problemer og releasegrenser

AS-02 inputisolasjon er en konkret stopper for den foreslåtte forenklingen på denne stakken. PI-01/02/03, full native AS-03-livstid/session-mapping, alle ufullførte native scenarioer og fresh installation gjenstår. R1 (uforklart historisk DMS SIGKILL/restart) og R2 (hyprland-dialog/libhyprtoolkit-krasj) er fortsatt åpne.

Fysisk Wi-Fi, høyttaler/lyd, mikrofon, Bluetooth, flere skjermer og suspend/resume er ikke testet på kompatibel maskinvare. Ingen public beta-/releasegodkjenning. Integration2 er bevart, ikke reklassifisert som sikkerhetsgodkjent av dette arbeidet.

## 9. Standarder, dokumentasjon og reviewbar levering

Rapporten følger de tolv rapporteringsdelene. Ny draft-PR er stablet på #47, med avgrensede cherry-picks og eksplisitt revert. Historiske PR-heads og artefakter beholdes; ingen merge, force-push, release eller omskriving av eksisterende PR-grener. Den avviste forsøksgrenen er kun reproduksjons-/reviewmateriale, ikke installeringskilde. Rapport og PR kvitteres med commit-pinnet lenke på statusissue #16 uten å lukke releasegater.

## 10. Modell, API og kostnader

Én hovedagent; ingen nye autonome agenter, betalte reviewtjenester eller nye workers. Oppgitt sesjonsrute: gpt-6.1-sol / openai-codex. Faktisk modellforbruk og fakturert kostnad er ikke tilgjengelig; ingen nullkostnadspåstand. Deterministiske shell-/Python-harnesser ble brukt. En web-extract-backend støttet ikke extraction; primærmanualene for pacman/repo-add ble hentet via vanlig HTTP. Ingen installasjon eller produktendring fulgte fra det oppslaget.

## 11. Prosesser, lås, pausekontroller og checkpoint

Den sesjonseide gjesten ble slått av med QGA `guest-shutdown`; QEMU avsluttet med RC=0, eksakt PID var borte, og ikke-reparerende offline qcow2-kontroll av overlayen ga RC=0. Ingen ny gjest eller builder ble startet etter sikkerhetsfunnet.

Prosjektlåsen ble holdt av en tidsavgrenset egen supervisor med automatisk guest-cleanup før release. Ved avslutning ble PID-starttid, kommando, fd/inode og flock verifisert; legitim eier mottok pidfd-bundet SIGTERM, avsluttet, og uavhengig flock-probe ga RC=0. GitHub-worker var fortsatt `paused=true`; scheduler `enabled=false`, `state=paused`. Disse ble ikke aktivert eller konfigurert om.

Varig privat checkpoint: `.local/state/wilsof-qa/integration3-20261102/checkpoint.json` under eierens hjemmekatalog. Det inneholder gren/commits, tester, VM-/låsekvitteringer, bevaringsmanifest, publisering og blokkere. Credential og VM-disk beholdes privat, utenfor rapportpayload. Avgrenset scan av 61 sesjonstekst-/publiseringsfiler fant ingen kopi av nytt testpassord; dette er ikke forensisk sletting eller kontroll av samtalelager/diskfriplass.

Ledig plass ved 2026-11-02T19:42:24Z: 63 581 945 856 bytes / 59,2153 GiB. Ingen lagringsrydding ble utført.

## 12. Neste gate og stoppbeslutning

**Stopp trygt ved den dokumenterte native sikkerhetsfeilen.** Ikke bygg eller deploy den avviste AS-02-kandidaten, og ikke reparer den med en forsinket Boolean-unlock-bro. Neste tekniske beslutning krever uavhengig vurdering av den nøyaktige installerte compositor/focus-grab-stakken og en dokumentert løsning som består post-acquisition inputisolasjon. Deretter må PI-01/02/03 fullføres, kilde-/buildgater kjøres, og en unik ny ISO få fresh-install/livsløpsakseptanse. Dette er en gjenstående oppgave, ikke en automatisk ny agent-/buildstart.
