# Integration3 — PI-01/02/03 kildeutbedring

Dato: 2026-11-02 UTC. Status: **kildeutbedring og fixtureverifikasjon ferdig; native byggeaksept gjenstår**. Ingen ISO-/releasegodkjenning.

## 1. Baseline og fullførte milepæler

PR #50 ble lest fra GitHub og beholdt OPEN/DRAFT ved `16ca0ec82c7552622cdf4ea74b402fafdf434868`, gren `integration/integration3-20261102`. Ny isolert gren: `fix/integration3-pi-remediation-20261102`, direkte fra dette hodet. Verifisert implementeringscommit: **`70fc13569f2719dd892dee472230d62740cebc83`**. Rapporten kommer i en etterfølgende dokumentasjonscommit; den endrer ikke testet implementasjon.

Autoritative definisjoner ble lest før redigering:

- [Review 4 ved publisert commit](https://github.com/tomli0/wilsof-os/blob/3e9d684fa7d3e1f54991c0ab01ec948a6caadad4/docs/development-reports/2026-11-02-iso-package-integrity-review-4.md): PI-01 Medium, PI-02 Medium, PI-03 Low; katalogkollisjonen heter PI-04 Low.
- [Review 5 ved publisert commit](https://github.com/tomli0/wilsof-os/blob/b75b8f8544e48578ac9c299307fe833c48f1ab19/docs/development-reports/2026-11-02-consolidated-engineering-review-5.md).
- [Integration3s stoppbeslutning](2026-11-02-integration3-stabilization-blocked.md) på faktisk PR #50-head.

Review 4/5 finnes på sine publiserte review-grener, ikke i PR #50-treet; de ble ikke kopiert inn eller omskrevet. PI-04s eksisterende tre-katalogvern beholdes. De ytterligere input-/symlinktestene nedenfor dekker oppdragets path-krav uten å feilmerke PI-03s opprinnelige funn.

## 2. Funn, konkrete rettelser og uavhengig review

| Funn | Kildeendring og avgrensning |
| --- | --- |
| PI-01 / Medium | `scripts/package-preflight.py` løser hele den ferdig genererte ISO-manifesttransaksjonen, inklusive avhengigheter, med ny tom lokal pacman-DB, eksplisitt profilkonfigurasjon, cache og offentlig nøkkelring. Ingen `--needed`, ingen vertsinstallert-status som utelatelsesgrunn og ingen skanning av historisk vertscache. Hver forventet fil må finnes og samsvare med DB-SHA256, `.PKGINFO` navn/versjon/arkitektur og en gyldig fullt/ultimat betrodd GPG-signatur; arkivet traverseres med bsdtar. Tom/ufullstendig/ukontrollerbar transaksjon avvises. |
| PI-02 / Medium | `prepare-iso.py` skriver deterministisk `BUILD-SOURCE.json` med kildecommit, kilde-/relenginnhold, modes og symlinkidentiteter. `build-inputs.py` håndhever Archiso 91, ekspanderer faktisk profilpolicy og fryser verifiserte pakker, sync-DB-er og offentlig pubring/trustdb. Profilens Server blir lokal `file://` før mkarchiso, uten svekket SigLevel. `BUILD-INPUTS.json` registrerer pakkeversjoner/hashes/signere, DB-/nøkkelringidentitet, effektiv opprinnelig/frosset policy, generert profil, vertsverktøypakker/kernel/OS-identitet og epoch/versjon. Kopi beholdes ved output. `iso/profiledef.sh` bruker SOURCE_DATE_EPOCH for label og standardversjon, ikke veggklokken. |
| PI-03 / Low | `docs/iso.md` erstatter den defekte korte kommandoen med rent, godkjent git-archive, eksplisitt SOURCE_COMMIT-markør og alle nødvendige verdier gjennom sudo. Faktisk kommando kjøres i en sanitert fixture. Foreldede påstander om ingen installer/autologin, BIOS-støtte og `work/profile` er korrigert; runbook får epoch/versjon og lenke til full prosedyre. |
| Supplerende path-sikkerhet | Wrapperen kontrollerer nødvendige kilde-/releng-/pakkeinput og pin før mkdir. Kanonisk work/profile/output må være parvis disjunkte og atskilt fra input. Fil-valued output, symlinkblad, dangling forfedre, ikke-katalogforfedre, input-nesting og releng-katalogsymlinker avvises. Direkte materialisering nekter profil under/over input og symlinkaliaser. Ingen automatisk destruktiv cleanup legges til. |

Én uavhengig kontekst gjennomgikk hele foreslåtte diffen og fant én Medium stopper: arvede `BUILD-SOURCE.json`/`BUILD-INPUTS.json`-symlinker kunne omdirigere de nye metadata-skrivingene. Den fant ingen andre logikkfeil. Dette ble rettet ved å reservere metadata-/state-navn før kopiering/outputoppretting, avvise eksisterende/dangling metadata og opprette begge JSON-filene eksklusivt med `open('x')`.

En kort separat uavhengig etterkontroll bekreftet akkurat rettelsen: `passed=true`, ingen gjenværende security_concerns eller logic_errors i dette avgrensede funnet. Den verifiserte at filene samsvarte med indeksen og review-diffen SHA256 `3d70ab8a0675713597be8144d45f70f86f3239b006ab3960a3b45cf98ca53d71`; denne diffidentiteten ble kontrollert igjen før implementeringscommit. Etterkontrollen var ikke en ny native/full produktreview. Ingen Claude/OpenRouter-review ble bestilt.

## 3. RED→GREEN, tester og sikkerhetsgrenser

Observerte før-rettelse-resultater er bevart privat som kommandooutput, ikke rekonstruert:

| Regresjon | RED | GREEN |
| --- | --- | --- |
| PI-01, faktisk opprinnelig inlineblokk med erstattede eksterne verktøy | 6 feil: verts-`--needed`/feil config/cache, uvedkommende korrupt cache og manglende fil/signatur/identitet/tom dekning | 6 pass etter transaksjonshjelper |
| PI-02, epoch/materialisering | 3 feil: månedsskifte endret label under fast epoch/versjon, manglende inputproveniens, veggklokkefallback uten epoch | 3 pass |
| PI-02, frosset input/policy | 4 feil: manglende lokal snapshot-/proveniensflyt og policyavvisning | 4 pass; senere tillegg sammenligner hele metadata byte-for-byte ved like kontrollerte input |
| PI-03 + inputgrenser | 6 feil / 4 pass: dokumentert kommando ga RC=2 ved manglende WILSOF_SOURCE_COMMIT; manglende input, input/output-nesting og ugyldig epoch/versjon ble ikke avvist tidlig | 10 pass; sammen med opprinnelige path/docs/cleanup-kontrakter 19 pass på dette stadiet |
| Ekstra path-forfedre/relengfil | 2 feil | 2 pass |
| Direkte materialiseringskollisjoner | 3 feil | 3 pass |
| Review-funn, reserverte metadata | 9 feil pluss 1 wrapperfeil | 10 pass; eksterne scratch-sentinelfiler beholdes uendret |

Sluttverifikasjon på implementeringsinnholdet i `70fc13569f2719dd892dee472230d62740cebc83`:

- Fokusert: **98 pass**, RC=0, 2,20 s.
- Full tilgjengelig source-suite: **499 pass / 2 skip**, RC=0, 26,03 s. Baseline var 460 pass / samme 2 skip.
- Skip: eksplisitt opt-in rootless arch-chroot-lab og disponibel QEMU user-manager/wallpaper-livssyklus. Ingen av dem ble startet.
- Begge foreskrevne ShellCheck-dialektgrupper: RC=0; sh-gruppen inkluderer også session-/idle-kallere.
- Python AST: 79 filer; JSON: 16; shell `-n`: 17; JavaScript: 2 etter fjerning av QMLs `.pragma library` kun i parserinput. Dette er ikke native QML-/compositorvalidering.
- Eksplisitt image-payload: 57 unike, eksisterende, ikke-symlinkede filer. Fire lokale dokumentlenker kontrollert. Staged whitespace-kontroll RC=0. Avgrenset scan av added lines for hemmelighetsliteraler, shell-injection, eval/exec og pickle ga ingen treff.
- Ingen eksisterende assertions ble svekket. Cleanup-testens fixture ble tilpasset den nye preflightgrensen; eksakt mkarchiso-argv uten `-r` og beholdt profil er fortsatt påkrevd.

Reproduserbare source-kommandoer:

    PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -rs -p no:cacheprovider
    PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -rs -p no:cacheprovider \
      tests/test_package_preflight.py tests/test_build_inputs.py \
      tests/test_build_interface.py tests/test_build_paths.py \
      tests/test_pinned_package.py tests/test_iso_materialization.py \
      tests/test_iso_cleanup_contract.py tests/test_image_payload_contract.py \
      tests/test_boot_experience.py tests/test_hardware_diagnostics.py \
      tests/test_chroot_contract.py tests/test_iso_build_documentation.py

ShellCheck-kommandoene følger `.github/workflows/validate.yml`/`CONTRIBUTING.md`, med de supplerende sh-wrapperne nevnt over. Testharnessene erstatter pacman, pacman-conf, GPG og arkivverktøy; wrapperharnessen erstatter også materialisering, frysing og mkarchiso. Ingen fixture-signatur er en ekte Arch-pakkesignatur. En innledende Node-sjekk av uendret QML-JS feilet på Qt-direktivet; den korrigerte parserinputkontrollen over er det beståtte resultatet.

## 4. Commits og CI-status

Implementering: `70fc13569f2719dd892dee472230d62740cebc83`, på separat remediation-gren over uendret #50. Rapport og draft-PR publiseres separat, stablet på Integration3; ingen merge til denne grenen eller main. Remote-head og eksakt rapportblob skal leses tilbake ved publisering, med kvittering i PR/statusissue og privat checkpoint.

PR #50 rapporterte ingen checks ved fersk lesing, ikke CI-green. Workflowens branchfiltre dekker ikke denne nye stablede basen; faktisk ny-PR-status kvitteres ved publisering. Lokal grønn testkjøring er ikke påstått GitHub CI-pass.

## 5. ISO-identitet og historisk bevaring

**Ingen ISO ble bygget, endret, montert, startet eller publisert.** Ingen nytt ISO-filnavn, størrelse eller hash konstrueres. Historiske artefakter forblir historiske; de inneholder ikke disse kildeendringene.

Et read-only metadata-inventar av `wilsof-assets` og den eksisterende lokale QA-roten omfattet **587 788 stier**. Ved kontroll 21:38:16 UTC var device/inode/mode/size/mtime/ctime uendret for samtlige; ingen manglet. Dette er en metadata-/ikke-skrivingskontroll, ikke en ny full innholdshashrevisjon av alle QA-filer. Alle **32** forhåndseksisterende remote branch-heads var uendret. PR #50s opprinnelige worktree var rent og stod fortsatt på eksakt baseline. Sluttkvitteringen gjentar kontroller etter publisering.

## 6. Installasjon og lagring

Ingen pakkeinstallasjon, systemoppgradering, ISO-bygg, QEMU, fysisk diskoperasjon, USB-skriving eller Proxmox-endring. Ingen ny installasjon/boot/installer-exit/PAM-/desktopaksept hevdes. Scratch brukes bare til kilde-, test- og evidensfiler.

Tilgjengelig lagring målt 21:38:16 UTC: **63 311 691 776 bytes**. Ingen historisk lagringsrydding ble utført. Endelig tidsstemplet tilgjengelig kapasitet oppgis i publiseringskvitteringen.

## 7. Oppstart, passord og fysisk klient

Ikke testet og ikke innenfor oppdraget. AS-02, Hyprlock, DMS og desktopatferd er ikke endret. Historisk boot/innlogging er ikke overført til denne kilden. Fysiske klientkontroller for USB/UEFI, GPU, Wi-Fi, lyd/mikrofon/Bluetooth, tastatur, skjermer og suspend/resume gjenstår som separate eierautoriserte porter.

## 8. Resterende begrensninger

- **Native pacman/pacman-conf/bsdtar og Archiso 91 mangler i denne source-testverten.** Ingen pakker ble installert for å omgå oppdraget. Den lokale filrepoen, kopiert offentlig nøkkelring, ekte signaturer og faktisk mkarchiso-transaksjon må få separat autorisert native aksept før byggbruk. Fixturepass er ikke dette beviset.
- Inputfrysingen er sporbarhet, ikke et uavhengig bevist byte-for-byte reproduserbart ISO. Like kontrollerte input gir like metadata; releng-endring gir endret identitet. Verktøypakkeversjoner/kernel/OS registreres, men hele vertens binær-/bibliotek-/filsystemtilstand fryses ikke av wrapperen. Byggeverten må holdes uendret av sin eier. Hooks, mtimes, komprimering og ISO-verktøy kan fortsatt påvirke bytes.
- Første løsning bruker aksepterte repo-/trustinput; behold frosne DB-/pakke-/signaturbytes og metadata for sammenligning/replay. Ingen gjenbruks-/resume-/cleanupautomatikk er lagt til. Samtidig ekstern endring av input/forfedre er utenfor det støttede eneier-byggeoppsettet.
- DatabaseOptional beholdes; dette er ikke obligatorisk databasesignering. Trusted pakkesignering svekkes ikke. Den separate interne Hypridle-artefakten beholder eksisterende package/binary SHA256-pin, ikke en påstått offisiell Arch-signatur eller varig full-upgrade-policy.
- AS-02 og alle øvrige runtime-/releaseblokkerere består. Ingen byte-identisk ISO-, native sikkerhets- eller public-beta-godkjenning gis.

## 9. Standarder og leveranse

Omfanget følger Engineering Standards og rapporteringens tolv deler: riktig base, RED→GREEN, uavhengig review, én presis review-rettelse, full source-verifikasjon og separat draft-PR. Primærmanualen for pacmans print-format og Archiso v91s config/cache-forbruk ble hentet read-only for grensesnittkontroll; ingen produkt-/systeminstallasjon fulgte. En extraction-backend feilet; direkte HTTP-oppslag ga faktisk kildeinnhold.

Ny PR endrer ikke #50s branchhistorikk, og lukker ingen releasegate eller issue. Publiseringskvitteringen angir eksakt final head, rapportlenke og faktisk CI-status. Rapportens relative lenke til tidligere stoppbeslutning er bevart.

## 10. Modell/API og avgrensning

Hovedsesjon: `gpt-6.1-sol / openai-codex`. To avgrensede read-only reviewkontekster: første gjennomgang og kort bekreftelse av det ene funnet. Ingen eksplisitte OpenRouter-kall, fallback-, balance- eller betalt-reviewtjeneste ble startet. Faktisk fakturert kostnad og samlet tokenbruk er ikke tilgjengelig; ingen nullkostnadspåstand. Oppgaven stoppes etter denne PI-leveransen, uten videre utviklingsrunde.

## 11. Prosesser, låser og checkpoint

Ingen builder, VM, installer, updater, prosjektworker eller scheduler ble startet. Ingen eksisterende prosjektlåseier ble stoppet eller lås fjernet; source-only arbeid tok ingen VM-/byggekjøringslås. Eksisterende worker-/schedulerkontroller ble ikke skrevet eller aktivert; deres driftsstatus ble ikke resertifisert. Alle test-/inspeksjonsprosesser var synkrone og avsluttet.

Privat evidens inneholder før/etter metadata, remote-head-snapshot, faktiske RED/GREEN-/fullsuite-/statikkresultater, reviewdiffidentitet og publiseringskvittering. Ingen private QA-disker, credentials eller rå agenttranskripter publiseres.

## 12. Stopp og neste gate

**Stopp etter PI-remediation og draft-PR.** Ingen automatisk AS-02-utbedring eller Integration3-ISO-konstruksjon. Før eventuell fremtidig byggbruk: separat autorisert, disponibel native kontroll av den nøyaktige frosne pacman-/nøkkelring-/Archiso 91-flyten, med AS-02s uendrede NO-GO respektert. Dette er en gjenstående port, ikke en startet oppgave.
