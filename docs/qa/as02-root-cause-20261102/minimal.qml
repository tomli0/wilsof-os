import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import Quickshell.Hyprland
ShellRoot {
    id: root
    property bool show: true
    property bool useGrab: false
    property string typed: ""
    property int keyCount: 0
    PanelWindow {
        id: panel
        visible: root.show
        implicitWidth: 420
        implicitHeight: 160
        color: "#20252c"
        WlrLayershell.namespace: "as02:minimal"
        WlrLayershell.layer: WlrLayershell.Top
        WlrLayershell.exclusiveZone: -1
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.OnDemand
        TextInput {
            id: field
            anchors.fill: parent
            text: root.typed
            color: "white"
            focus: true
            Component.onCompleted: forceActiveFocus()
            onTextEdited: { root.typed = text; console.log("AS02_TEXT", text); }
            Keys.onPressed: e => { root.keyCount++; console.log("AS02_KEY", e.key); }
        }
    }
    HyprlandFocusGrab {
        windows: [panel]
        active: root.show && root.useGrab
    }
    IpcHandler {
        target: "probe"
        function close(): void { root.show = false; }
        function open(grab: bool): void { root.useGrab = grab; root.show = true; }
        function status(): string { return JSON.stringify({shown:root.show, query:root.typed, keys:root.keyCount, grab:root.useGrab}); }
    }
}
