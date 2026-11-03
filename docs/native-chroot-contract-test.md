# Native arch-chroot-kontraktstest

Denne testen følger opp A–D i [issue #34](https://github.com/tomli0/wilsof-os/issues/34). Den er ikke en ISO-, installasjons-, autentiserings- eller fysisk maskinvaretest. Standard `python3 -m pytest -q` starter ingen container: native-porten er eksplisitt opt-in.

## Produksjonskontrakten

- ISO-manifestet deklarerer `arch-install-scripts` eksplisitt. Den genererte Archiso-customization kjører `verify_arch_chroot_support()` før eventuell lokal pakkeinstallasjon, også uten `--hypridle-package`.
- Støttet baseline er **arch-install-scripts >= 31**, med tilleggskrav om at den faktisk installerte `arch-chroot -r -h` lykkes. Det er en konservativ, testet støttepolicy, ikke en påstand om hvilken første release som innførte `-r`. Native-testen brukte **31-2**.
- Historisk QA-funn F02 hevdet at `-r` først kom i v28. [Oppstrøms v28-kilde](https://github.com/archlinux/arch-install-scripts/blob/v28/arch-chroot.in) har derimot `getopts ':hNu:'` uten `r`. Derfor brukes ikke denne historiske versjonspåstanden som garanti. Selve opsjonsparsing-testen forblir påkrevd.
- Eksternt mål bruker `arch-chroot -r TARGET COMMAND`; allerede klargjort `/` kjører direkte. Ingen skjult fallback ved feil.
- Installert provisioning kontrollerer etter desktop-transaksjonen at `etc/resolv.conf` fremdeles er symlenken `/run/systemd/resolve/stub-resolv.conf`, også når lenkemålet ennå er fraværende. Ved kommando-feil beholdes opprinnelig unntak/exitkode; eventuell resolver-skade eller inspeksjonsfeil legges til som merknad. Live-modus bruker ikke denne installert-mål-postbetingelsen.

## Testlag

| Lag | Faktisk dekning |
| --- | --- |
| `tests/test_chroot_contract.py` | Versjons-/opsjonsgate; kjørbar materialisert customization med/uten pakke og gatefeil; provisioning med faktiske midlertidige filer, resolver-postbetingelse, feilpropagering og eksakt kommando; full `install_package(Path('/'))`-flyt med pakke-/binærvalidering og feiltilfeller. |
| Root-regresjonen | Kun `Path('/')` sine filoperasjoner omdirigeres til en reell midlertidig rot; prosessgrensen simuleres. Den eksisterende separate `target_command('/')`-testen bruker ekte Path-semantikk. Ingen vertsrot endres. Selvkopiering, ugyldig/manglende pakke, symlenker, Pacman-feil og feil binær avvises. |
| `tests/test_arch_chroot_integration.py` | Avviser ubevist isolasjon i ordinær suite. Opt-in kjører det eksakte native-inngangspunktet og kontrollerer rapporten. |
| `tests/integration/arch_chroot_lab.py` | Uendret upstream-wrapper og ekte Arch Pacman, API-mounts, resolverinnhold under transaksjonen og lenke/data etterpå; reell lokal installasjon; ugyldig pakke; exit 23 fra kommando; injisert sysfs-oppsettfeil; full mount-opprydding i alle tilfeller. |

Den nye provisioning-testen erstatter den gamle kilde-/fraværsteksttesten fra `test_pinned_package.py`. To private mutasjonsprober har dessuten avvist henholdsvis tvungen nesting over `/` og bortfall av pakkevalideringen. De er ikke ekstra produksjonsfunksjoner.

## Isolasjon før native-eksekvering

Kun eksisterende, **rootless Docker** og et eksakt lokalt image-ID aksepteres; `--pull=never`. Ingen `--privileged`, verts-home, fysisk disk, Docker-socket eller nettverksinterface bindes inn. Image-roten er read-only; testroten og labens runtime-data ligger i disponible `/work`- og `/run`-tmpfs-er. Grenser: én CPU, 384 MiB minne og 128 prosesser. `/work` er eksplisitt `exec,nosuid,nodev` fordi testen faktisk må starte målbinærer.

Effektive capabilities må være eksakt `SYS_ADMIN`, `SYS_CHROOT`, `SETUID`, `SETGID`, `CHOWN`, begrenset til rootless user namespace. `CHOWN` er nødvendig for Pacmans cache til `DownloadUser=alpm`; ingen `MKNOD`, `SYS_RAWIO` eller generelt sett med capabilities tillates. Host UID 0-mapping, blokknoder, skrivbar image-rot eller annet interface enn loopback avvises før arch-chroot/mount-transaksjonen. Docker-konfigurasjonen kontrolleres før start og namespace-/capability-tilstanden før native-operasjonene.

**Avgrenset lab-tilpasning:** Upstream `arch-chroot`-filen er uendret. En lab-only `mount`-adapter erstatter global devtmpfs med bind av containerens allerede isolerte `/dev`, og sysfs med read-only bind av containerens `/sys`. Andre API-mounts og upstream teardown kjøres faktisk. Adapteren er under `tests/`, ikke i image-payloadmanifestet, og endrer ikke produksjonskommandoen. Testen beviser dermed den avgrensede kontrakten, ikke produksjons-devtmpfs på fysisk maskinvare. Produksjons-arch-chroot deler fortsatt live `/run` og har upstreams vanlige device-/tillitsgrense.

Alle lab-containere er navngitt med unik eieridentitet, kjøres synkront med tidsfrist og fjernes etter avslutning. Eksisterende containere berøres ikke. Ingen scheduler eller utviklingsarbeider startes.

## Reproduksjon uten nytt bygg

Forutsetninger: eksisterende bevart og uavhengig checksum-identifisert ISO, `xorriso`, `unsquashfs`, rootless Docker og et allerede tilgjengelig image med Python 3.11+, bash, coreutils og mount/umount/unshare. Ikke bruk en pensjonert/ufullstendig byggerot som testrot. Uttrekkshjelperen skriver bare i en ny disponibel katalog; den bygger ikke ISO eller installerer på verten.

```sh
python3 tests/integration/prepare_arch_fixture.py \
  --iso "$EXISTING_ISO" --sha256 "$RECORDED_ISO_SHA256" \
  --output "$NEW_FIXTURE_DIRECTORY"

LOCAL_IMAGE_ID=$(docker image inspect "$EXISTING_LOCAL_IMAGE" --format '{{.Id}}')
WILSOF_RUN_ARCH_CHROOT_TEST=1 \
WILSOF_ARCH_CHROOT_FIXTURE="$NEW_FIXTURE_DIRECTORY" \
WILSOF_ARCH_CHROOT_IMAGE="$LOCAL_IMAGE_ID" \
WILSOF_ARCH_CHROOT_REPORT="$PRIVATE_REPORT_PATH" \
python3 -m pytest tests/test_arch_chroot_integration.py -q
```

Uttrekket beholder faktisk `ALPM_DB_VERSION`, faktisk arch-install-scripts-pakkemetadata og root/alpm-identitet fra ISO-en, ikke vertens kontoer. Nødvendige Arch-biblioteker finnes med mål-loaderens `--list`, med begrenset konvergens. Inputfiler og symlenker registreres i manifest og kontrolleres før bruk. Ingen signatur-/CheckSpace-/DownloadUser-kontroll svekkes. Offline-fixturen mangler sync-databaser og kan derfor gi varsler om `core`/`extra`; den kjører aldri `-Sy` eller nettverksnedlasting.

Den syntetiske lokale pakken er kun testdata. SHA-pinnene overstyres kun i testens isolerte Python-namespace for å teste kontrakten; produksjonspinnene og den bevarte Hypridle-pakken endres ikke. Pakken har ingen hooks, installasjonsskript eller avhengigheter. Dette er ikke en ny Hypridle-bygging eller et nytt testbevis for den virkelige Hypridle-binærens funksjon.

Resultat og begrensninger for denne milepælen står i [sluttrapporten](development-reports/2026-10-28-engineering-quality-34.md). Separat tillatelse kreves fortsatt før nytt ISO-bygg.
