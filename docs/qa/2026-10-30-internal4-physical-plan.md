# Internal4 — fysisk live-diagnostikk og avgrenset retest

Status: fysisk Wi-Fi-/lyd-/Bluetooth-godkjenning **PENDING**. Dette er en read-only diagnoseplan, ikke tillatelse til installasjon, USB-skriving eller endring av interne disker.

## Observerte fakta fra første internal3-test

Eieren har bekreftet fungerende UEFI-meny, splash, live-skrivebord, Hyprland/DMS, Super+Space, CLEAN/STUDY, profilmarkør, batteridata, kontrollsenterdesign og Wilsof-bakgrunner. Dette visuelle grunnlaget skal beholdes. Wi-Fi/internett og lydavspilling fungerte ikke i denne testen. Bluetooth viste «No adapters»; faktisk adaptertilstedeværelse er ukjent. Ingen PCI-/USB-ID-er eller fysiske driverlogger er levert. Bilder alene beviser ikke driverfeil eller krasj.

## Read-only rapport fra samme fysiske live-økt

Kjør som den vanlige live-brukeren, **uten sudo**:

    ~/.local/bin/wilsof-hardware-report > ~/wilsof-hardware-report.json

Internal3 har ikke dette nye skriptet innebygd. For diagnose før en ny ISO må eieren hente den eksakte, gjennomgåtte `bin/wilsof-hardware-report` fra denne PR-en på en annen maskin og gjøre filen tilgjengelig i live-økten. Der kan den kjøres uten installasjon:

    python3 /sti/til/wilsof-hardware-report > ~/wilsof-hardware-report.json

Ingen nedlasting, installasjon, nettverkstilkobling, radioendring, unmute, service-restart eller opplasting utføres av skriptet. Vanlige statusforespørsler til PipeWire/Pulse kan utløse deres eksisterende socket-aktivering; ingen konfigurasjon eller aktiveringspolicy endres. Rapporten skriver bare JSON til stdout; omdirigeringen over oppretter den valgte rapportfilen.

Rapporten inneholder kun:

- numeriske PCI-nettverks-/lyd-ID-er, subsystem-ID-er og driverens modulnavn;
- numeriske USB vendor/product-ID-er, uten serienummer eller produkt-/produsentnavn;
- rfkill-type og hard/soft-block, uten radio-/nettverksnavn;
- relevante pakkeversjoner og avgrenset systemd-tilstand for NetworkManager, Bluetooth, PipeWire, WirePlumber og DMS;
- nettverksenhetstype/tilstand og Wi-Fi radio enabled/disabled — ikke SSID, tilkoblingsnavn, MAC, IP eller nøkler;
- anonymiserte sink/source-indekser, standardvalg, mute/volum og tilstand — ikke lydstrømmer, mediatitler eller enhetsnavn;
- antall relevante kernel-feillinjer og eksplisitte manglende firmwarefilnavn/-feilkoder — ingen råjournal.

Utilgjengelige verktøy, utilgjengelig kerneljournal og tidsavbrudd vises som `unavailable`; det er ikke et rent resultat. Rapporten er et øyeblikksbilde, ikke en atomisk måling. Del bare den gjennomgåtte JSON-rapporten og korte testobservasjoner, aldri passord, Wi-Fi-nøkler, private filer eller rålogger. Ikke legg til nettverksnavn i issue-kommentarer.

## Hva kildeundersøkelsen faktisk viser

- Immutable internal3-live har NetworkManager 1.58.1-2, wpa_supplicant 2:2.12-1, linux-firmware 20260916-1 (inkludert leverandørfamiliene), sof-firmware 2026.09.2-1, alsa-ucm-conf 1.2.16.1-1, alsa-utils 1.2.16-1, PipeWire/Pulse/audio 1:1.6.10-1 og WirePlumber 0.5.18-1. NM er aktivert; PipeWire/Pulse-sockets og WirePlumber-lenke er inkludert.
- Dermed er «alle lyd-/Wi-Fi-pakker mangler» avkreftet for denne ISO-en; en bestemt fysisk driver-/firmwarefeil er **ikke** avkreftet.
- Det bevarte installerte internal3-målet mangler SOF-pakken som live-image har. Internal4-manifestet inkluderer derfor generisk `sof-firmware` eksplisitt også for installert desktop. Dette forklarer **ikke** lydfeilen i brukerens live-test, og er ingen chipsetspesifikk driverrettelse.
- Live-image har `bluez-libs`, men ikke `bluez`-daemonen. «No adapters» kan derfor ikke brukes som bevis for manglende fysisk adapter. Ingen BT-driver eller tjenestepolicy endres uten relevant verifikasjon.
- Den disponible QEMU-gjesten gir kun Ethernet/HDA-testdata. Den kan ikke godkjenne fysisk Wi-Fi, høyttalere, mikrofon eller Bluetooth.

## Anbefalt fysisk retest etter gjennomgang

1. Bruk samme identifiserte internal3-ISO til første diagnose; noter faktisk ISO/SHA256 og bærbar modell uten serienummer. Ikke skriv USB eller interne disker gjennom agenten.
2. Samle rapporten i den aktive grafiske økten før manuelle endringer. Oppgi om innebygd Wi-Fi/Bluetooth faktisk er forventet på modellen.
3. Hvis Wi-Fi-adapter vises: prøv eierens ordinære tilkobling gjennom kontrollsenteret; oppgi bare om scanning, autentisering, forbindelse og nettlesertilgang lykkes. Del ingen nettverksnavn eller nøkler.
4. Velg faktisk høyttaler/headset og volum i kontrollsenteret. Spill en ufølsom, lokal lydfil; test eventuelt mikrofon separat. Samle en ny rapport etter forsøket og noter valgt utgangstype, ikke private enhetsnavn.
5. Bluetooth testes bare hvis adaptertilstedeværelse er bekreftet. «No adapters» uten dette forblir ukjent, ikke godkjent/driverfeil.
6. For en senere, faktisk godkjent internal4-ISO: bekreft uendret UEFI/splash/topbar/kontrollsenter, fravær av normal konsollstøy og automatisk What's New, Super+Space/vanlig appsøk, `profil`/barvalg og Escape. Vanlig appsøk skal ikke fylles med profilrader; qv4l2/qvidcap kan fortsatt kjøres eksplisitt fra terminal.
7. Prøv standardbakgrunn og den brede eksisterende Wilsof-logoen på faktisk skjerm. `Fit` skal bevare proporsjoner og hele motivet. Verifiser 16:9/16:10/3:2 bare på skjermer/oppløsninger som faktisk er testet; statisk geometri er ikke fysisk aksept.
8. Installerte innlogging-/lock/unlock-porter er separate. Live er bevisst ulåst; ikke bruk live-låseadferd som PAM-aksept.

R1/R2 og sikkerhets-/ISO-portene står i utviklingsrapporten. Ingen automatisk videreutvikling eller retest startes av dette dokumentet.
