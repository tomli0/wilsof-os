# Internal4 completion — safe physical diagnostics from internal3

Physical Wi-Fi, playback/microphone and Bluetooth remain PENDING. This procedure does not install a driver, change a radio, start an installer, write an ISO to USB or modify an internal disk.

## 1. Obtain the exact reviewed script on a machine with internet

Internal3 does NOT contain `wilsof-hardware-report`. Use this existing reviewed revision; the script is byte-identical in the completion candidate.

Run one command per step:

    curl --fail --location --proto '=https' --tlsv1.2 --output wilsof-hardware-report https://raw.githubusercontent.com/tomli0/wilsof-os/418a4ff8f5e50d79132aeb6a23d8064e5889c162/bin/wilsof-hardware-report

    printf '%s\n' 'b8f9148b968ee091b3ae371817888f8910fa7ee005617e279b12f16ad45a54ec  wilsof-hardware-report' | sha256sum --check

The second command must say `wilsof-hardware-report: OK`. Otherwise stop; do not execute it. A checksum checks these exact bytes, not the trustworthiness of an arbitrary replacement download.

If Wi-Fi is unavailable on the test PC, transfer this small file through an already available data medium or ordinary file-transfer route. Do not format a device or recreate the boot USB. Using the live file manager, save the reviewed file to `/home/live/Downloads/wilsof-hardware-report`. This is an ordinary file copy, not a disk/driver installation. No internet is required to run the script.

## 2. Boot the unchanged internal3 live environment

Expected ISO: `wilsof-internal-2026.10.30-internal3-x86_64.iso`, 2548035584 bytes, SHA256 `b3cf9726f2d55a7a0398aadeb6327a839a5607a7dd7f5a10b9a862a5c1936dd1`.

Use the ordinary live desktop. Do not start Install Wilsof. Live evaluation is intentionally unlocked. Do not put private files or account secrets into the live environment. Internal4 has not been built.

As the ordinary live user, WITHOUT sudo:

    cd /home/live/Downloads

    printf '%s\n' 'b8f9148b968ee091b3ae371817888f8910fa7ee005617e279b12f16ad45a54ec  wilsof-hardware-report' | sha256sum --check

    python3 /home/live/Downloads/wilsof-hardware-report > /home/live/wilsof-hardware-report-before.json

    python3 -m json.tool /home/live/wilsof-hardware-report-before.json

These commands create only the selected JSON file in the live home. The probe does not download, change configuration, upload anything, enable Bluetooth or unmute audio. Audio status queries can socket-activate existing PipeWire/Pulse services; this is disclosed and does not change activation policy.

## 3. Review before sharing

Read the complete JSON output locally. It is allowlisted: numerical PCI/USB IDs and driver names, rfkill blocked flags, package/unit state, network type/state, anonymized audio sink/source state and counts/filenames for firmware errors. SSID, connection names, MAC/IP addresses, credentials, audio streams/media titles, USB serials and raw journals are not intentionally exported. `unavailable` means not observed, not a clean result. Do not add private identifiers in an issue comment.

Keep the JSON private until you have reviewed it. Share only that reviewed JSON and these short observations:

- PC model/family without serial number; whether Wi-Fi and Bluetooth are expected to be fitted.
- Wi-Fi: device visible, scan works, authentication succeeds, connection succeeds, browser works — yes/no/not attempted. Never share network name or key.
- Audio: selected output TYPE (built-in speakers/headphones/HDMI), whether a non-sensitive LOCAL audio file is audible; microphone separately if tested. Do not raise volume unexpectedly or change drivers.
- Bluetooth: adapter visible or not; pairing not tested unless a real adapter exists. Internal3 lacks the BlueZ daemon, so its "No adapters" indication alone cannot classify physical capability. The source candidate's package fix cannot be installed by claiming it is already in internal3.

If you make ordinary manual connection/output choices, capture a second snapshot:

    python3 /home/live/Downloads/wilsof-hardware-report > /home/live/wilsof-hardware-report-after.json

    python3 -m json.tool /home/live/wilsof-hardware-report-after.json

Review this JSON as well before sharing. Do not send passwords, keys, raw logs, coredumps or the VM disk. No automatic upload is provided.

## What these results do not prove

An internal3 diagnostic snapshot does not validate the SOF/BlueZ changes in an unbuilt internal4 image, nor installed-system propagation, physical sound playback or Bluetooth pairing by itself. Wi-Fi/audio causes remain unknown until actual hardware evidence is examined. QEMU exposes Ethernet/HDA and no Wi-Fi/Bluetooth adapter; its results cannot be relabelled as physical acceptance. No new ISO is authorized by this procedure.
