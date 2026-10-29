# Wilsof OS — UX-spesifikasjon

Status: planleggingsdokument (ingen implementering). Dato: 2026-10-29 UTC. Kildegrunnlag som i produktvisjonen.[52]
Designutgangspunkt: eksisterende Wilsof Charcoal-tema og gjeldende binds/hjelp-manifest i `config/`.[52]

## 1. Opplevelsesprinsipper

1. **Tastatur først, mus mulig.** Alle primærflater (launcher, profilvelger, Quick Settings, dashboard) skal kunne betjenes fullstendig med tastatur; Esc avbryter alltid uten effekt.
2. **Én ting per snarvei, ingen skjulte særregler.** Wilsof beholdes som en tynn bind-oversikt over DMS-genererte binds (eksisterende `wilsof.lua`-praksis fjerner kun dokumenterte konflikter).[52]
3. **Forutsigbarheter kan testes.** Hver interaksjon har akseptansekriterier som kan verifiseres i VM (og fysisk der CONTRIBUTING.md krever konsoll).[51]
4. **Ingen systemkritisk UI-komponent.** DMS kan krasje uten at Hyprland/innlogging feiler; Wilsof-dashboard er et valgfritt lag på toppen.[53]

## 2. Wilsof-profiler

### 2.1 Definisjon

En profil er en navngitt tilstand med tre deler:

1. **Arbeidsområde 1-oppsett** (CLEAN: tomt; STUDY/DEV/EVERYDAY: dashboard-instans på arbeidsområde 1).
2. **Anbefalt startsett** (appinnstillinger) som brukes bare ved eksplisitt "Åpne …"-handling fra dashboardet — aldri automatisk autostart.
3. **En profilmarkør** i lokal tilstandsfila (ingen egen brukerkonto, ingen egen DMS-konfigurasjon; personlig `settings.json` berøres ikke, jf. dagens bevaringspraksis).[52]

### 2.2 CLEAN (standard)

- Alle arbeidsområder 1–9 starter helt tomme; ingen dashboardprosess startes; ingen autostart av arbeidsapper.
- Top bar, launcher og vindushåndtering er identiske med andre profiler.
- Akseptansekriterium M1: `pgrep` viser ingen Wilsof-dashboardprosess; arbeidsområde 1 er tomt; Super+Space/innstillinger fungerer.
- CLEAN fungerer uavhengig av om noensinne en annen profil er brukt (tilstandsfila tåler fravær og gjenopprettes til CLEAN).

### 2.3 STUDY

- Arbeidsområde 1: Study Dashboard med Kanban (To Do / In Progress / Done) per fag eller prosjekt, fristfelt per oppgave.
- Arbeidsområder 2+: anbefalte appar (PDF-leser `papers`, Firefox, Nautilus, teksteditor) tilgjengelige via launcher; ingen automatisk start.
- Dashboardet starter kun når brukeren bytter til STUDY (valgfri komponent; se arkitekturdokumentet).

### 2.4 DEVELOPMENT (DEV)

- Arbeidsområde 1: Development Dashboard med prosjekter (lokal mappereferanse), oppgaver og fremdrift (kolonnesummer/ferdigprosent).
- Arbeidsområder 2+: Ghostty, editor (gnome-text-editor; VS Code vurderes utenfor MVP), Firefox, Nautilus.
- Brukerdefinerte prosjektmapper registreres i dashboardet (banneverdi), aldri som globale systeminnstillinger.

### 2.5 EVERYDAY

- Arbeidsområde 1: Everyday Dashboard med én enkel personlig oppgaveliste (samme Kanban-kolonner, ett standardprosjekt).
- Arbeidsområder 2+: vanlige apper (Firefox, Nautilus, VLC, Text Editor — alle inngår allerede i pakkesettet).[52]

### 2.6 Regler for profilbytte med åpne vinduer

