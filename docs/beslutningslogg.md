# Beslutningslogg

## D-001 — Vanlig Fedora-VM før bootc

Status: vedtatt for prototype.

Begrunnelse: Startprompten krever fungerende skrivebord før installer/image-løp. Fedora/Hyprland/DMS-integrasjonen må demonstreres i en isolert VM før bootc innføres. Fedora bootc-dokumentasjonen beskriver bootbare containere og installer-ISO via bootc-image-builder, men dette er ikke gjennomført her.

## D-002 — DMS som shell, Wilsof som smal søkutvidelse

Status: vedtatt, integrasjon ikke testet.

Begrunnelse: DMS-dokumentasjonen beskriver støtte for Hyprland, Spotlight med apper, filer, vinduer, kalkulator og kommandoer, og `dms setup` for starterkonfigurasjon. Wilsof må eie samlet gruppering, lokalt personvern og bekreftelseskravene; å bruke rå DMS Spotlight direkte ville ikke dokumentere dem.

## D-003 — Profilmeny i referansen er ikke hovedmeny

Status: vedtatt.

Begrunnelse: Godkjent presisering overstyrer mockupens illustrative profilmeny. Profiltreff kommer først når profilfunksjonen finnes, inne i felles søk.

## Kilder kontrollert 2026-10-14

- https://danklinux.com/docs/dankmaterialshell/installation
- https://danklinux.com/docs/dankmaterialshell/compositors
- https://danklinux.com/docs/dankmaterialshell/cli-setup
- https://github.com/AvengeMedia/DankMaterialShell
- https://docs.fedoraproject.org/en-US/bootc/bare-metal/
- https://osbuild.org/docs/user-guide/image-descriptions/fedora-44

Pakkerevisjoner, Fedora-repoer og lisenser er ikke låst før VM-installasjon og må registreres der.