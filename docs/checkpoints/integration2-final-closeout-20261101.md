# integration-20261101 — integration2 final closeout

2026-11-01 UTC. [Full 12-punktsrapport](../development-reports/2026-11-01-integration2-final-closeout.md). Draft #47, stablet på #46; ingen merge/release.

- ISO: `wilsof-internal-2026.11.01-integration2-x86_64.iso`, `2549536768` byte.
- SHA256: `cfe0571664b69b94bb8f2aebe0121704aa3e8feb063b11270fee227debc95eec`.
- Eksakt kilde: `b755bfabf82ece67eea3d666ea94330ff95f738e`. Historisk lokal suite 375 passed / 2 skipped; ikke gjentatt. Ingen CI-sjekker rapportert på kilde-head ved kontroll.
- Bevart byggmanifest: build exit 0. Full fersk installasjon: **RC=0**, bevart installasjonsresultat. Ingen nytt bygg eller ny installasjon i avslutningen.
- Tidligere installert aksept **PASS**: selvstendig disk-only boot, passordinnlogging, Hyprland, DMS, Command Center, Shortcuts-modal, Ghostty, Nautilus, lås/opplåsing. Ikke gjentatt.
- Ny kald omstart via eksisterende `launch-disk.sh`: **PASS**. Ingen ISO, ext4-root på disponibel disk, normal passordinnlogging med ny PAM-session 23:29:39Z, aktiv Wayland/Hyprland/DMS og visuelt bekreftet desktop. Ikke en ny in-place `systemctl reboot`-test. Tuigreet, ikke ReGreet-aksept.
- `/tmp/install-transcript` var borte etter oppstart; eksplisitt fjerning/fravær bekreftet før avslutning. 212 gjestefiler undersøkt uten hemmelighetstreff; én testgenerert privat vertskopi sladdet; 402 scoped tekstfiler uten treff etterpå. Ikke forensisk sletting eller full historikklagringsaudit. Ingen rålogger/hemmeligheter publisert.
- **49/49** bevarte artefakter hash-/størrelsesidentiske; **15/15** bevarte qcow2-sjekker exit 0. Originale QA-disker ikke modifisert. Disponibel disk bestod offline før/etter; endelige disk-/firmware-hasher privat.
- Gjest kontrollert avsluttet via QGA powerdown; QEMU **exit 0**, ingen QEMU igjen, offline sluttkontroll **0**.
- Prosjektlås beholdes til publiserings-read-back; frigivelse bare etter ny identitets-/eierskapskontroll og dokumentert normal avslutning. Sluttkvittering i privat kontrollpunkt og #16. Scheduler/worker fortsatt pauset.
- **PENDING:** R1 (historisk DMS-kaldstart/SIGKILL), R2 (hyprland-dialog/libhyprtoolkit), fysisk maskinvareaksept og uavhengig review. Ingen frisk runtime-/releasepåstand.

Privat gjenopptakingsnøkkel: `integration-20261101/checkpoint.json`. Bevar ISO-er, installert disponibel disk, firmware og private sanerte bevis. Neste steg krever separat autorisasjon; ingenting starter automatisk.
