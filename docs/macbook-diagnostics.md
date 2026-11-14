# Physical MacBook diagnostics (read-only)

Physical support remains **unverified**. Neither QEMU nor a firmware package's
presence identifies the owner's Wi-Fi chipset or establishes working Wi-Fi.
Do not install a guessed vendor driver or change the existing Omarchy system.

## One owner command

From a reviewed Wilsof checkout containing the current diagnostic, run in the
MacBook's normal Wilsof desktop session (live USB is sufficient):

    python3 bin/wilsof-hardware-report > "$HOME/wilsof-hardware.json"

Alternatively, after this revision is deployed, the installed command is
`wilsof-hardware-report`. An older Private2 command does not contain the new
module, display and power fields. No sudo, installation, driver loading,
rfkill write, network scan request or configuration change is performed.
Review the JSON, then return it privately. The report contains numeric PCI/USB
IDs and interface/module names, but omits MACs, SSIDs, network addresses,
connection profiles, serial numbers, monitor identities and raw journals.

## Interpretation order

1. Identify actual PCI class/vendor/device/subsystem IDs and bound driver, plus
   numeric USB IDs. Match these to hardware documentation before choosing a driver.
2. Compare wireless interfaces with driver-module ownership and loaded state.
   No wireless interface is evidence to investigate, not proof of a blocked radio.
3. Read firmware package versions, kernel missing-firmware filenames/error codes,
   and `modinfo` declarations for the actual Wi-Fi/Bluetooth modules. Declared
   firmware candidates are **not all mandatory** for every device; missing optional
   variants do not alone diagnose a failure. Compressed `.xz`/`.zst` files count.
4. Compare NetworkManager load/active/result, device states, Wi-Fi radio and rfkill
   hard/soft state. Unreadable rfkill values are `null`, not "unblocked".
5. Read cached Wi-Fi network count/signal. `--rescan no` cannot trigger discovery.
   Zero cached networks is **not** a failed active scan. Active scan behavior,
   SSID connection and reconnect require a separate observed physical test;
   obtain explicit owner consent before changing radio/connection state.
6. Inspect Bluetooth controller/module, service and numeric USB IDs. Adapter
   presence is not pairing/audio acceptance; no Bluetooth discovery is started.
7. Inspect numeric audio IDs, audio service state, anonymous default/mute/volume,
   and kernel audio-error summary. Sound playback/microphone require observation.
8. Inspect graphics IDs, compositor pixel dimensions/scaling/refresh only, battery
   percentage/status and supported/selected kernel sleep modes. These are state
   readings, not working suspend/resume, battery-life or physical scaling acceptance.

Each external probe has an eight-second deadline. Inaccessible tools/journals
remain unavailable, never a clean result. Do not run the whole report as root:
that would inspect the wrong user audio/session context. If kernel evidence is
unavailable, arrange a separately reviewed, narrowly scoped collection rather
than bypassing authentication or publishing raw logs.

After receiving the report, select one chipset-specific investigation with the
actual identifiers and kernel/package versions. Preserve the unchanged Omarchy
installation and keep physical acceptance separate from all virtual results.
