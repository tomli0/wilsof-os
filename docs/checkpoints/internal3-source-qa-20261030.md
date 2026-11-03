# Internal3 — kilde-/GUI-kontrollpunkt C/D, 2026-10-30

## Testet identitet

Testet kode: `aa913d7c6f5d54dbea716b9e4597e4df2b3f82f8`, draft #41 på isolert `integration/internal3-20261030`. Kildeeksportens SHA256: `1ef5dfeea5d78a582e3b32732b1660234bcf534a7476efd58661f8a38db3d09c`. Eksporten er overført i begrensede QGA-biter og hashkontrollert før utpakking. Installerte helper-/dropin-hasher er kontrollert. Det immutable underlaget er fortsatt internal2/f7c3945; **dette er nye lokalt deployede kildebytes i disponible COW-gjester, ikke en internal3-ISO**.

Ingen originaldisk ble endret. To sekvensielle QEMU-livsløp (TCG/Nehalem, 2 vCPU, 6144 MiB), aldri samtidige. Andre oppstart brukte et nytt barn over den frosne første overlayen, nye firmwarevariabler og egne logger/sockets. Vanlig greeterpassord ble brukt begge ganger, ikke root/runuser som innloggingsbevis.

## Automatiserte porter

- Før egen rettelse: samlet M1/M2/wallpaper-suite **305 passed / 2 skips**.
- Nye kombinerte tester reproduserte to feil under umask 0002; samme test med 0022 bestod. Faktisk nye mapper var 0775 og M1 avviste dem korrekt. Ingen vilkårlig svekking av M1-validering.
- Rettelse `aa913d7`: fem produksjonslinjer oppretter bare manglende `.local`, `.local/state`, `.local/state/wilsof-os` som 0700. Ingen chmod av eksisterende mapper, ingen profilfil opprettes/resettes. Seks kombinerte tilfeller dekker live/installert med to umasker samt bevart gyldig/korrupt profil og brukerdata.
- Etter rettelse: **311 passed / 2 eksplisitte opt-in-skips**, 16,26 s. ShellCheck sh/bash, Python AST/3.12-grammatikk, JSON og diffkontroll bestått.
- **Sju faktiske systemd-livssyklustester** i gjesten: alle bestått, 108,285 s. Første harnesskall manglet den eksplisitte disposable-VM-markøren og ble korrekt avvist; først den korrigerte kjøringen telles som pass.
- Eksakt aa913d7 push-CI [41027794029](https://github.com/tomli0/wilsof-os/actions/runs/41027794029) og PR-CI [41027889824](https://github.com/tomli0/wilsof-os/actions/runs/41027889824): success, head lest fra check-runs API.
- Native qmllint returnerte 0, men importaliaset i første nye harness var ufullstendig og gav warnings. Dette rapporteres **ikke** som warning-fri/importfullstendig QML-aksept. Faktisk native DMS-lastet plugin og renderet launcher/bar er separat direkte bevis.

Én av maksimalt to målrettede rettelsesrunder er brukt. Ingen spekulativ refaktorering eller nye produktfunksjoner. Ingen ny uavhengig Claude-review; endringen er en middels-risiko brukerprovisjoneringsrettelse, ikke ny privilegie-/disk-/autentiseringspolicy. Tidligere installerreview gjelder uendret installer, ikke ny profilkode.

## Faktiske GUI-/runtime-porter

| Port | Resultat og presis avgrensning |
| --- | --- |
| Normal innlogging | Begge oppstarter: vanlig tuigreet, privat syntetisk passord, ny UID1000-økt. |
| CLEAN-standard | Manglende profilfil i deploy-test gir CLEAN. Første grafiske økt viste CLEAN. Senere kaldstart beholdt eksplisitt valgt CLEAN. |
| Super+Space | Syntetisk QEMU Meta+Space åpnet faktisk eksisterende launcher; første tidlige søketast kom før feltet var klart og ble ikke godkjent. Fysisk klient-ruting ikke testet. |
| Launcher/Enter | Navngitt STUDY, DEV, EVERYDAY, CLEAN-rad visuelt kontrollert før hvert Enter. Alle gav saved=applied, error=null og faktisk synlig barmarkør. Senere åpninger brukte eksisterende Spotlight openQuery; disse er ikke ført som nye Super-tester. |
| Esc | Ekte Esc fjernet spotlight-laget, beholdt CLEAN og rørte ingen klient. |
| Vindusbevaring | Tre faktiske klienter (Ghostty, Text Editor, Files), samme adresse/PID/klasse/posisjon/størrelse/monitor/workspace/mapped/hidden/floating/fullscreen gjennom alle fire valg. Programmatisk likhetskontroll bestod. |
| CLEAN-kontrakt | Ingen dashboard/Kanban implementert/startet. Ordinære vinduer er fortsatt synlige; ingen app-/oppgave-/arbeidsområdemutasjon i profilvalget. |
| Personlig konfigurasjon | Eksisterende layout ble bevart av deploy. Widget ble deretter eksplisitt aktivert bare i disponibel QA-settings, med originalbytes bevart privat; dette er ikke skjult migrasjonspolicy. Nye hjem får standardwidget i egne deploy-tester. |
| Lås/feil passord/opplåsing | Faktisk hyprlock og PAM-avvist feil passord, deretter `auth: authenticated for hyprlock`, locker-exit og original desktop visuelt gjenopprettet. Inhibitor ble aktivert etter at en allerede oppstått idle-lås var håndtert, og deaktivert før stopp. Ikke en presis automatisk 300s-låsmåling. |
| DMS-restart | Ny InvocationID, NRestarts=0, faktisk ExecStartPost exit0 og ny wallpaper-invokasjon/helper0. Godkjent get-sti og faktisk WS-bakgrunn på tomt workspace2. Brukerflyttet fokus til workspace2 er ikke profilflytting; klientene var fortsatt på workspace1. |
| Kaldstart | Ny normal innlogging; faktisk post-hook exit0 09:14:48–49Z, helper0, NRestarts=0, godkjent get-sti og faktisk rendret WS/CLEAN. Etter settling saved=applied=clean/error=null. |
| Ingen restart-/avhengighetsløkker | Native sju porter samt to faktiske oppstarter og eksplisitt DMS-restart. Ingen automatisk restart i disse observerte DMS-livsløpene. |

## Åpne begrensninger og R1–R5

TCG gir betydelige oppstarts-/repaintforsinkelser. Faktiske helper-IPC-timeouts (3 s), midlertidig applied=null/ukjent markør og tidlige stale frames er bevart. Senere stabile porter består; dette sletter ikke tidlige feil. **Ingen ≤1s-launcher-/≤2s-markørpåstand. Ytelse, fysisk Super-ruting og flerskjerm forblir human-check i akselerert/fysisk miljø.**

R1: ingen ny automatisk DMS-kaldstart-SIGKILL observert her; tidligere ukjent årsak er ikke løst. R2: ingen ny hyprland-dialog-core i øktens tidsavgrensede coredump-kontroll; gammel core fra 28. oktober ble eksplisitt skilt fra ny boot. R3: ingen ny gvfsd-fuse-core observert i disse installerte kildegjestene; live-ISO-gate gjenstår. R4: historisk Tracker-varsel er ikke erklært løst. R5: kilderettelse nå kombinert og restart/kaldstart verifisert, men ikke i ny ISO ennå. Alle relevante issues beholdes åpne.

## Bevarte bevis og avslutning av C

Første gjest exit0/offline qcow2 check0 kl. **09:10:01Z**. Kaldgjest exit0/offline check0 kl. **09:17:03Z**. Fullt native/runtime-arkiv er lastet ned og SHA256-verifisert; separat full kaldjournal er bevart privat. Original internal2-ISO, original installert disk og firmware matcher samtlige opprinnelige SHA256 etter siste stopp. Ingen gjest er aktiv ved dette kontrollpunktet. Prosjektlåsen beholdes for beskyttet publisering/evt. bygg; scheduler/worker er pauset.

Bilder som er faktisk inspisert: [STUDY med tre apper](../../evidence/internal3-source-study.png), [DEV](../../evidence/internal3-source-dev.png), [EVERYDAY](../../evidence/internal3-source-everyday.png), [wallpaper etter restart](../../evidence/internal3-source-restart-wallpaper.png), [wallpaper etter kaldstart](../../evidence/internal3-source-cold-wallpaper.png).

## Neste betingede port

C funksjonelle kildeporter er gjennomført med ovenstående eksplisitte ytelses-/human-check-begrensninger; D har én bekreftet rettelse. Ingen nye kritiske/blokkerende integrasjonsfeil er identifisert i denne gjennomgangen. Før E: ny kostnads-/plass-/prosess-/låskontroll, grønn CI på eksakt fryst integrasjonscommit, autentisert byggmiljø/uforandrede signatur- og installergater, rene reviewede kilder. Deretter maksimalt ett internal3-bygg og én konkret verifisert ombygging. Full ny installasjon og F er fortsatt **ikke utført**.
