# Wilsof OS — produktvisjon

Status: produktplan fra PR #36, presisert for M1 2026-10-29 UTC. Kun profil-CLI/tilstand implementeres i M1; øvrige funksjoner er planlagte, ikke levert.
Autorisert kildegrunnlag: `integration/internal-iso-20261026` @ `219894f1d4fc365b5e6546c2af9a146141634a1c` (samme produksjonskode som internal2-ISO-kilden),[52] med Engineering Standards fra draft-PR #35 @ `a78d887`.[51]
M1-kildekontroll: PR #36 skrev `2198989f1d4fc365b5e6546c2af9a146141634a1c`; dette tokenet er ikke en gyldig 40-tegns Git SHA-1. Korrekt base ovenfor er verifisert separat mot faktisk Git/remote, ikke utledet ved å «reparere» tokenet.
Gjeldende stabilitetsgrunnlag: internal2 virtuell funksjonsaksept med åpne merknader R1–R5; ikke fysisk verifisert, ingen merge/release.[53]

## 1. Visjon

**A desktop built around your workflow.**

Wilsof OS er en minimalistisk Arch-basert Wayland-skrivebordsplattform bygget på Hyprland og Dux Shell (DMS),[1] hvor arbeidsflyten — ikke funksjonsantallet — styrer oppsettet. Systemet starter tomt og stille (CLEAN), og brukeren bygger bevisst videre med én av fire definerte arbeidsflytprofiler.

Fire holdninger som styrer alle produktvalg:

1. **Få ting, godt integrert.** Hver funksjon må ha et konkret behov ingen eksisterende komponent dekker (jf. Engineering Standards §8: nye avhengigheter skal ha konkret behov og vurdering).[51]
2. **En kilde til sannhet per opplevelse.** Én launcher (Super+Space), én top bar, ett hurtigtastkart — Wilsof har allerede én delt manifest for snarveier og dette beholdes.[52]
3. **Gjenbruk før egne mekanismer.** DMS eier allerede bar, launcher, Control Center, oppdateringsbakende og IPC;[1][48][49] Hyprland eier tiling, vindusregler og monitorhåndtering.[44][45] Wilsof overstyrer, bygger ikke avkom.
4. **Bevis, ikke påstand.** Modenhetsnivåene implementert/testet/integrert/ISO-verifisert/fysisk verifisert holdes alltid atskilt.[51]

## 2. Målgruppe og behov

- Hovedbruker: eier selv (student/utvikler/hverdagsbruk på bærbar PC).
- Sekundær: en ny Linux-bruker som skal kunne sette opp et forutsigbart skrivebord uten å redigere konfigurasjonsfiler.
- Kjerneproblemet Wilsof løser: generiske tiling-setups gir et blankt lerret uten struktur, mens tunge skrivebord (GNOME/KDE) skjuler arbeidsflyten bak menyer. Wilsof gir et lite, forklart sett med arbeidsflater.

## 3. Produktsjikt

| Sjikt | Eier | Rolle |
| --- | --- | --- |
| Base | Arch Linux + systemd-boot + greetd | Eksisterende installer og oppstartsprosess; uendret produktstrategisk omfang.[52] |
| Compositor | Hyprland 0.57 (BSD-3-Clause, aktiv)[56] | Tiling, vindusregler, monitorer, IPC.[44][45] |
| Shell | Dux Shell/DMS 2.0 (MIT, aktiv)[54] | Bar, Spotlight-launcher, Control Center (Quick Settings), notifikasjoner, systemoppdaterings-UI/-bakende.[1][48] |
| Wilsof-lag | Dette repoet | Tema (Wilsof Charcoal), hurtigtaster, hjelp, lås/idle, profiltilstand, Kanban-dashboard, wallpaper-gjenoppretting. Allerede implementert i dag: tema, binds, hjelp, lås, idle, wallpaper-service.[52] |

Wilsofs identitet ligger i sjikt 4: kuraterte valg, norsk-first påstand, profilbasert arbeidsflyt og en gjennomført visuell identitet — ikke i å omimplementere shell eller compositor.

## 4. De fire profilene (sammendrag; detaljer i UX-spesifikasjonen)

- **CLEAN** — standard ved første oppstart: ingen synlige Wilsof-dashboardflater, ingen ny dashboardprosess. Brukerens eksisterende vinduer og arbeid beholdes. En tidligere dashboardinstans kan leve skjult; se UX §2.6. Første oppstart uten brukerprogrammer er tom, ikke en regel om å tømme arbeidsområder.
- **STUDY** — arbeidsområde 1 med Study Dashboard (Kanban To Do/In Progress/Done knyttet til fag), arbeidsområder 2+ for skolearbeid.
- **DEVELOPMENT** — arbeidsområde 1 med Development Dashboard (prosjekter/oppgaver/fremdrift), arbeidsområder 2+ for editor/terminal/dokumentasjon.
- **EVERYDAY** — arbeidsområde 1 med enkel personlig oppgaveliste, arbeidsområder 2+ for vanlige apper.

