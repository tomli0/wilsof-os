# Status — Wilsof Arch-prototype

Oppdatert: 2026-10-16 UTC

## Tilgang og utplassering

- VM 113 `wilsof-arch-test` svarer med korrekt pinnet ED25519-fingeravtrykk: `SHA256:0IOuFZDTGymRZzoa5kSAO1x8FCo+ZO1khL3q/xqNAqw`.
- `root`-SSH med eksisterende ED25519-nøkkel fungerte. Årsaken til avvisning for `wilsofdev` var konkret: `/home/wilsofdev/.ssh/` og `authorized_keys` manglet. Kontoen var ikke låst, og ingen begrensende sshd-regel ble funnet.
- Den eksisterende offentlige nøkkelen ble lagt tilbake med katalog `0700`, nøkkelfil `0600` og korrekt eierskap. En ny, separat `wilsofdev` nøkkelinnlogging med kun publickey ble verifisert før utplassering.
- Commit `94ebc4a` (desktop-utplassering) er utplassert under `/opt/wilsof-os`. Installering som `wilsofdev` passerte Arch-preflight, og installerte kopier av `wilsof-search` ble sammenlignet byte-for-byte med kildeversjonen. Den senere installasjonsrettingen `e192b17` konfigurerer greetd med tuigreet/Hyprland på fremtidige rene installasjoner; den er ikke kjørt mot eksisterende VM 113.

## Brukeropplevelse og design

- Tomt skrivebord, WS-bakgrunn, charcoal `#14181E`, isblå `#86B9CE`, tynne vinduskanter og avgrenset topplinje er visuelt inspisert på VM 113 i 1280×800.
- `Super+Space` bruker nå DMS Launcher i programmets modus (`launcher toggleWith apps`), ikke Spotlight. Det gir en tydelig programliste, et fokusert søkefelt, synlig valgt treff og diskrete piltast/Enter-hint. Det unngår at Wilsof åpner QR-generatorens frie tekstresultat ved et vanlig programåpne-søk.
- `Super+I` åpner DMS Settings via IPC. Bakgrunn, tema/farger, typografi/bevegelse, Hyprland, topplinje og arbeidsområder er synlige. Brukerens DMS-innstillinger bevares ved gjentatt installasjon.
- Systemmenyen viser lås, logg ut, start på nytt, slå av, hvilemodus og start DMS på nytt. Den viser «Hold to confirm (500 ms)» før en valgt handling utføres; ingen destruktiv handling ble utført under kontrollen.
- DMS har ingen støttet launcher-widget i den installerte minimale topplinjen (`widget list` returnerte klokke, kontrollsenter, batteri og tray). Det er derfor ikke laget en falsk eller separat topplinjemeny. Launcher nås med standardbindingen; fysisk topplinjeklikk er ikke testet.

## Ekte VM-skjermbilder

- `evidence/vm113-2026-10-16-desktop.png` — tomt skrivebord/topplinje.
- `evidence/vm113-2026-10-16-launcher-apps.png` — installert Wilsof-wrapper åpner programmodus med markert Apps-filter.
- `evidence/vm113-2026-10-16-launcher-firefox.png` — Firefox er synlig og valgt som programtreff.
- `evidence/vm113-2026-10-16-settings.png` — DMS Settings og synlige kategorier.
- `evidence/vm113-2026-10-16-powermenu.png` — systemhandlinger og hold-bekreftelse.

## Begrensninger

- DMS sin oppstrømslauncher mangler norsk placeholder og viser enkelte engelske kategorier/metadata. Wilsof har ikke startet en DMS-fork for dette.
- Programmodus er testet med tomt søk og IPC-åpning. Fysisk piltast, Enter og Esc gjennom MacBook → Omarchy → Proxmox → VM er IKKE TESTET.
- Ghostty-hjelpens renderer og manifest er lokalt testet, men den aktive grafiske Ghostty-visningen ble ikke PASS-merket: en syntetisk SSH-lansering utløste Ghosttys `PostForkError`, som ikke er samme prosessvei som den reelle Hyprland-bindingen. Hjelp via fysisk `Super+F1` eller VM-testbinding er IKKE TESTET.
- Låseflate, PAM-opplåsing, fem minutters idle-lås, logout/login og reboot-persistens er IKKE TESTET. Ingen låsetest er startet mens brukeren er borte.
- Dette er funksjonell/visuell gjennomgang, ikke brukertesting med nye personer.