1. **Ingen app lukkes noensinne.** Eksisterende vinduer forblir på sine arbeidsområder.
2. **Byttet er en layoutoperasjon:** valgt profil lagres; hvis målprofilen har dashboard på arbeidsområde 1 og området er tomt, startes dashboard-vinduet; hvis området er opptatt, vises dashboardet i stedet som launcher-handling eller brukeren bytter til et ledig område — aldri tvungen fortrenging.
3. **Hvis en tidligere profil sitt dashboard fortsatt kjører**, blir det stående; brukeren kan lukke det selv. Ingen bakgrunnsnedstenging.
4. **Angremulighet:** byttet vises i topbaren umiddelbart; nytt bytte tilbake er alltid en lokal operasjon uten datatap.
5. **Krasj-uavhengighet:** hvis tilstandsfila er korrupt, faller systemet tilbake til CLEAN og viser én lesbar melding via launcher-hjelpen — innlogging påvirkes aldri.
- Akseptansekriterium M2: bytt CLEAN→STUDY→CLEAN med 3 åpne vinduer: vinduene beholdes (samme PID-er), ingen dataendring i dashboard-DB, topbar-profilnavn oppdateres <2 s.

### 2.7 Datagarantier

- Oppgavedata lagres kun lokalt (`~/.local/share/wilsof-os/dashboard/`), offline-first; ingen konto, ingen backend, ingen obligatorisk bakgrunnstjeneste.
- Profiltilstand og oppgavedata er separate filer; profilbytte kan derfor ikke påvirke oppgavedata.
- Eksport/sikkerhetskopi: eksplisitt eksport til JSON via dashboardet + dokumentert manuell kopi av DB-fila (regler i arkitekturdokumentet §7).

## 3. Vindushåndtering (Hyprland beholdes)

### 3.1 Eksisterende funksjoner som dekker behovet (ingen egne mekanismer)

- Automatisk tiling: Hyprland `dwindle`-layout er allerede valgt i DMS-generert config og Wilsof-arven har `preserve_split`-semantikk via DMS-basen; DMS genererer `dms/layout.lua` som Wilsof overstyrer med egne gaps/rounding.[52][46]
- Fokus/flytting/størrelse: Wilsof-bindene Super+piler/Shift+piler/Ctrl+piler er implementert og dokumentert i `config/wilsof-shortcuts.json` og `wilsof.lua`.[52]
- Floating/fullskjerm: `togglefloating` (Super+Shift+Space) og `fullscreen` (Super+F) — Hyprland-dispatchere uten egne mekanismer.[44]
- Dialoger: Hyprland window rules støtter `match = { modal = true }` og `float`/`center`-effekter; DMS float-regler finnes allerede for egne modalvinduer.[45] Wilsof skal kun legge til én generisk modal/Dialog-regel (`float=true, center=true`) — ikke per-app-liste.
- Flere skjermer: DMS genererer per-output monitor-regler (`dms/outputs.lua`, `hl.monitor` preferred/auto/auto);[52] bar viser på alle skjermer via `screenPreferences: ["all"]` i settings-malen.[52]
- Konsistent navigasjon: samme binds i alle profiler fordi binds er globale og profiluavhengige.

### 3.2 Kun én ny innstillingsgruppe

Wilsof skal sette én dokumentert standard: `gaps_in/gaps_out/border/rounding` (finnes i `wilsof.lua`)[52] plén én modal-regel. Ingen flere særregler; ingen eigen tiling-motor; ingen workspace-rule per profil.

### 3.3 Hurtigtastkart (status quo beholdes; kun profilbytte-aksjon legges til launcher)

Eksisterende manifest er kildesannhet (`config/wilsof-shortcuts.json`): Super+Space launcher, Super+L lås, Super+I innstillinger, Super+F1 hjelp, Super+1–9 arbeidsområder (+Shift flytt), Super+piler fokus/flytt/resize, Super+Q lukk, Super+F fullskjerm, Super+Shift+Space floating.[52] Nye binds unngås; profilbytte skjer via launcher (Super+Space → "Profil").

## 4. Wilsof Launcher (Super+Space)

### 4.1 Eksisterende grunnlag

`wilsof-search toggle` er en argumentvalidert bro til `dms ipc call spotlight toggle` (arkitekturdok. påpeker at VM113-observasjonen brukte `launcher toggleWith apps`-variant; nøyaktig modus verifiseres i M3).[52] DMS Spotlight gir apps-, fil-, emoji-, vindu-, kalkulator- og kommandoresulter oppstrøm, samt pluginutvidelse med triggere.[1][50]

