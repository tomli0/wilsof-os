# Internal4 — kontrollert stopp før ISO, 2026-10-30

- Status: kildeleveranse i draft #42; ingen internal4-ISO/byggforsøk. Fysisk maskinvaregodkjenning PENDING.
- Base: `4112e45998430c50711a2e51e9e7ba26f97e5b4d`, uendret internal3-gren.
- Første kandidat: `79fcb2e2fb087058df03cbd487a19095cbdbe730`; endelig kilde: `5f19e69c3cb98927dd13924ea9b6fd7a6e4946d2`.
- Fullrapport: [internal4-stabilisering](../development-reports/2026-10-30-internal4-stabilization.md). [Fysisk diagnoseplan](../qa/2026-10-30-internal4-physical-plan.md).
- Automatisert: 326 passed / 2 opt-in skips; ShellCheck/JSON/diff; push41137560781 og PR41137566959 success på eksakt kildehead. Alle21 endrede fjernblober og alle41 payload-bytes i gjesten identiske med endelig kilde.
- Runtime: én disk-only COW-gjest over internal3, faktisk vanlig passordøkt med start-hyprland/watchdog-fd, desktop uten automatisk What's New/advarsel, DMS-kaldstart og én bevisst restart; fire isolerte profiler visuelt etter frisk shell, alle fire helper-ack, fem bekreftelsesbeskyttede Power-valg og stor logo/Fit på1280×800. Syntetisk selector Down/Enter bekreftet ikke ønsket Study; sen IPC-timeout/CLEAN? bevart. Ingen ny lock/unlock-/installer-/treklient-/fysisk aksept.
- Porter: uavhengig session/provisioneringsreview og ny selector-keyboard/fokusaksept mangler. SOF-target-manifest er rettet, ikke prøvd i ny installasjon. Ingen vendorpatch eller spekulativ Wi-Fi-driver.
- R1/R2 fortsatt åpne; R3/R4 uendret; R5 eksisterende hook bevart med kildebevis, ikke ny ISO-aksept.
- Prosess: gjest exit0, offline qcow2 check0; original installert disk/firmware og seks ISO-hasher uendret. Alle15 opprinnelige remote-heads uendret. Ingen fysisk disk/USB/Proxmox, main-/leveransegrenendring, merge/release eller sletting.
- Lås: holdes kun til publisering/readback; endelig faktisk frigivelse/probe kvitteres privat og i #16. Scheduler disabled/paused og worker paused; ingen ny worker/reviewer.
- Måling22:34:28Z: 89143566336 byte/83.02141571044921875GiB ledig. OpenRouter50.380381901→50.380381901USD21:45:43Z–22:34:29Z, observert0USD (delt teller, ikke faktura). Codex included; actual-cost mangler; senere rapporteringskall kommer i tillegg. Rutingen ikke endret, ingen betalt review.
- Private bevisgruppe: `internal4-20261030` (ikke publiser råjournal, VM-disk eller syntetiske credentials).

Neste oppgave bare etter ny autorisasjon: eierens read-only fysiske internal3-diagnose. Ikke gjenoppta bygg/VM/worker automatisk. Rapport-/sluttcommit og statuslenker står i #16 og privat kvittering uten selvrefererende commit-loop.
