# Kontrollpunkt — internal3 E2-gjenoppretting, 2026-10-30 (sanert)

Gjenopptatt fra privat kontrollpunkt `CONTROLLED_STOP_BLOCKED_BEFORE_INTERNAL3_ISO` (09:43:59Z). Dette er den sanerte offentlige gjenopptakingsreferansen; private logger/disker/legitimasjon beholdes i privat QA-gruppe.

## Status ved gjenopptakelse (verifisert 10:10–10:16Z)

- Fryst byggkilde `448e0190e786475f083abdce223b3b24dc2a85ef` byte-identisk med bevart `frozen-source.tar` og payload-manifest (42/42 kontroller).
- Bevart resume-work: 16 ferdige run-once-markører, profil og identifisert SquashFS (sha256 `6f5c4f92…dcf7`); `out-internal3` tom; ingen ISO tidligere.
- Ingen aktive bygg-/QEMU-prosesser, ingen private mounts; prosjektlås ledig; scheduler paused/worker paused; 5 tidligere ISO-er og 14 remote-refs hash-/SHA-uendrede.
- Eksisterende modellruting inspisert, ikke endret (config sha `ab41ee8f…`); OpenRouter-nøkkelmåling 48,328455501 USD som baseline.

## E2-avklaring (10:16–10:19Z)

- Rotårsak: `mkarchiso -r` (Archiso 91) fjerner airootfs rekursivt i starten av `_build_iso_image`, før xorriso; privat selv-bind for nested CheckSpace lever til navneromsavslutning ⇒ EBUSY før ISO. Sekundært: `base._make_work_dir`-markøren hopper over `-r`-nullstilling ved resume.
- Rettelse `a952e80…`: wrapper utelater `-r`, beholder work/profile; cleanup-kontrakt dokumentert; regresjon RED→GREEN; 312/2; eksakt push+PR-CI success.
- Disponibel native lab: tom-katalog-rmdir ga EBUSY; faktisk mkarchiso+xorriso uten cleanup exit 0; ingen host-lekkasje; ingen rekursiv sletting.

## ISO og F-port

- Finalisering exit 0 på bevart kilde/work (ingen ny pakketransaksjon); `wilsof-internal-2026.10.30-internal3-x86_64.iso`, 2548035584 byte, sha256 `b3cf9726…3dd1`; immutable-audit 55/55; embedded SquashFS identisk med bevart.
- Ny disponibel 24GiB-disk + fersk firmware; installer exit 0 (5/5 prompts, skjult passord); 25/25 målkontroller; ren unmount; live-gjest exit 0/check 0.
- Disk-only UEFI-boot uten ISO; vanlig passordinnlogging; rendret skrivebord/bar/wallpaper; fire renderte apper; fire profiler satt og verifisert; launcher+Fremhev-rad+Esk-kontrakt; hyprlock lås; feil passord PAM-avvist; korrekt opplåsing etter dokumentert pam_faillock-vindu (sluttkvittering i [fullrapporten](../development-reports/2026-10-30-internal3-e2-recovery.md)).

## Gjenstående

Fysisk USB-testklarhet **CONDITIONAL GO**; R1/R2-runtime-notater; TCG-only-bevis; cleanup av bevart build-work krever verifisert prosessavslutning + mount-sjekk + separat autorisering. Fysisk disk/USB, Proxmox, merge, release, M3/M4, scheduler/worker: uendret ikke-autorisert.