### 4.2 Krav som kan møtes med eksisterende utvidelsesflate (ingen ny launcher)

- **Søke og starte apper:** allerede dekket (app-entry verifisert; filer/vinduer krever dsearch/AUR og er ikke aktivert — Wilsof gjør ingen universal search-påstand, jf. eksisterende beslutning).[52]
- **Velge profiler:** implementeres som en **DMS launcher-plugin** (type `launcher`, `trigger: ""` eller f.eks. "profil") som viser CLEAN/STUDY/DEV/EVERYDAY som elementer og kaller `wilsof-profile set <navn>` via `exec:`-handling. Plugin-API er dokumentert (`getItems`/`executeItem`, `categories`, ikon, comment).[2][50]
- **Små systemhandlinger:** samme plugin kan tilby et lite kuratert sett: Lås, Omstart (med DMS-bekreftelsesdialog som allerede finnes for destruktive handlinger),[52] Systemoppdatering (åpner Quick Settings/oppdateringsflate). Ikke en kommandoplattform.
- **Finne hurtigtaster:** Super+F1-hjelpesiden (eksisterende, manifestdrevet) er oppføringen; launcher-elementet "Hurtigtaster" åpner den.[52]
- **Åpne innstillinger:** Super+I finnes; launcher-element "Innstillinger" kaller `dms ipc call settings open`.[49]

### 4.3 UX-regler

- Tastaturnavigasjon: DMS Spotlight har innebygd pil/Enter/Esc-navigasjon (oppstrøms egenskap).[1] Kravet er derfor konfigurasjon, ikke utvikling.
- Respons: ingen Wilsof-plugin-kall skal blokkere; pluginen holder alt i minne/leser én tilstandsfil ved åpning.
- Enkelhet: maks 4 profiloppføringer + maks 6 systemoppføringer; ingen kategoribombe.

## 5. Wilsof Top Bar

### 5.1 Struktur (gjenbruk av DMS bar-widgets; ingen ny bar)

| Felt | Innhold | Implementering |
| --- | --- | --- |
| VENSTRE | Aktiv profil (CLEAN/STUDY/DEV/EVERYDAY) → klikk åpner profilvelger; arbeidsområder 1–9 | Profil: **liten DMS bar-widget-plugin** som leser tilstandsfila og viser navn; klikk kaller `wilsof-profile select` (åpner launcher-plugin-filter). Arbeidsområder: eksisterende `workspaceSwitcher`-widget (allerede i settings-malen).[52][3] |
| MIDTEN | Klokke og dato | Eksisterende `clock`-widget (malen).[52] |
| HØYRE | Nettverk, Bluetooth, lyd, batteri når relevant, Quick Settings-knapp | DMS har alle widgets (`network`, `bluetooth`, `audio`, `battery`, `controlCenterButton`); malen har i dag `systemTray + battery + controlCenterButton` — utvides med de dekkende DMS-widgets som konfigurasjon, ikke kode.[3][52] |

Top bar er identisk i alle profiler (profilnavnet er eneste variable feltet). Batteri skjules automatisk når maskinvaren ikke støtter det (DMS-widgetens betingede visning; på test-VM er batteri fraværende, jf. eksisterende avviksdokumentasjon).[52]

### 5.2 Quick Settings (Control Center)

DMS Control Center har allerede Wi-Fi (NetworkDetail), Bluetooth, lyd med enhetsvalg (AudioOutputDetail/AudioPortSelector), lysstyrke (BrightnessDetail), batteri (BatteryDetail), Do-not-disturb, strømprofiler og session/power-handlinger (lås/logg ut/omstart/avslutt) via PowerMenu med 500 ms hold-bekreftelse for destruktive handlinger.[52][3] Kravet er konfigurasjon av hvilke tiles som vises, ikke noen ny kontrollsentertjeneste. Konkret: behold DMS-standardtiles; fjern ingen; Wilsof skal ikke bygge egne tiles i MVP.

## 6. Wilsof Dashboard (UX)

