import QtQuick
import Quickshell
import qs.Modules.Plugins

// Original WS button; the exact same entry point as the keyboard binding.
PluginComponent {
    id: root
    pillClickAction: () => Quickshell.execDetached([Quickshell.env("HOME") + "/.local/bin/wilsof-search", "toggle"])
    horizontalBarPill: Component {
        Item {
            implicitWidth: 38; implicitHeight: root.widgetThickness
            Image {
                anchors.fill: parent
                fillMode: Image.PreserveAspectFit
                source: "file://" + Quickshell.env("HOME") + "/.local/share/wilsof-os/assets/ws-monogram.png"
                Accessible.name: "Open Wilsof Menu"
            }
        }
    }
    verticalBarPill: Component {
        Item {
            implicitWidth: root.widgetThickness; implicitHeight: 38
            Image {
                anchors.fill: parent
                fillMode: Image.PreserveAspectFit
                source: "file://" + Quickshell.env("HOME") + "/.local/share/wilsof-os/assets/ws-monogram.png"
                Accessible.name: "Open Wilsof Menu"
            }
        }
    }
}
