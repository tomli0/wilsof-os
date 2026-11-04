# Internal3 — integrasjonsgjennomgang, 2026-10-30

## Fase A: kildegrunnlag og beslutning

Autorisasjon: separat integrasjonskandidat og betinget ett internal3-bygg/virtuell aksept. Ingen merge, release, fysisk skriving, M3/M4 eller automatiseringsstart.

- Autorisert base: `219894f1d4fc365b5e6546c2af9a146141634a1c`, faktisk remote-head for integrasjon/#27; main er separat og endres ikke.
- #38 M1: `f8709a38d4cf939c4088bbadf6eb8abf2d487a70`, implementasjon `e4aecd6f8d1259098a843a9b56d8a2a2fef00fce`, direkte på basen.
- #39 M2: `28e0a8f856eacc4ecac8e8d5ceb79d0580e36929`, stablet på M1; implementasjon `ac037b0e57ca4a7e5dac266fdacddddfbb71fbad` og rettelse `7ba3bb89322258eefbcc1f6a7b82a82444070355`.
- #40 wallpaper: `ad159b0eeb545d60912355256e9f012a1c331de1`, direkte på basen; implementasjon `d05ec2f8c11730c00145bf1bc9239bfdf4d4aaac`.
- Alle seks etterspurte PR-er (#27/#35/#36/#38/#39/#40) er OPEN/DRAFT, umerget. #35/#36 er dokumentasjonsforslag; deres innhold er allerede eksplisitt videreført i M1 der nødvendig, ikke nye produksjonsavhengigheter. Fersk `gh pr checks` bekrefter #27/#38/#39/#40; #35/#36 har ingen sjekker rapportert av denne kommandoen, ikke erklært grønn.
- Åpne #30/#31/#34/#37 er lest med kommentarer. Nyere native #31- og internal2-rapporter supersederer eldre issue-bodys. Ingen issues lukkes.

## Egen kodegjennomgang

M1s FD-baserte sti-/eierskaps-/modusvalidering, lås, JSON-kontrakt, avvisning av korrupt/fremtidig tilstand, atomisk rename og feilmeldinger er gjennomgått. M2 gjenbruker denne modulen, skiller saved/applied/error og utfører bare lesende Hyprland-inventar. Ingen ordinære vinduer flyttes/lukkes, ingen dashboard/Kanban finnes. CLEAN er fravær av profilfil; alle fire tillatte verdier beholdes. Post-rename-feil leser faktisk lagret tilstand tilbake. M4-hide/show er ikke implementert.

M2s desktop-/image-manifest distribuerer begge hjelpere og seks pluginfiler én gang. Personlig DMS-layout og eksplisitt deaktivert plugin bevares; ny installasjon får widget. Installerens disk-/passord-/chrootgrenser endres ikke. Wallpaper legger bare én feil-isolert, ikke-blokkerende post-READY-aktivering til eksisterende dropin; synkront kall ville gitt avhengighetssyklus og brukes ikke. Ingen nye pakker, tjenester eller privilegier introduseres.

Risiko: middels UI/brukerkonfigurasjon. Ingen ny uavhengig review påstås; tidligere Claude gjelder uendret installer, ikke ny profilkode. Ingen ny lisens-/asset-/upstream-pakke introduseres. Manglende overordnet prosjektlisens er fortsatt ingen tillatelse til offentlig distribusjon; dette er intern QA, ikke release.

## Eksplisitt integrasjonspolitikk

Overfør fire implementasjonsdiff-er i rekkefølgen M1, M2, M2-feilvisning, wallpaper. Behold tilhørende kontraktdokumenter/tester som tilsiktede avhengigheter, ikke tidligere rapporter/bilder. Utelat de tre kildenenes overlappende CI-grenfiltre; legg bare kandidatgrenen og dens PR-base til eksisterende workflow. Ingen øvrig workflow-/automatiseringsendring. Verifiser endelig produksjonsinnhold byte-for-byte mot source heads og kontroller manifestduplikater.

## Ressurser og grenser

Før beskyttet arbeid: ingen bygge-/QEMU-/utviklingsbarn funnet; eksisterende Hermes-gateway/dashboard er ikke Wilsof-arbeidere og røres ikke. Alle registrerte originalworktrees er rene og beholdes. Eksisterende eksklusiv prosjektlås er tatt av separat lokal prosess-supervisor (ingen AI-agent), og konkurrerende nonblocking-probe avvises. Scheduler enabled=false/paused og worker paused=true er kun lest. Ingen originalartefakt slettes eller åpnes skrivbart.

KVM finnes ikke. TCG/Nehalem skal brukes på disponibel overlay; funksjonsbevis, prosessobservasjon, screenshot og ytelse rapporteres separat. Timing/fysisk klient forblir human-check når måling ikke kan godkjennes.

OpenRouter-baseline 2026-10-30T08:31:12Z: key usage 48.328455501 USD, remaining 51.671544499 USD; account total_usage 58.472343972 USD. Administrative øktgrense 5 USD beholdes. Ingen modell-/betalingskonfigurasjon endres. Betalt arbeid krever ny pålitelig måling; ingen betalt review er bestilt. Included Codex faktisk bekreftet i sesjonsregisteret. Aggregate actual_cost mangler og er ikke en nullfaktura.

Private bevis og trygg gjenopptaking: `internal3-20261030/` i prosjektets private QA-state. Ved avbrudd: les checkpoint, supervisorstatus og eksakt prosess/diskidentitet før nye operasjoner. Ingen parallell gjest eller låsoverstyring.

Status ved dette kontrollpunktet: A gjennomgått; B/C/E/F ikke erklært bestått. Ingen ISO startet.