- Én applikasjon, fire moduser (CLEAN = ikke kjørende; STUDY/DEV/EVERYDAY = samme Kanban-flate med modusspesifikk startinnhold).
- Tre kolonner: To Do / In Progress / Done; dra-eller-tastaturrekkeflytting (Left/Right + Enter); ny oppgave med N; rediger M; fullfør med Enter på valgt kort; slett Delete.
- Prosjekt-/fagsvelger øverst; EVERYDAY har ett ikke-slettbart standardprosjekt; STUDY/DEV oppretter/sletter prosjekter fritt.
- Fristfelt (valgfri dato); oversiktslinje viser antall per kolonne.
- Fil-meny: Eksporter JSON, Sikkerhetskopi nå, Åpne datamappe; dataregler i arkitekturdokumentet §7.
- Failsafe: dashboardet kan avsluttes/kastes uten effekt på Hyprland, bar eller innlogging (ingens systemd-avhengighet peker mot det; det starter ikke ved `wilsof-session.target`).

## 7. Visuell identitet — Wilsof Charcoal-designsystem

### 7.1 Eksisterende grunnlag

- DMS custom-temafil `wilsof-theme.json`: primær isblå `#86B9CE`, bakgrunn/surface `#14181E`, tekst `#E7EEF2`, outline `#3A424B`, fullstendig Material-tokenliste (surfaceContainer-trapp, error/warning/info);[52] Matugen er deaktivert via DMS-dropin (`DMS_DISABLE_MATUGEN=1`) så bakgrunn aldri kan overstyre paletten.[52]
- Hyprland-dekorasjon: 1px aktiv isblå border, inactive `#3A424B`, gaps 8/10, rounding 6, ingen skygge, inactive opacity 0.96 (`wilsof.lua`).[52]
- Låseskjerm (`hyprlock.conf`): forhåndsrådig låsebakgrunn-asset, stor WS-logo, klokke 64 px Inter Variable, dato 18 px, inputfelt 360×54 med isblå ramme og norske tekster ("Skriv passord for å låse opp", "Feil passord", "Esc tømmer feltet").[52]
- Lås/idle-policy: `wilsof-lock`-wrapper forhindrer duplikat Hyprlock; Hypridle 5 min → lås, før suspend;[52] patchet hypridle-0.1.8-2.1-pakke med verifiserte SHA256.[53]
- Ikoner: Adwaita; typografi: Inter Variable (tekst) + JetBrains Mono Nerd (terminal) — begge inngår i pakkesettet.[52]
- Bakgrunn: godkjent asset "Mørk geometrisk bakgrunn med isblått WS-monogram.png" + lock background med proveniensfil i repoet.[52]

### 7.2 Funn: hvorfor internal2 viste upstream DMS-bakgrunn (dokumentert, ingen ISO-endring)

Direkte journalbevis fra den bevarte internal2-evidensen: ved kald start ble den første DMS-UI-prosessen drept med SIGKILL (status 137, rotårsak/killer fortsatt ukjent — R1), og `wilsof-wallpaper.service: Job wilsof-wallpaper.service/start failed with result 'dependency'` fordi enheten krever `dms.service`; den avhengige oneshot-en startet aldri på nytt etter DMS' automatiske restart, og ingen ny manuell start ble utført i akseptøkten.[53] Da DMS kom opp uten noen satt `wallpaperPath` i sin (nyopprettede) `dms/session.json`, ble oppstrøms standard-artwork vist i stedet for den Wilsof-eide bakgrunnen (R5, kosmetisk).[53] Medvirkende faktor: enheten har ingen `Restart`-politikk og ingen retry etter DMS-restart. **Utbedring er planlagt (M5), ikke utført: ISO-en forblir uendret.**

### 7.3 Designprinsipper (målbare)

