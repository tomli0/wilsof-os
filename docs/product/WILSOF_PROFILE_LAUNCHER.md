# M2 — profilvelger og profilmarkør

M2 er en tynn utvidelse av eksisterende DMS 2.0-launcher og top bar. Den starter ingen apper eller dashboard. M3/M4 implementeres ikke.

## Bruk

- Super+Space åpner eksisterende DMS-launcher. Skriv `profil`, velg CLEAN, STUDY, DEV eller EVERYDAY med piler og Enter. Esc avbryter uten å endre profil.
- Klikk profilnavnet i baren for samme launcher med `profil` som søk. DMS kan også finne egne app-/innstillingsrader; velg den navngitte `Profil · …`-raden, ikke automatisk første treff. Et eksakt søk som `Profil · DEV` begrenser treffene.
- Markøren viser bekreftet profil. `· ?` betyr ukjent/ikke bekreftet GUI; rødt betyr feil. En feil ved valg gir DMS-feilmelding, aldri suksessmelding.
- `wilsof-profile get/list/set` beholder M1s rene tilstandskontrakt. `set` lagrer bare ønsket profil. `wilsof-profile-ui status` returnerer JSON med `saved`, `applied` og `error`; `apply <profil>` serialiserer lagring og avgrenset GUI-verifikasjon.

## CLEAN og GUI-bekreftelse i M2

Ingen klient-, arbeidsområde-, fokus-, oppgave- eller prosessmuterende Hyprland-operasjoner utføres. Hjelperen leser klienter og lagflater på alle skjermer. Den krever grafisk økt og gyldige IPC-inventarer før en profil bekreftes. M4 finnes ikke: hvis en flate med eksakt identitet `org.wilsof.Tasks` oppdages, avvises operasjonen tydelig. Hjelperen starter aldri dashboard bare for å skjule det, og dreper/flytter/skjuler ingen vinduer.

`applied` i M2 bekrefter derfor kun den implementerte M2-kontrakten: valgt profil med ingen dashboardflate i kompositorinventaret. Det er ikke en implementasjon av den fremtidige M4-protokollen. Skjuling av levende dashboard, dialoger, usendt redigering og reconnect må fortsatt leveres/testes i M4. Bekreftelsen er et øyeblikksbilde; ett delt QML-singleton oppdaterer bar/launcher og kontrollerer på nytt hvert femte sekund (anvendelsessvaret oppdaterer markøren direkte, ikke ved neste poll). Ved samtidige GUI-valg serialiseres kall, siste ventende valg vinner, og foreldede svar gir ingen suksessmelding. Det innføres ingen egen daemon.

Korrupsjon gir CLEAN-lesefallback med synlig feil og `applied=null`; original fil bevares og nytt valg avvises. IPC-feil, ugyldig svar, timeout eller fraværende GUI gir aldri anvendt profil. GUI kan forsvinne etter lagring: ønsket profil kan da være lagret mens `applied` er null. Ny status avstemmer uten å reparere tilstand stille.

## Distribusjon og personlige innstillinger

`runtime/image-files.txt` inkluderer begge hjelpere og alle seks pluginfiler eksplisitt. Eksisterende `runtime/desktop.py` installerer disse i brukerens hjem med eksisterende confinement/backup. Det eldre VM-installasjonsskriptet gjenbruker samme runtime; det kjøres ikke på utviklingsverten.

Nye hjem får profilwidget i standardbar. Eksisterende personlige `settings.json` forblir byte-identisk; M2 flytter ikke brukerens widgets. Pluginoppføringen legges til i DMS' separate `plugin_settings.json` bare når den mangler, med backup av tidligere fil. Andre plugins og eksplisitt deaktivering beholdes. For en eksisterende personlig bar legges Wilsof Profiles til gjennom DMS' barinnstillinger; ingen automatisk layoutoverskriving. Ugyldige eller symlinkede plugininnstillinger avvises, ikke repareres.

## Primærkilder og porter

API-grunnlag er Dux/DMS-tag `v2.0.0`: `.agents/skills/dms-plugin-dev/references/launcher-plugin-guide.md`, `widget-plugin-guide.md`, `quickshell/Services/PluginService.qml`, `Common/SettingsData.qml`, `Modules/Plugins/PluginComponent.qml` og `DMSShellIPC.qml`. Kildene ble hentet og lest direkte før implementering. Manifestet bruker v2s faktiske `components.launcher/widget`; plugininnstillinger er DMS' dokumenterte separate fil, ikke en ny innstillingsmotor.

Fokuserte automatiserte tester: `python -m pytest tests/test_profile_ui.py tests/test_profile_plugin.py tests/test_profile_deployment.py -q`. JS-modellen kjøres faktisk med Node; mock-IPC er grense-/feilhåndteringstester, ikke GUI-bevis. Full suite, CI og VM-resultater står i den daterte øktrapporten. Fysisk Super-tast videresending fra klient, flere fysiske skjermer og endelig ISO-akzept blir ikke bevist av IPC eller syntetisk QEMU-input.
