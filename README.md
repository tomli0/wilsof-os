# Wilsof OS — første skrivebordsprototype

Dette er et lokalt, reviewbart grunnlag for en Fedora-basert Wilsof OS-prototype. Det er ikke et ferdig OS eller en produksjonsklar distribusjon.

## Leveranse i dette revisjonssettet

- Godkjente logo-, bakgrunns- og mockupfiler under `assets/`.
- Hyprland-profil med tomt skrivebord, 1 px aktiv isblå vinduskant, kompakt topplinje via DankMaterialShell og ingen dock/ikoner.
- `Super+Space` reservert for én Wilsof-søkeflate (`wilsof-search toggle`), ikke profilmenyen fra mockupen.
- Systemd-mål og wallpaper-enhet som dokumenterer D-Bus/systemd-integrasjon.
- Arkitektur, beslutningslogg, installasjonsrunbook, testplan og avviksrapport.
- En interaktiv, lokalt åpningbar referanseprototype i `prototype/`.

## Lokal kontroll

```sh
pytest -q
python3 -m http.server 8080 -d prototype
```

Åpne deretter `http://localhost:8080` og trykk `Super+Space` (eller klikk søkeknappen) for prototypen. Dette verifiserer bare nettleserprototypen; det erstatter ikke Wayland/VM-test.

## Status

VM-opprettelse og GUI-kjøring er blokkert i dette miljøet: ingen Proxmox-/libvirt-/QEMU-tilgang og ingen `/dev/kvm`. Se `docs/avvik.md` og `docs/testplan.md` for nøyaktig teststatus og overtakelsessteg.
