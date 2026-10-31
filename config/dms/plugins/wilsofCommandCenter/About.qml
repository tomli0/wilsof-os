import QtQuick
import Quickshell
import Quickshell.Io
import qs.Common
import qs.Services
import qs.Modals.Common

DModal {
    id: about
    layerNamespace: "wilsof:about"
    modalWidth: Math.min(560, screenWidth - 32)
    modalHeight: Math.min(620, screenHeight * 0.8)
    backgroundColor: Theme.surface
    borderColor: Theme.outline
    borderWidth: 1
    cornerRadius: 6
    enableShadow: false
    property var info: ({})
    onOpened: details.running = true

    Process {
        id: details
        command: [Quickshell.env("HOME") + "/.local/bin/wilsof-about-info"]
        stdout: StdioCollector {
            onStreamFinished: {
                try { about.info = JSON.parse(text); }
                catch (e) { about.info = {version: "Installed identity unavailable"}; }
            }
        }
    }

    content: Component {
        Flickable {
            anchors.fill: parent
            anchors.margins: 24
            clip: true
            contentWidth: width
            contentHeight: body.height
            boundsBehavior: Flickable.StopAtBounds
            Column {
                id: body
                width: parent.width
                spacing: 16
                Row {
                    width: parent.width
                    Text { width: parent.width - 100; text: "[ W S ]"; color: Theme.primary; font.family: "JetBrainsMono Nerd Font"; font.pixelSize: 32 }
                    Text {
                        text: "Close · Esc"
                        color: Theme.primary
                        font.pixelSize: 14
                        activeFocusOnTab: true
                        font.underline: activeFocus
                        Keys.onReturnPressed: about.close()
                        MouseArea { anchors.fill: parent; onClicked: about.close() }
                    }
                }
                Text { text: "Wilsof OS"; color: Theme.surfaceText; font.pixelSize: 24 }
                Text { text: "Everything you need. Nothing you don't."; color: Theme.surfaceVariantText; font.pixelSize: 14 }
                Text { width: parent.width; text: (about.info.version || "Loading installed identity…") + "\nInstalled source: " + (about.info.sourceCommit || "Unavailable"); wrapMode: Text.WrapAnywhere; color: Theme.surfaceText; font.pixelSize: 13 }
                Text { width: parent.width; text: "System\n" + (about.info.platform || "Linux") + " · " + (about.info.architecture || "") + "\nKernel " + (about.info.kernel || "unavailable"); color: Theme.surfaceVariantText; font.pixelSize: 14; wrapMode: Text.WordWrap }
                Text { width: parent.width; text: "Upstream acknowledgements\nBuilt on Arch Linux, Linux, systemd, Hyprland, DMS / Dux, Quickshell, Qt, Ghostty, Firefox and Nautilus. These are independent open-source projects, not Wilsof-owned components."; color: Theme.surfaceText; font.pixelSize: 14; wrapMode: Text.WordWrap }
                Text { width: parent.width; text: (about.info.packages || []).map(p => p.Name + " " + p.Version + " · " + p.Licenses).join("\n"); color: Theme.surfaceVariantText; font.pixelSize: 12; wrapMode: Text.WordWrap }
                Text { width: parent.width; text: "License\n" + (about.info.license || "License information unavailable"); color: Theme.surfaceVariantText; font.pixelSize: 13; wrapMode: Text.WordWrap }
                Text {
                    text: "GitHub  ↗"
                    color: Theme.primary
                    font.pixelSize: 15
                    activeFocusOnTab: true
                    font.underline: activeFocus
                    Keys.onReturnPressed: Qt.openUrlExternally("https://github.com/tomli0/wilsof-os")
                    MouseArea { anchors.fill: parent; onClicked: Qt.openUrlExternally("https://github.com/tomli0/wilsof-os") }
                }
                Text { text: "Official website: not configured"; color: Theme.surfaceVariantText; font.pixelSize: 12 }
                Text { text: "Dedicated to William and Sofie."; color: Theme.primary; font.pixelSize: 14 }
            }
        }
    }
}
