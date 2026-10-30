# Wallpaper #37 — reaktivering etter DMS-avhengighetsfeil

## Reprodusert rotårsak

Det bevarte internal2-journalarkivet viser 2026-10-28T23:33:07Z at første DMS-prosess avsluttes med status 137 og wallpaper-startjobben feiler med `dependency`. DMS planlegger automatisk restart 23:33:08Z. Dette forklarer ikke hvem/hva som sendte SIGKILL (R1), og retter ikke R1–R3.

Den eksisterende wallpaper-hjelperen har allerede begrensede set/get-forsøk. Problemet er en startjobb som aldri nådde hjelperen: `Requires=dms.service` + `After=dms.service` gir ingen ny aktivering etter at DMS senere starter vellykket. Å legge `Restart=on-failure` til oneshot-en ville derfor ikke treffe den dokumenterte hendelsen.

## Minste produksjonsrettelse

Bare eksisterende DMS-dropin får en ny instruksjon:

    ExecStartPost=-/usr/bin/systemctl --user --no-block start wilsof-wallpaper.service

DMS 2.0s pakkede unit er `Type=notify`; posten kjøres etter READY. Systemd inkluderer ExecStartPost i rekkefølgen før wallpaper, derfor må kølegging være ikke-blokkerende. `-` isolerer en kosmetisk køleggingsfeil fra skrivebordets oppstart. Den eksisterende wallpaper-jobben koaleserer med en samtidig startforespørsel. Ingen timer, daemon, ny Restart-policy eller ubegrenset løkke tilføyes. Hjelperens timeout, assetkontroll og bekreftelse av faktisk get-sti beholdes uendret.

Eksisterende image-manifest og desktop-runtime distribuerer allerede denne dropin-fila; ingen ny installer-/payloadarkitektur trengs. En uendret gammel ISO inneholder ikke rettelsen. Brukerens wallpaper-policy endres ikke utover at den allerede definerte Wilsof-policyen faktisk gjenaktiveres etter DMS-start.

## Native regresjon

`tests/integration/wallpaper_lifecycle.py` kjøres kun som vanlig bruker i eksplisitt disponibel QEMU/KVM-gjest. Den lager unike, isolerte mock-DMS-/wallpaper-/sesjonsenheter i gjestens user-manager; ingen virkelig DMS-, desktop- eller eksisterende enhet startes/stoppes av selve fixturen. Fixturefiler, tellere, verify-resultater og journaler bevares, bare egne nye unit-lenker/jobber ryddes.

    WILSOF_TARGET_VM=1 python3 tests/integration/wallpaper_lifecycle.py --source "$PWD" --evidence "$HOME/.local/state/wilsof-wallpaper-lifecycle"

RED: opprinnelig avhengighetsfeil reprodusert; første DMS-start feiler før READY, andre blir aktiv, null helperkall. Regresjonen som krever reaktivering feiler eksplisitt før rettelsen. GREEN: sju native tester består på systemd 262.1-1:

1. Opprinnelig dependency-feil/no-reactivation kontroll.
2. Rettet recovery og eksplisitt restart gir nøyaktig én ny kjøring per vellykket start, uten startventesyklus/duplikatstorm.
3. Kosmetisk helperfeil er synlig uten å restarte/feile DMS.
4. Ignorert post-hook-køleggingsfeil tar ikke ned DMS.
5. ExecCondition ved manglende binær hopper over helper.
6. Permanent DMS-feil er avgrenset av fixture-startgrense og starter ingen helper.
7. Sesjonsavslutning avbryter pending oppstart før helperen kjører.

Vanlig pytest kjører negative IPC-/assettester og verifiserer den faktiske dropin-kontrakten. Native-porten er bevisst opt-in/skip i CI, ikke en simulert bestått native-test. Den ekte DMS-restart-/kaldstart-/bildeporten dokumenteres separat i øktrapporten; den kan ikke erstattes av disse mock-enhetene.

## Primærkilder

- systemd.service: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html — ExecStartPost, Type=notify, feilprefiks og rekkefølge.
- systemd.unit: https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html — Requires/After/PartOf.
- systemctl: https://www.freedesktop.org/software/systemd/man/latest/systemctl.html — --no-block.

Gjeldende service-/systemctl-dokumenter ble hentet direkte, og faktisk pakkede DMS/systemd-versjoner ble lest i gjesten. Ingen årsak for andre runtimekrasj, fysisk GPU/input/suspend, ny ISO eller offentlig release påstås.
