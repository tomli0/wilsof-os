# Arkitektur — første prototype

## Valgt retning

Fedora i en dedikert VM, Hyprland som kompositor og DankMaterialShell (DMS) som eksisterende Wayland-shell. DMS dekker topplinje, varsler, låsing og utvider Spotlight med programmer, `dsearch`-filer, vinduer, kalkulator og kommandoer. Wilsof beholder én inngang gjennom en smal `wilsof-search`-utvidelse; den skal aggregere og gruppere alle treff i stedet for å åpne DMS sin standardmeny direkte.

`Super+Space` → `wilsof-search toggle` → DMS Spotlight/utvidelse → lokale leverandører: desktop entries, avgrenset filindeks, Hyprland-vinduer, innstillinger og eksplisitt tillatte systemhandlinger. Ingen vilkårlig shell-kommando eller nett-søk.

## Sikkerhetsgrenser

- SELinux beholdes enforcing; problemer analyseres med avc-meldinger og presise policy-tiltak, aldri global deaktivering.
- `loginctl lock-session` er direkte; omstart, avslutning og utlogging får en tastaturstyrt bekreftelsesdialog.
- Filindeks må avgrenses til brukerens eksplisitt valgte mapper og følge personvern-/ressursgrense før den aktiveres.
- Systemhandlinger mappes fra norske og engelske aliaser til en fast handlingstabell.

## Sesjon og tjenester

Hyprland eksporterer miljøet til brukerens systemd- og D-Bus-sesjon og starter `wilsof-session.target`. Målet drar inn DMS og den godkjente bakgrunnen. Dette følger DMS-dokumentasjonen for Hyprland; faktisk end-to-end-test er fortsatt ikke utført.

## Pakkestrategi

Systemet: Fedora-pakker for Hyprland, portals, PipeWire/WirePlumber, polkit og kjerneintegrasjon. DMS installeres fra dokumentert aktuell kilde etter lisens- og versjonskontroll. Brukerprogrammer primært Flatpak. Standardsettet er Firefox, Ghostty, Nautilus, GNOME Text Editor, Papers, Loupe og VLC; desktop-id-er og oppstart skal måles i VM før de låses.

Langsiktig: bootc-container som kilde til sannhet, med image-bygg og rollback etter at skrivebordet fungerer i vanlig Fedora-VM. ISO/installer er ikke i scope nå.
