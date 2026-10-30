pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Io
import qs.Services
import "Profiles.js" as Profiles

QtObject {
    id: root
    property var status: ({saved: null, applied: null, error: null})
    readonly property string label: Profiles.label(status)
    property string pending: ""
    readonly property bool busy: operation.running

    function openSelector() {
        PopoutService.openDankLauncherV2WithQuery("profil");
    }

    function apply(profile) {
        if (!Profiles.valid(profile)) return;
        pending = profile;
        // Do not leave the previous profile displayed as confirmed during a switch.
        status = {saved: status.saved, applied: null, error: null};
        startNext();
    }

    function startNext() {
        if (operation.running) return;
        operation.applying = pending !== "";
        operation.command = [Quickshell.env("HOME") + "/.local/bin/wilsof-profile-ui"]
            .concat(operation.applying ? ["apply", pending] : ["status"]);
        pending = "";
        operation.running = true;
    }

    function finish(code) {
        // Last choice wins; no success notification for a superseded request.
        if (pending !== "") {
            Qt.callLater(startNext);
            return;
        }
        try {
            const value = JSON.parse(operation.stdout.text);
            if (value.schema_version !== 1 || !Profiles.valid(value.saved)
                || (value.applied !== null && value.applied !== value.saved))
                throw new Error("Invalid profile acknowledgement");
            if (code !== 0 && !value.error)
                throw new Error("Profile helper failed");
            status = value;
        } catch (e) {
            status = {saved: status.saved, applied: null, error: String(e)};
        }
        if (!operation.applying) return;
        if (status.error || !status.applied)
            ToastService.showError("Profil ikke bekreftet", status.error || "GUI-status er ukjent");
        else
            ToastService.showInfo("Profil: " + Profiles.name(status.applied), "Ingen apper ble flyttet, lukket eller startet");
    }

    property Process operation: Process {
        property bool applying: false
        stdout: StdioCollector {}
        stderr: StdioCollector {}
        onExited: (exitCode, exitStatus) => root.finish(exitCode)
    }
    // One shared singleton across all bars and the launcher, not one poller per output.
    property Timer refresh: Timer {
        interval: 5000
        repeat: true
        running: true
        triggeredOnStart: true
        onTriggered: { if (!operation.running) root.startNext(); }
    }
    property Timer watchdog: Timer {
        interval: 18000
        running: operation.running
        onTriggered: {
            operation.running = false;
            root.status = {saved: root.status.saved, applied: null, error: "Profile operation timed out"};
        }
    }
}
