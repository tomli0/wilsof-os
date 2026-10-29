# Wilsof Profile State — M1, schema v1

Status: lokal kildekomponent, ingen desktopintegrasjon. Kontrakt datert 2026-10-29.

## Grensesnitt

`bin/wilsof-profile` er ett selvstendig kjørbart Python 3-skript. Det fungerer fra repoet eller som kopi av bare denne filen; ingen modulsti, root, nettverk, D-Bus, Wayland, DMS eller Hyprland trengs. Python finnes allerede i prosjektets runtime. Ingen ny ekstern avhengighet eller bakgrunnstjeneste.

    wilsof-profile get
    wilsof-profile list
    wilsof-profile set clean
    wilsof-profile set study
    wilsof-profile set development
    wilsof-profile set everyday

I kildearbeidsområdet brukes `./bin/wilsof-profile ...`. M1 endrer ikke eksisterende desktop, installer, distribusjonsmanifest eller ekte brukertilstand. Kopiert kjørbar fil er testet uten repo og grafisk miljø. Eventuell automatisk installasjon skal gjennomgås separat i M2, ikke utføres ved profilvalg.

`list` skriver de fire navnene i rekkefølgen ovenfor, ett per linje, uten å lese tilstand. `get` og vellykket `set` skriver ett profilnavn med linjeskift. Navn er små bokstaver; DEV er kun en UI-forkortelse, ikke et CLI-alias. Ekstra/manglende argumenter og ukjente navn avvises før filoperasjoner. `-h`/`--help` er standard argparse-hjelp, ikke profilhandlinger.

| Exit | Betydning |
| --- | --- |
| 0 | Vellykket lesing/listing/lagring; også manglende fil som vanlig CLEAN-standard. |
| 1 | Tilstands-, tilgangs-, sikkerhets-, låse- eller I/O-feil. `get` skriver `clean` på stdout og tydelig `CLEAN fallback` på stderr. `set` skriver ingen suksess på stdout. |
| 2 | Ugyldig kommandolinje, bruksmelding på stderr. |

## Eksakt format og sti

Fast sti relativt til brukerens absolutte HOME: `~/.local/state/wilsof-os/profile.json`.
`XDG_STATE_HOME` overstyrer ikke den eksplisitte produktstien i M1. HOME er tillitsrot; kjør aldri med sudo eller med en annens HOME.

    {"profile": "clean", "schema_version": 1}

UTF-8 JSON-objekt, maksimalt 4096 byte. Nøyaktig to påkrevde felt, ingen ekstra eller dupliserte nøkler:

- `schema_version`: heltallet 1, ikke bool, flyttall eller streng.
- `profile`: én av `clean`, `study`, `development`, `everyday`.

Ingen tidsstempel, oppgaver, programliste, layout, vindusidentitet eller hemmelighet lagres. Ukjent fremtidig skjemaversjon avvises; ingen automatisk migrering eller nedgradering. Parsing bruker kun stdlib, ikke runtime-avhengighet på jsonschema.

## Manglende, korrupt og usikker tilstand

- Manglende fil eller manglende `.local/state/wilsof-os` gir `clean`, exit 0, ingen skriving, katalogoppretting eller feilmelding ved `get`.
- Korrupt/tom/ugyldig/for stor fil og I/O-/rettighetsfeil gir `clean`, exit 1, eksplisitt stderr. Rå filinnhold skrives ikke ut.
- En senere eksplisitt `set` validerer eksisterende fil på nytt under skrivelås og **nekter å erstatte ugyldig fil**, også ukjent versjon og usikkert mål. Originalbytes beholdes. Ingen automatisk «reparasjon», `.bak`-overskriving eller sletting.
- Bevisst gjenoppretting: stans konkurrerende profilkommandoer; undersøk feilen; arkiver filen med en ny, ikke-eksisterende eier-valgt destinasjon innen tilstandsmappen (aldri overskriv en eldre kopi). Bekreft arkivets bytes og rettigheter. Kjør så ønsket `set` på nytt. Dette er en manuell filarkivering, ikke automatisk rollback. Testene utfører denne flyten på disponible data og bekrefter at arkivet er urørt.
- Ved kun feil modus kan eier etter inspeksjon eksplisitt rette den, uten å endre data. M1 gjør ingen automatisk chmod av eksisterende `profile.json`/låsefil eller delte foreldremapper.

## Rettigheter og confinement

Alle operasjoner under HOME går gjennom katalog-FD-er med `O_NOFOLLOW`; symlenker i `.local`, `state`, `wilsof-os`, `profile.json` eller `.profile.lock` avvises. Foreldremapper må være bruker-eide og ikke gruppe-/verdensskrivbare; de endres ikke. HOME må være absolutt, uten `..`, og selve HOME-katalogen kan ikke være symlenke.

