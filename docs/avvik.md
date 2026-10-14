# Avviksrapport og status

## Ressurser og design

PASS: Alle tre leverte grafiske filer er kopiert uendret til `assets/` og åpnet ved inspeksjon. Bakgrunnsfilen er 1672×941, ikke native 4K; dette stemmer med kravets merknad om en oppskalert eksport. Mockupen er 1672×941. Logoen er 2172×724 RGBA.

PASS: Designretningen er fanget i prototype og Hyprland-profil: koksgrå basis, isblå aktiv kant, små hjørner, moderate mellomrom, tom bakgrunn, diskret topplinje og felles søk.

## Miljøblokkering

IKKE TESTET / blokkert: Dette miljøet har Docker, men mangler Proxmox (`qm`), libvirt (`virsh`), VirtualBox og `/dev/kvm`. Maskinen har 4 CPU-er, 7,8 GiB RAM totalt og omtrent 6,2 GiB tilgjengelig under kartleggingen. Det er derfor ikke autorisert eller teknisk mulig å opprette den foreslåtte 4 vCPU/6 GiB/40 GiB test-VM-en her. Vertens nettverk, disker, pakker, cron og eksisterende arbeidslaster er ikke endret.

IKKE TESTET: Fedora/Hyprland/DMS-pakker, Wayland-portals, D-Bus, polkit, SELinux, lyd, innlogging, standardprogrammer og alle GUI-akseptkriterier. Ingen slik påstand gjøres av dette prosjektet.

## Dokumenterte avvik fra mockup

Mockupens profilmeny er ikke implementert som global inngang. `Super+Space` åpner den avtalte samlede søkeflaten, med søkefelt øverst. Arbeidsprofiler er en senere treffgruppe og ikke en eksisterende funksjon.

## Neste nødvendige overtakelse

Gi tilgang til en isolert, autorisert Fedora-VM eller en Proxmox-API/vert med kapasitet. Utfør deretter runbooken i `docs/vm-runbook.md`, ta tre faktiske skjermbilder (tomt skrivebord, søk, innstillinger) og fyll PASS/FAIL i testplanen.