1. **Tokens, ikke hexkoder i UI-kode.** Alle Wilsof-eide flater (dashboard, launcher-plugin-tekst, profilwidget) leser Charcoal-tokenne fra én delt definisjon.
2. **Kontrast ≥ 4.5:1** for all normal tekst på surface-bakgrunn (isblå/kul hvit på `#14181E` oppfyller dette; verifiseres programmatisk i design-review).
3. **Én aksecentfarge** (isblå) for aktiv/interaktiv; outline for passive grenser; ingen dekorative farger.
4. **Konsistens:** samme radius (6px), gaps-skala (4/8/10) og 1px-border på tvers av dashboard, launcher og bar-modul.
5. **Lesbarhet før stemning:** ingen blur i låseskjerm-kritiske flater, ingen tekst under 14 px, skala for HiDPI via Hyprland monitor-scale (DMS-outputs preferred/auto/auto dekker dette).[52]
6. **Branding kun der eieren ser den:** WS-monogram i låseskjerm og bakgrunn; ingen logo i topbar (plass til arbeidsflyt).

### 7.4 Akseptansekriterier (per flate)

| Flate | Kriterium |
| --- | --- |
| Top bar | Eksisterer på alle skjermer; feltene venstre/midt/høyre følger §5.1; profilnavn oppdateres ≤2 s etter bytte; ingen Wilsof-spesifikke farger hardkodet utenfor tema. |
| Launcher | Åpner fokusert ved Super+Space ≤1 s i ren økt (VM-måling); Esc lukker uten sideeffekt; profiloppføringer viser aktiv markering. |
| Dashboard | Charcoal-tokens i alle komponenter; fokusmarkering synlig 2px isblå; kolonnenavn/antall lesbare 14 px+. |
| Vindusdekorasjon | Aktiv 1px isblå; inaktiv 1px `#3A424B`; gaps/rounding per `wilsof.lua` (uendret). |
| Quick Settings | Kun DMS-standardtiles; strømhandlinger krever DMS-bekreftelse (500 ms hold). |
| Låseskjerm | Eksisterende hyprlock-konfig (uendret) gjengir WS-logo, klokke, felt; feil passord beholder flate (verifisert i internal2, port 11–12).[53] |
| Bakgrunn | Godkjent asset vises etter M5-utbedring i alle profiler, også etter DMS-omstart; `dms ipc call wallpaper get` bekrefter samme sti. |
| Typografi/ikoner | Inter Variable/JetBrains Mono/Adwaita iht. pakkesett; ingen ekstra fontavhengighet. |

## Sources

- [1] https://raw.githubusercontent.com/duxlabs-dev/dux-shell/v2.0.0/README.md
- [2] https://raw.githubusercontent.com/duxlabs-dev/dux-shell/v2.0.0/.agents/skills/dms-plugin-dev/references/launcher-plugin-guide.md
- [3] https://raw.githubusercontent.com/duxlabs-dev/dux-shell/v2.0.0/.agents/skills/dms-plugin-dev/references/widget-plugin-guide.md
- [44] https://raw.githubusercontent.com/hyprwm/hyprland-wiki/e9b1f8f56bc1e74d3f4d8cb64b55147152658fe2/content/configuring/core/dispatchers.md
- [45] https://raw.githubusercontent.com/hyprwm/hyprland-wiki/e9b1f8f56bc1e74d3f4d8cb64b55147152658fe2/content/configuring/core/rules/window-rules.md
- [46] https://raw.githubusercontent.com/hyprwm/hyprland-wiki/e9b1f8f56bc1e74d3f4d8cb64b55147152658fe2/content/configuring/layouts/dwindle-layout.md
- [49] https://raw.githubusercontent.com/duxlabs-dev/dux-docs/6bf44c0c03bd4c3a917abeaa6b366fda741c2f76/versioned_docs/version-2.0/dms/keybinds-ipc.mdx
- [50] https://raw.githubusercontent.com/duxlabs-dev/dux-docs/6bf44c0c03bd4c3a917abeaa6b366fda741c2f76/versioned_docs/version-2.0/dms/plugin-development.mdx
- [51] https://github.com/tomli0/wilsof-os/blob/a78d88790754886750bb1a5f93dd33cb257cc47e/docs/ENGINEERING_STANDARDS.md
- [52] https://github.com/tomli0/wilsof-os/tree/219894f1d4fc365b5e6546c2af9a146141634a1c
- [53] https://github.com/tomli0/wilsof-os/blob/219894f1d4fc365b5e6546c2af9a146141634a1c/docs/development-reports/2026-10-28-internal2-acceptance.md
