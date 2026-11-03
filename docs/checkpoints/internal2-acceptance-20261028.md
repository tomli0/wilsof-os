# Internal2 — virtuelt akseptansekontrollpunkt, 28. oktober 2026

## Faktisk gjennomført

- Frosset ISO-kilde `f7c39451e2ff00ae28b6eb2a1809b17ae29072fe`, produksjonskode identisk med reviewet `f628884b314dd13c3bf9d7059eee2fefec1b3400`; `b3b8e74` inkludert.
- Ett fullbygg, bygg-exit0, null ombygginger. Ny signaturverifisert Arch-bootstrap; ingen pensjonert byggerot eller svekkede kontroller.
- `wilsof-internal-2026.10.28-internal2-x86_64.iso`, 2546053120 byte, SHA256 `dc4bfb3944767e743f858880d32b0d1179b5a6c629e5cfed68410e3a73a4f8d1`.
- Faktisk ISO/UEFI/live-boot, én ny selvstendig 24 GiB testdisk, reell syntetisk PTY-installasjon: **installer exit0**, 5/5 prompter, ingen plaintext-passordutskrift.
- Installert mål/vernet konto-/resolver-/pakkepolicy og fstab verifisert; mål rent umontert etter målrettet avslutning av target-Pacman-gpg-agent; installasjonsgjest kontrollert avsluttet.
- Samme vellykkede disk bootet med **ingen ISO tilkoblet**, nye UEFI-variabler; QMP og faktiske root/boot-mounts kontrollert.
- Vanlig greetd-passordinnlogging; faktisk renderte Ghostty, Firefox lokal fixture, Nautilus og Text Editor; tastaturredigering og fil-read-back.
- Reell Super+L/Hyprlock-flate; feil passord ga PAM-avvisning og beholdt samme locker; korrekt passord gjenåpnet original compositor og de samme app-prosessene. Ingen administrativ omgåelse.
- Begge QEMU-prosesser avsluttet med exit0; siste offline qcow2 check exit0. ISO-hash uendret etterpå.

## Ikke slett eller oppgrader bevis til bredere aksept

Privat varig gruppe: `internal2-20261028/`, med `live-vm/`, `installed-vm/`, ny testdisk, separate firmwarevariabler, SHA256-verifiserte private logger/arkiver, kjørekommandoer og separat testhemmelighet. Disk er vellykket installert, **ikke blank**; ikke bruk den til en ny installasjon. Tidligere internal1-disk/ISO og øvrige bevis er bevart. Fire eldre ISO-hasher samsvarer med originalmanifestet. To gamle allerede fraværende scratch-firmwarekopier har verifiserte identiske backupkopier.

[Full rapport med alle 12 seksjoner og 13 porter](../development-reports/2026-10-28-internal2-acceptance.md). [Sanert strukturert evidens og ni faktiske GUI-bilder](../qa/2026-10-28-internal2-acceptance.json).

Åpne runtime-merknader: én automatisk DMS-kaldstartomstart etter UI-SIGKILL, ukjent killer/rotårsak; separat `hyprland-dialog`-krasj i libhyprtoolkit mens kald Nautilus senere rendret; live gvfsd-fuse-krasj; Tracker-varsel; observert upstream desktop-artwork er ikke WS-wallpaper-/persistensaksept. Ingen manuell renderer-/sikkerhetsomgåelse eller spekulativ kodepatch. Funksjonell aksept er ikke en ren/krasjfri runtime-påstand.

Fysisk USB/PC/GPU/Wi-Fi/lyd/suspend, automatisk idle-intervall, pakkeoppgradering og konfigurasjonsgjenoppretting er ikke testet for internal2. Ingen merge, offentlig release eller fysisk diskskriving. #27 forblir draft og #34/#16 åpne.

## Operasjonell grense

Ingen QEMU/bygger/installer gjenstår ved rapportforberedelse. Egen prosjektlås holdes fortsatt gjennom synkron dokumentasjonspublisering; den frigjøres/probes først etter faktisk remote-verifikasjon og siste prosesskontroll. Eksakt sluttkvittering finnes i privat kontrollpunkt og GitHub-statusoppdateringen. Wilsof-jobb `8df95a6101e7` og worker forblir pauset; modellkonfigurasjonen er uendret. Ikke start en ny milepæl, gjest, installer, review eller worker fra dette kontrollpunktet.

Målt ledig byggplass 2026-10-28T23:51:35Z: 106667229184 byte / 99,341599 GiB. Ingen opprydding eller infrastrukturell kapasitetsendring i oppgaven.

Neste anbefaling er en separat godkjent, eierstyrt USB live-test av samme ISO-hash, med R1–R5 fra fullrapporten eksplisitt beholdt. Ingen slik test starter automatisk.
