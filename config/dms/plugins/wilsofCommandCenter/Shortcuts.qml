import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import qs.Common
import qs.Modals.Common
import "Capture.js" as Capture

// One interface, shared by Learn and Configure. The backend owns all writes.
DModal {
    id: editor
    layerNamespace: "wilsof:shortcuts"
    modalWidth: Math.min(700, screenWidth - 24)
    modalHeight: Math.min(640, screenHeight - 48)
    backgroundColor: "#14181E"
    borderColor: "#3a424b"
    borderWidth: 1
    cornerRadius: 6
    enableShadow: false
    animationDuration: 0
    closeOnEscapeKey: false
    property var actions: []
    property var bindings: []
    property bool runtimeAvailable: false
    property string filter: ""
    property bool capturing: false
    property string captureAction: ""
    property bool confirmReset: false
    property string message: ""
    property string errors: ""
    property var arguments: []
    readonly property string helper: Quickshell.env("HOME") + "/.local/bin/wilsof-shortcuts"
    onOpened: { editor.capturing = false; confirmReset = false; refresh(); }
    onDialogClosed: { editor.capturing = false; captureAction = ""; confirmReset = false; }
    ShortcutInhibitor { window: editor.contentWindow; enabled: editor.capturing }
    function refresh() { if (!loader.running) loader.running = true; }
    function visibleRows() {
        const all = actions.map(a => ({id:a.id,label:a.label,keys:runtimeAvailable ? (a.activeKeys.length ? a.activeKeys.join(", ") : "Not active · configured " + a.keys) : "Offline · " + a.keys,readOnly:false,default:a.default}));
        for (const b of bindings) {
            if ((b.description || "").startsWith("Wilsof:")) continue;
            all.push({id:"",label:b.description || b.dispatcher,keys:b.keys,readOnly:true,default:true});
        }
        const q = filter.trim().toLowerCase();
        return q ? all.filter(a => (a.label + " " + a.keys + " " + a.id).toLowerCase().includes(q)) : all;
    }
    function change(action) {
        if (writer.running || !runtimeAvailable) return;
        captureAction = action; capturing = true; confirmReset = false;
        message = "Press the new combination. Escape cancels capture.";
    }
    function save(args) {
        if (writer.running) return;
        capturing = false; captureAction = ""; confirmReset = false; errors = "";
        editor.arguments = [helper].concat(args).concat(["--apply"]);
        message = "Checking conflicts and applying…";
        writer.running = true;
    }
    Process {
        id: loader
        command: [editor.helper,"list","--json"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    const data = JSON.parse(text);
                    editor.actions = data.actions; editor.bindings = data.bindings;
                    editor.runtimeAvailable = data.runtimeAvailable;
                } catch (e) { editor.runtimeAvailable = false; editor.message = "Active bindings could not be read. Editing is disabled."; }
            }
        }
        onExited: code => { if (code !== 0) { editor.runtimeAvailable = false; editor.message = "Active bindings unavailable. No changes were made."; } }
    }
    Process {
        id: writer
        command: editor.arguments
        stderr: StdioCollector { onStreamFinished: editor.errors = text.trim() }
        onExited: code => {
            editor.message = code === 0 ? "Saved. Active Hyprland bindings verified; changes persist after login." : (editor.errors || "Shortcut could not be applied. Configuration was preserved.");
            editor.refresh();
        }
    }
    content: Component {
        Item {
            Material.theme: Material.Dark
            Material.accent: "#86B9CE"
            Material.primary: "#86B9CE"
            Material.background: "#202830"
            Material.foreground: "#E7EEF2"
            anchors.fill: parent
            anchors.margins: 18
            Keys.onPressed: event => {
                if (editor.capturing) {
                    event.accepted = true;
                    if (event.isAutoRepeat) return;
                    const keys = Capture.combination(event.key,event.modifiers);
                    if (keys === "cancel") { editor.capturing = false; editor.message = "Capture cancelled."; }
                    else if (keys) editor.save(["set",editor.captureAction,keys]);
                } else if (event.key === Qt.Key_Escape) {
                    if (editor.confirmReset) editor.confirmReset = false;
                    else editor.close();
                    event.accepted = true;
                }
            }
            Column {
                id: header
                width: parent.width; spacing: 10
                Row {
                    width: parent.width
                    Label { width: parent.width - 80; text: "Keyboard Shortcuts"; color: "#E7EEF2"; font.pixelSize: 21 }
                    Button { text: "Back"; onClicked: editor.close() }
                }
                TextField {
                    id: search
                    width: parent.width
                    placeholderText: "Search shortcuts and active bindings"
                    text: editor.filter
                    onTextEdited: editor.filter = text
                    enabled: !editor.capturing
                    Component.onCompleted: forceActiveFocus()
                    Connections { target: editor; function onOpened() { search.forceActiveFocus(); } }
                }
                Label { width: parent.width; text: editor.runtimeAvailable ? "Wilsof bindings are editable. Other active bindings are read-only." : "Offline view only. A running Hyprland session is required to edit."; wrapMode: Text.WordWrap; color: "#AAB6C0"; font.pixelSize: 12 }
            }
            ListView {
                id: list
                anchors.top: header.bottom; anchors.topMargin: 12
                anchors.bottom: status.top; anchors.bottomMargin: 12
                width: parent.width; clip: true; spacing: 4
                visible: !editor.capturing && !editor.confirmReset
                model: editor.visibleRows()
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                delegate: Rectangle {
                    required property var modelData
                    width: list.width; height: 66; radius: 4; color: "#202830"
                    Column {
                        x: 10; anchors.verticalCenter: parent.verticalCenter; width: Math.max(70,parent.width - 234)
                        Label { width: parent.width; text: modelData.label; color: "#E7EEF2"; elide: Text.ElideRight; font.pixelSize: 14 }
                        Label { width: parent.width; text: modelData.keys; color: "#86B9CE"; elide: Text.ElideRight; font.pixelSize: 12 }
                    }
                    Row {
                        anchors.right: parent.right; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter; spacing: 6
                        visible: !modelData.readOnly
                        Button { text: "Change"; enabled: editor.runtimeAvailable && !writer.running; onClicked: { editor.change(modelData.id); captureSurface.forceActiveFocus(); } }
                        Button { text: "Restore default"; enabled: editor.runtimeAvailable && !writer.running && !modelData.default; onClicked: editor.save(["reset",modelData.id]) }
                    }
                }
            }
            FocusScope {
                id: captureSurface
                anchors.top: header.bottom; anchors.bottom: status.top; width: parent.width
                visible: editor.capturing || editor.confirmReset
                activeFocusOnTab: visible
                Column {
                    anchors.centerIn: parent; width: parent.width; spacing: 18
                    Label { width: parent.width; text: editor.capturing ? "Press a combination for " + editor.captureAction : "Restore all Wilsof defaults?"; wrapMode: Text.WordWrap; color: "#E7EEF2"; font.pixelSize: 18 }
                    Label { width: parent.width; text: editor.capturing ? "System shortcuts are temporarily inhibited during capture. Escape cancels." : "Unrelated bindings will not be modified."; wrapMode: Text.WordWrap; color: "#AAB6C0" }
                    Row {
                        spacing: 12
                        Button { visible: editor.confirmReset; text: "Restore all defaults"; onClicked: editor.save(["reset"]) }
                        Button { text: "Cancel"; onClicked: { editor.capturing = false; editor.confirmReset = false; search.forceActiveFocus(); } }
                    }
                }
            }
            Column {
                id: status
                anchors.bottom: parent.bottom; width: parent.width; spacing: 10
                Label { width: parent.width; text: editor.message; wrapMode: Text.WordWrap; color: "#86B9CE"; font.pixelSize: 12 }
                Button { text: "Restore all defaults"; enabled: editor.runtimeAvailable && !writer.running; onClicked: { editor.confirmReset = true; captureSurface.forceActiveFocus(); } }
            }
        }
    }
}
