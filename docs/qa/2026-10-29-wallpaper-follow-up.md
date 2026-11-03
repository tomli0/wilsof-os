# R5 — avgrenset wallpaper-oppfølging etter M1

Dato: 2026-10-29. **Kun analyse og testforslag. Ingen wallpaper-, DMS- eller Hyprland-kode er endret i M1.**

## Direkte bevis og hva det ikke beviser

Internal2-rapporten ved `219894f1d4fc365b5e6546c2af9a146141634a1c` beskriver R1–R5. M1 har i tillegg lest originalarkivets `run/internal2-installed-journal.log` uten å starte gjesten eller skrive i arkivet:

    2026-10-28T23:33:07+00:00 dms.service: Main process exited, code=exited, status=137/n/a
    2026-10-28T23:33:07+00:00 wilsof-wallpaper.service: Job wilsof-wallpaper.service/start failed with result 'dependency'.
    2026-10-28T23:33:08+00:00 dms.service: Scheduled restart job, restart counter is at 1.

Dette er en kort sanert transkripsjon (verts-/brukerdetaljer utelatt). Arkiv, JSON-diagnostikk og opprinnelige skjermbilder er bevart i den private bevisgruppen `internal2-20261028/installed-vm/`. Senere UI1103 kom opp. Manglende bekreftet WS-bakgrunn og session-tilstand er dokumentert tidligere; dette er ikke en ny grafisk test.

Kilden viser `Type=oneshot`, `Requires=dms.service`, `After=dms.service`, `TimeoutStartSec=150`, ingen Restart-policy; helperen har allerede opptil 120 s med IPC-forsøk, 5 s per kall, og krever både vellykket set-svar og identisk get-sti. Å hevde «ingen retry» uten dette skillet ville være feil: det finnes **IPC-retry i en kjørende helper**, men ikke en ny aktivering etter en avhengighetsfeilet startjobb.

R1s SIGKILL-årsak/killer er fortsatt ukjent. R2 (hyprland-dialog/libhyprtoolkit) og R3 (live gvfsd-fuse) har heller ikke tilstrekkelig verifisert rotårsak. Wallpaper-avhengighetskjeden er ikke forklaringen på disse krasjene, og ingen av dem lukkes.

## Vurdering av tidligere forslag

`After=` gir rekkefølge, ikke ny aktivering. `Restart=on-failure` håndterer feil i tjenestens egen kjøring; en startjobb som ikke nådde ExecStart på grunn av `dependency`, får ikke automatisk en ny start bare ved denne innstillingen. `RestartSec`/`StartLimit` alene fyller derfor ikke hullet. Dette er en statisk slutning fra journal + unit + systemd-kontrakten, ikke en ny runtime-reproduksjon.

## Minste foreslåtte rettelse — krever egen godkjenning/test

Legg én ikke-blokkerende aktivering til eksisterende DMS-user-dropin, uten å endre helperens sikkerhets-/bekreftelsesregler:

    [Service]
    ExecStartPost=-/usr/bin/systemctl --user --no-block start wilsof-wallpaper.service

Dette er **ikke implementert**. DMS er `Type=notify`; posten kjøres etter READY. `--no-block` er nødvendig fordi wallpaper har `After=dms.service`, og ExecStartPost inngår i denne rekkefølgen; synkron venting kan ellers skape en startventesyklus. Prefikset `-` hindrer at en kosmetisk køleggingsfeil gjør DMS-oppstart til feil; systemd-journalen må fortsatt bevare og testen fange den. Den eksisterende wallpaper-jobben og en ny startforespørsel skal koalesere, ikke starte to skrivere. En vanlig fullført oneshot blir inaktiv og kan startes på nytt etter neste vellykkede DMS-start. Ingen timer, poll-daemon, ny bakgrunnstjeneste eller ubegrenset retry foreslås.

Dette er det minste forslaget fordi det kobler til den faktisk manglende hendelsen (ny vellykket DMS-start), ikke bare til helperfeil. Det må forkastes/justeres dersom isolert test på målversjonen av systemd/DMS ikke viser riktig jobbkoalesering, feil-isolasjon og stoppsemantikk. Ingen generell wallpaper-policy for brukerens bevisste bakgrunnsendring avgjøres her; eksisterende Wilsof-policy beholdes, ingen nye innstillinger innføres.

## Avgrenset testplan for egen oppgave

1. Lag en disponibel **isolert user-manager-fixture**, ikke vertens aktive desktop: navn-avgrensede mock-DMS/wallpaper-enheter. Reproduser første DMS-startfeil før READY og senere automatisk vellykket restart. Rød kontroll: opprinnelig unit gir dependency-jobbfeil og null wallpaper-kjøringer etter gjenoppretting.
2. Grønn kontroll: forslaget kølegger nøyaktig én wallpaper-kjøring etter vellykket READY, også etter eksplisitt DMS-restart. Ingen ventesyklus, duplikat kjørende helper, retry-storm eller start uten aktiv økt. Registrer journal, InvocationID, antall kjøringer og tidsgrenser.
3. Negative porter: permanent DMS-startfeil, manglende IPC, IPC timeout, uventet set/get-svar, manglende asset/binary, køleggingsfeil, logout under pending jobb. DMS skal ikke feile fordi kosmetikken feiler; feilen skal fortsatt være synlig. Behold eksisterende helpertester; legg til livssyklustest, ikke strengmatch alene.
4. Bare ved separat godkjenning: eksisterende disponibel VM, ingen ISO-bygg eller reinstallasjon. Faktisk brukermiljø, normal kaldstart og `systemctl --user restart dms`, journal, prosess-/lagtilstand, `dms ipc call wallpaper get` og rendret bilde av godkjent asset. Gjenta etter login/restart med alle profilmarkører; ingen profilkode skal være en forutsetning.
5. Bevar original ISO og R1–R3; lokal konfigrettelse er ikke rettelse av immutable internal2-bytes. Fysisk GPU/USB/input/suspend blir egne uutførte porter.

## Primærkilder

- [systemd.service — ExecStartPost og Restart](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)
- [systemd.unit — Requires og Before/After](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html)
- [systemctl — --no-block](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html#--no-block)
- [Bevart internal2-rapport](../development-reports/2026-10-28-internal2-acceptance.md)

Avgrenset oppfølging er registrert som [issue #37](https://github.com/tomli0/wilsof-os/issues/37), uten approval-label eller worker-autorisasjon. Opprettelsen er ikke automatisk oppstart av M5.
