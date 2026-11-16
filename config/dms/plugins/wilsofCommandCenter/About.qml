import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import Quickshell
import Quickshell.Io
import qs.Common
import qs.Modals.Common

DModal {
    id: about
    layerNamespace: "wilsof:about"
    modalWidth: Math.min(580, screenWidth - 24)
    modalHeight: Math.min(680, screenHeight - 48)
    backgroundColor: "#14181E"
    borderColor: "#3a424b"
    borderWidth: 1
    cornerRadius: 6
    enableShadow: false
    animationDuration: 0
    property var info: ({})
    onOpened: details.running = true
    Process {
        id: details
        command: [Quickshell.env("HOME") + "/.local/bin/wilsof-about-info"]
        stdout: StdioCollector {
            onStreamFinished: {
                try { about.info = JSON.parse(text); }
                catch (e) { about.info = {version:"Installed identity unavailable"}; }
            }
        }
    }
    content: Component {
        ScrollView {
            Material.theme: Material.Dark
            Material.accent: "#86B9CE"
            Material.primary: "#86B9CE"
            Material.background: "#202830"
            Material.foreground: "#E7EEF2"
            anchors.fill: parent
            anchors.margins: 20
            ScrollBar.vertical.policy: ScrollBar.AlwaysOn
            contentWidth: availableWidth
            Column {
                width: parent.width
                spacing: 15
                Row {
                    width: parent.width
                    Image {
                        width: parent.width - 90; height: 78
                        horizontalAlignment: Image.AlignLeft
                        fillMode: Image.PreserveAspectFit
                        source: "file://" + Quickshell.env("HOME") + "/.local/share/wilsof-os/assets/ws-monogram.png"
                        Accessible.name: "Wilsof WS logo"
                    }
                    Button { text: "Back"; onClicked: about.close() }
                }
                Label { text: "Wilsof OS"; color: "#E7EEF2"; font.pixelSize: 25 }
                Label { width: parent.width; text: "Made with purpose. Built with curiosity."; color: "#86B9CE"; wrapMode: Text.WordWrap; font.pixelSize: 16 }
                Label { text: "Vision"; color: "#E7EEF2"; font.pixelSize: 17 }
                Label { width: parent.width; text: "Wilsof OS was created from a simple idea: Linux should be powerful without being complicated. A clean, modern desktop that puts usability, freedom and simplicity first."; color: "#C8D7DE"; wrapMode: Text.WordWrap; font.pixelSize: 14 }
                Label { text: "Built on Open Source"; color: "#E7EEF2"; font.pixelSize: 17 }
                Label { width: parent.width; text: "Built on Arch Linux, Hyprland and Dux, combining established open-source technology with custom Wilsof design, configuration and development."; color: "#C8D7DE"; wrapMode: Text.WordWrap; font.pixelSize: 14 }
                Label { text: "Dedicated to William & Sofie"; color: "#86B9CE"; font.pixelSize: 17 }
                Label { width: parent.width; text: "The name Wilsof comes from my two children, William and Sofie. What began as a personal project carries their names as a reminder of curiosity, creativity and the joy of building something of your own."; color: "#C8D7DE"; wrapMode: Text.WordWrap; font.pixelSize: 14 }
                Label { text: "System"; color: "#E7EEF2"; font.pixelSize: 17 }
                Label { width: parent.width; text: (about.info.version || "Loading installed identity…") + "\nInstalled source: " + (about.info.sourceCommit || "Unavailable") + "\n" + (about.info.platform || "Linux") + " · " + (about.info.architecture || "") + "\nKernel " + (about.info.kernel || "unavailable"); color: "#AAB6C0"; wrapMode: Text.WrapAnywhere; font.pixelSize: 12 }
                Label { text: "Open-source credits and licenses"; color: "#E7EEF2"; font.pixelSize: 17 }
                Label { width: parent.width; text: "Upstream components include Linux, Arch Linux, systemd, Hyprland, Dux / DMS, Quickshell, Qt, Ghostty, Fastfetch and the installed applications. They retain their respective licenses and attribution."; color: "#C8D7DE"; wrapMode: Text.WordWrap; font.pixelSize: 13 }
                Label { width: parent.width; text: (about.info.packages || []).map(p => p.Name + " " + p.Version + " · " + p.Licenses).join("\n"); color: "#AAB6C0"; wrapMode: Text.WordWrap; font.pixelSize: 12 }
                Label { width: parent.width; text: about.info.license || "License information unavailable"; color: "#AAB6C0"; wrapMode: Text.WordWrap; font.pixelSize: 12 }
                Button { text: "Open installed license notices"; onClicked: Qt.openUrlExternally("file:///usr/share/licenses") }
                Button { text: "GitHub"; onClicked: Qt.openUrlExternally("https://github.com/tomli0/wilsof-os") }
            }
        }
    }
}
