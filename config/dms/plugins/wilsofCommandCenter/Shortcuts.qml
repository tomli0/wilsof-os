import QtQuick
import Quickshell
import Quickshell.Io
import qs.Common
import qs.Services
import qs.Modals.Common

// Searchable overview of the common Wilsof shortcuts. Editing and conflict
// detection live in wilsof-shortcuts (one command per action); this surface
// only lists, marks edited bindings and offers the explicit restore default.
DModal {
    id: editor
    layerNamespace: "wilsof:shortcuts"
    modalWidth: Math.min(640, screenWidth - 32)
    modalHeight: Math.min(600, screenHeight * 0.85)
    backgroundColor: Theme.surface
    borderColor: Theme.outline
    borderWidth: 1
    cornerRadius: 6
    enableShadow: false
    property var actions: []
    property string filter: ""

    function refresh() {
        actions = [];
        loader.running = true;
    }

    onOpened: refresh()

    function visibleRows() {
        const needle = filter.trim().toLowerCase();
        if (!needle)
            return actions;
        return actions.filter(a => (a.id + " " + a.label + " " + a.keys).toLowerCase().includes(needle));
    }


    Process {
        id: loader
        command: [Quickshell.env("HOME") + "/.local/bin/wilsof-shortcuts", "list", "--json"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    editor.actions = JSON.parse(text).actions;
                } catch (e) {
                    editor.actions = [];
                }
            }
        }
    }

    content: Component {
        Column {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 12
            // The search field owns the keyboard the moment the modal opens.
            Component.onCompleted: search.forceActiveFocus()

            Row {
                width: parent.width
                spacing: 12
                Text { text: "[ W S ]"; color: Theme.primary; font.family: "JetBrainsMono Nerd Font"; font.pixelSize: 24 }
                Text {
                    text: "Close · Esc"
                    color: Theme.primary
                    font.pixelSize: 14
                    activeFocusOnTab: true
                    font.underline: activeFocus
                    Keys.onReturnPressed: editor.close()
                    MouseArea { anchors.fill: parent; onClicked: editor.close() }
                }
            }
            Text { text: "Wilsof snarveier"; color: Theme.surfaceText; font.pixelSize: 20 }
            TextField {
                id: search
                width: parent.width
                placeholderText: "Søk i snarveier…"
                color: Theme.surfaceText
                font.pixelSize: 14
                onTextChanged: editor.filter = text
            }
            ListView {
                id: list
                width: parent.width
                height: parent.height - 210
                clip: true
                model: editor.visibleRows()
                delegate: Row {
                    width: list.width
                    height: 34
                    spacing: 16
                    Text {
                        text: modelData.keys
                        color: Theme.primary
                        width: 220
                        font.family: "JetBrainsMono Nerd Font"
                        font.pixelSize: 14
                    }
                    Text { text: modelData.label; color: Theme.surfaceText; font.pixelSize: 14; width: parent.width - 220 - 90 }
                    Text {
                        text: modelData.default ? "" : "endret"
                        color: Theme.warning
                        font.pixelSize: 12
                        visible: !modelData.default
                    }
                }
            }
            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                color: Theme.surfaceVariantText
                font.pixelSize: 12
                text: "Endre: wilsof-shortcuts set <handling> <taster> · Tilbakestill: wilsof-appearance reset og wilsof-shortcuts reset · Bruk: hyprctl reload"
            }
            Text {
                text: "Restore defaults ↻"
                color: Theme.primary
                font.pixelSize: 14
                activeFocusOnTab: true
                font.underline: activeFocus
                Keys.onReturnPressed: resetter.running = true
                MouseArea { anchors.fill: parent; onClicked: resetter.running = true }
                Process {
                    id: resetter
                    command: ["systemd-run", "--user", "--collect", "--quiet", "--", Quickshell.env("HOME") + "/.local/bin/wilsof-shortcuts", "reset"]
                }
            }
        }
    }
}