Felles invariant: én Linux-bruker, ett skrivebordsmiljø; profilbytte endrer bare layout/tilstand, aldri eierskap eller kjørende apper. Data lagres lokalt; ingen synk, kalender eller AI i første versjon.

## 5. Ikke-mål (første versjon)

- Ingen ny egen pakkebeholder, kontrollsentertjeneste, kommandoplattform eller AI-integrasjon.
- Ingen snapshots/rollback uten verifiserbar teknisk løsning (ingen Btrfs/Limine-betinget funksjon inngår i Wilsofs kontrakt; se arkitekturdokumentet).
- Ingen utvidelse av "universal search" utover det eksisterende, dokumenterte nivået (app-entry via DMS Spotlight; fil-/vindu-/settings-søk er ikke verifisert og skal ikke markedsføres).[52]
- Ingen endring av installer/ISO-omfang som del av produktutviklingen; internal2-stabilitetssportene forblir et separat spor (jfr. #27/#34/#16).[53]

## 6. Suksesskriterier

1. En bruker kan fra første oppstart åpne launcher, finne apper, bytte arbeidsområde og låse skjermen uten dokumentasjon (Super+Space / Super+1–9 / Super+L).
2. Profilbytte er forutsigbart: ingen apps lukkes, ingen data går tapt, oppsettet etter bytte er deterministisk (akseptansekriterier i UX-dokumentet).
3. Dashboardprosessen kan drepes uten at bar, Hyprland eller innlogging påvirkes (akseptansetest M4).
4. Oppdateringstilbudet bruker kun pacman-bakenden (`pacman -Syu`-semantikk via DMS), avviser delvis oppgradering og presenterer omstartsbehov.[48]
5. Alle Wilsof-eide flater følger Wilsof Charcoal-designsystemet med dokumenterte akseptansekriterier (visuell identitet-dokumentet i UX-spesifikasjonen).

## 7. Forhold til eksisterende dokumentasjon

Dette dokumentet definerer produktretningen. Det utfyller, og erstatter ikke: `docs/arkitektur.md` (nåværende tekniske arkitektur), `docs/ENGINEERING_STANDARDS.md` (prosesskrav),[51] `docs/security.md` (trusselmodell), `docs/installer-*.md` og `docs/internal-test-runbook.md` (installer- og testautoritet). Duplisering er bevisst unngått; teknisk kartlegging ligger i WILSOF_TECHNICAL_ARCHITECTURE.md og detaljert UX i WILSOF_UX_SPECIFICATION.md.

## Sources

- [1] https://raw.githubusercontent.com/duxlabs-dev/dux-shell/v2.0.0/README.md
- [44] https://raw.githubusercontent.com/hyprwm/hyprland-wiki/e9b1f8f56bc1e74d3f4d8cb64b55147152658fe2/content/configuring/core/dispatchers.md
- [45] https://raw.githubusercontent.com/hyprwm/hyprland-wiki/e9b1f8f56bc1e74d3f4d8cb64b55147152658fe2/content/configuring/core/rules/window-rules.md
- [48] https://raw.githubusercontent.com/duxlabs-dev/dux-docs/6bf44c0c03bd4c3a917abeaa6b366fda741c2f76/versioned_docs/version-2.0/dms/cli-system-updater.mdx
- [49] https://raw.githubusercontent.com/duxlabs-dev/dux-docs/6bf44c0c03bd4c3a917abeaa6b366fda741c2f76/versioned_docs/version-2.0/dms/keybinds-ipc.mdx
- [51] https://github.com/tomli0/wilsof-os/blob/a78d88790754886750bb1a5f93dd33cb257cc47e/docs/ENGINEERING_STANDARDS.md
- [52] https://github.com/tomli0/wilsof-os/tree/219894f1d4fc365b5e6546c2af9a146141634a1c
- [53] https://github.com/tomli0/wilsof-os/blob/219894f1d4fc365b5e6546c2af9a146141634a1c/docs/development-reports/2026-10-28-internal2-acceptance.md
- [54] https://github.com/duxlabs-dev/dux-shell/releases/tag/v2.0.0
- [56] https://github.com/hyprwm/Hyprland/releases/tag/v0.57.0