`set` oppretter manglende mapper med 0700 og innsnevrer eksisterende, sikkert bruker-eid `wilsof-os` til 0700 (eldre desktop-provisioning kan ha laget den 0755). `get` endrer ikke katalogmoduser. Profil, lås og skrivefil opprettes 0600. Eksisterende profil/lås må være bruker-eid, vanlig fil, nøyaktig 0600 og én hardlenke. FIFO/enheter/kataloger avvises før lesing; ikke-blokkerende åpning unngår FIFO-heng. Uventede eier-/modusfeil krever eierinspeksjon.

Det eneste normale filsettet skrevet av CLI er `profile.json` og `.profile.lock` i egen tilstandsmappe. Manglende `.local`/`state` kan opprettes som nødvendig sti-skjelett. Ingen andre konfigurasjoner eller oppgavedata leses/endres. Dette er ikke en sandbox mot kompromittert kode med samme UID, root, endret Python-runtime eller filsystem uten lokale POSIX-garantier.

## Atomisk lagring, avbrudd og samtidighet

1. Bruk en vedvarende `.profile.lock` med `flock(LOCK_EX)`; vent høyst 2 s med nonblocking-prober. Låsen slettes aldri, slik at ventende skrivere bruker samme inode.
2. Valider eksisterende tilstand mens låsen holdes. Ved feil: nekt overskriving.
3. Opprett unik 0600-tempfil med `O_EXCL` i samme FD-forankrede mappe; skriv komplett JSON, flush, `fsync` filen.
4. `os.replace` bytter navn atomisk innen samme mappe; deretter `fsync` mappen før suksess. Lesere ser gammel eller ny komplett fil, aldri delvis JSON.
5. Ved fangbar feil før rename beholdes tidligere profil; egen tempfil ryddes i `finally`. Ved SIGKILL/strømbrudd før rename kan en privat `.profile-*.tmp` bli igjen, men brukes aldri som tilstand, overskrives eller automatisk ryddes av neste kall. Eier kan arkivere den etter kontroll når ingen skriver er aktiv.
6. Ved feil etter rename, f.eks. katalog-`fsync`, er ny tilstand mulig og holdbarheten usikker: exit 1, tydelig melding, ingen falsk «gammel fil bevart»/rollback-påstand. Les med `get` og undersøk lagringsfeilen før ny handling. Full garanti mot maskinvare-/strøm-/filsystemfeil hevdes ikke.

Operasjonene er serialiserbare: **siste vellykkede commit i låsrekkefølgen vinner**. Samtidig starttid bestemmer ikke rekkefølgen; ingen profil eller PID prioriteres. Testen holder første skriver før rename, starter en reell konkurrent og slipper deretter låsen: sluttprofilen er deterministisk `development`. En egen stresskontroll kjører tolv konkurrerende skrivere med aktiv rå-JSON-leser. Ingen lost-update-modifikasjon er nødvendig fordi `set` erstatter ett komplett profilvalg, ikke en read-modify-write-datastruktur.

## Forhold til CLEAN og senere milepæler

M1 lagrer bare ønsket profil, ikke faktisk GUI-synlighet. Det finnes ingen dashboard-, launcher-, bar- eller compositorhandling i koden. Den normative CLEAN-/vinduskontrakten finnes i [UX §2.2 og §2.6](WILSOF_UX_SPECIFICATION.md): ingen synlige dashboardflater, ingen ny dashboardprosess ved CLEAN, ingen automatisk flytting/lukking av øvrige brukerprogrammer, ingen oppgaveendring. M2/M4 må implementere/verifisere dette før de påstår at GUI-profilen er anvendt.

## Bevis og videre grenser

De tre `tests/test_profile*.py`-filene kjøres av eksisterende pytest-jobb. De dekker manglende/gyldig/ugyldig tilstand, alle profiler, strenge argumenter/skjema, feilinjeksjon, rename-/sync-rekkefølge, reell SIGKILL og konkurranse, rettigheter/lenker/FIFO, uendret brukerdata og en selvstendig kopiert CLI. Ingen VM er nødvendig for denne kontrakten. Fysisk klient, dashboardets skjuling, DMS-plugin og ISO-integrasjon er ikke testet eller levert i M1.

Teknisk primærreferanse: [Python os.replace, dir_fd og fsync](https://docs.python.org/3.12/library/os.html#os.replace). Egne lokale bevis og eksakt CI-kvittering er lenket fra M1-utviklingsrapporten.
