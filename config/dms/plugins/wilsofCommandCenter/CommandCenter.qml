import QtQuick
import Quickshell
import Quickshell.Io
import qs.Common
import qs.Services
import qs.Modals.Common
import qs.DCommon.Widgets
import "Model.js" as Model
import "NativeLock.js" as NativeLock

// The WS bar button and Super+Space address this one resident component.
Item {
    id: root
    property var pluginService: null
    property string query: ""
    property bool wantedOpen: false
    property string category: ""
    property var rows: []
    property int selected: -1
    property var history: []
    property var searchItem: null
    property var listItem: null
    property var capabilities: ({screenshot:false, recording:false, install:false, remove:false, update:false, system:false, guide:false, emoji:false, "window-visuals":false})
    property var confirmation: null
    property int usefulResultsMs: 0
    readonly property string bin: Quickshell.env("HOME") + "/.local/bin/"
    readonly property string logo: "file://" + Quickshell.env("HOME") + "/.local/share/wilsof-os/assets/ws-monogram.png"

    // Preserve Private2's authoritative native lock observer and fail-closed gate.
    property var nativeState: NativeLock.fresh()
    property string observerEpoch: ""
    property string pendingModal: ""
    property var dialogSnapshot: null
    function nonce() {
        let s = "";
        for (let i = 0; i < 32; i++) s += Math.floor(Math.random() * 16).toString(16);
        return s;
    }
    function admission() { return NativeLock.allowed(nativeState); }
    onNativeStateChanged: if (!admission()) lockdown()
    Component.onCompleted: { observerRestart.start(); capabilityProbe.running = true; }
    Timer {
        id: observerRestart
        interval: 1000
        onTriggered: {
            root.nativeState = NativeLock.fresh();
            root.observerEpoch = root.nonce();
            nativeObserver.running = true;
        }
    }
    Timer {
        id: observerLease
        interval: 2500
        onTriggered: { root.nativeState = NativeLock.fresh(); nativeObserver.running = false; }
    }
    Process {
        id: nativeObserver
        command: [root.bin + "wilsof-lock-observer", root.observerEpoch]
        stdinEnabled: true
        stdout: SplitParser {
            splitMarker: "\n"
            onRead: line => {
                try {
                    const m = JSON.parse(line);
                    root.nativeState = NativeLock.receive(root.nativeState, m, root.observerEpoch);
                    if (root.nativeState.fault) { nativeObserver.running = false; return; }
                    observerLease.restart();
                } catch (e) { root.nativeState = NativeLock.fresh(); nativeObserver.running = false; }
            }
        }
        onExited: {
            observerLease.stop(); root.nativeState = NativeLock.fresh(); observerRestart.restart();
        }
    }
    function modalClosed(modal) {
        if (!modal) return true;
        if (modal.shouldBeVisible || modal.shouldHaveFocus || modal.isClosing || (modal.contentWindow && modal.contentWindow.visible)) return false;
        let found = false;
        for (const obj of modal.data) {
            if (obj && obj._held !== undefined && obj.wanted !== undefined && obj.active !== undefined) {
                found = true;
                if (obj._held || obj.wanted || obj.active) return false;
            }
        }
        return !modal.useHyprlandFocusGrab || found;
    }
    Process {
        id: capabilityProbe
        command: [root.bin + "wilsof-action", "capabilities"]
        stdout: StdioCollector {
            onStreamFinished: {
                try { root.capabilities = JSON.parse(text); root.refresh(true); }
                catch (e) { ToastService.showError("Wilsof Menu", "Tool availability could not be checked"); }
            }
        }
    }
    function desktopEntry(kind) {
        const ids = {firefox:"firefox", ghostty:"com.mitchellh.ghostty", nautilus:"org.gnome.Nautilus"};
        return DesktopEntries.heuristicLookup(ids[kind]);
    }
    function available(row) {
        if (!Model.available(row, capabilities)) return false;
        return row.kind !== "shortcut" || !!desktopEntry(row.data);
    }
    function publish(items, preserve) {
        const id = preserve && selected >= 0 && selected < rows.length ? rows[selected].id : "";
        rows = items.filter(available);
        selected = Model.selection(rows, id);
    }
    function refresh(preserve) {
        const started = Date.now();
        let result = [];
        if (query.trim() || category === "applications") {
            const apps = AppSearchService.searchApplications(query).map(app =>
                Model.row("app:" + (app.id || app.name) + (app.isAction ? ":" + app.name : ""), app.name, app.comment || "Application", "apps", "app", app));
            result = category === "applications" && !query.trim() ? apps : Model.search(query, apps, capabilities);
        } else result = Model.page(category);
        if (category === "emoji") result = Model.emojis(query);
        publish(result, preserve);
        usefulResultsMs = Date.now() - started;
    }
    function snapshot() {
        return {category:category, query:query, selectedId:selected >= 0 && selected < rows.length ? rows[selected].id : "", scrollY:listItem ? listItem.contentY : 0, stack:history};
    }
    function apply(state) {
        category = state.category; query = state.query; history = state.stack;
        refresh(false); selected = Model.selection(rows, state.selectedId);
        Qt.callLater(() => {
            if (listItem) listItem.contentY = state.scrollY;
            if (searchItem) searchItem.forceActiveFocus();
        });
    }
    function goRoot() { confirmation = null; apply({category:"",query:"",selectedId:"",scrollY:0,stack:[]}); }
    function goBack() {
        if (confirmation) { confirmation = null; return; }
        const state = Model.back(snapshot());
        if (state) apply(state);
        else { wantedOpen = false; center.close(); }
    }
    function lockdown() {
        wantedOpen = false; pendingModal = ""; confirmation = null; dialogWait.stop();
        if (aboutLoader.item) aboutLoader.item.instantClose();
        if (shortcutsLoader.item) shortcutsLoader.item.instantClose();
        center.instantClose();
    }
    function open() {
        if (!root.admission()) return;
        wantedOpen = true; pendingModal = ""; goRoot();
        center.targetScreen = CompositorService.getFocusedScreen(); center.open();
        capabilityProbe.running = true;
    }
    function openDialog(kind) {
        dialogSnapshot = snapshot(); pendingModal = kind; center.close(); dialogWait.restart();
    }
    Timer {
        id: dialogWait
        interval: 20
        repeat: true
        onTriggered: {
            if (!root.admission() || !root.pendingModal) { stop(); return; }
            if (!root.modalClosed(center)) return;
            const loader = root.pendingModal === "about" ? aboutLoader : shortcutsLoader;
            loader.active = true;
            if (loader.item) { loader.item.targetScreen = center.targetScreen; loader.item.open(); stop(); }
        }
    }
    function returnFromDialog() {
        if (!pendingModal || !root.admission()) return;
        pendingModal = ""; wantedOpen = true;
        center.open();
        if (dialogSnapshot) apply(dialogSnapshot);
        Qt.callLater(() => { if (searchItem) searchItem.forceActiveFocus(); });
    }
    function launch(argv) {
        Quickshell.execDetached(["systemd-run", "--user", "--collect", "--quiet", "--"].concat(argv));
    }
    function confirmPower() {
        if (!confirmation || !root.admission()) return;
        const action = confirmation.data;
        confirmation = null; wantedOpen = false; center.close();
        if (action === "logout") SessionService.logout();
        else if (action === "reboot") SessionService.reboot();
        else if (action === "poweroff") SessionService.poweroff();
    }
    function activate(index) {
        if (!root.admission()) { root.lockdown(); return; }
        if (index < 0 || index >= rows.length) return;
        selected = index;
        const row = rows[index];
        if (row.kind === "category" || row.kind === "emoji") {
            apply(Model.enter(snapshot(), row.kind === "emoji" ? "emoji" : row.data)); return;
        }
        if (row.kind === "power") { confirmation = row; return; }
        if (row.kind === "about" || row.kind === "shortcuts") { openDialog(row.kind); return; }
        wantedOpen = false; center.close();
        switch (row.kind) {
        case "shortcut": {
            const entry = desktopEntry(row.data);
            if (entry) SessionService.launchDesktopEntry(entry);
            else ToastService.showError("Application unavailable", row.comment);
            break;
        }
        case "app":
            if (row.data.isAction) SessionService.launchDesktopAction(row.data.parentApp, row.data.actionData);
            else SessionService.launchDesktopEntry(row.data);
            break;
        case "settings": PopoutService.openSettingsWithTab(row.data); break;
        case "control": launch(["dms", "ipc", "call", "control-center", "openWith", row.data]); break;
        case "url": Qt.openUrlExternally(row.data); break;
        case "action": launch([root.bin + "wilsof-action", row.data]); break;
        case "clipboard": PopoutService.openClipboardHistory(); break;
        case "copy": launch(["wl-copy", "--foreground", "--", row.data]); break;
        case "lock":
            Quickshell.execDetached(["systemd-run", "--user", "--collect", "--quiet", "--", root.bin + "wilsof-lock"]);
            break;
        }
    }
    function handleKey(event, editing) {
        const names = {};
        names[Qt.Key_Down]="Down"; names[Qt.Key_Up]="Up"; names[Qt.Key_Left]="Left";
        names[Qt.Key_Right]="Right"; names[Qt.Key_Backspace]="Backspace";
        names[Qt.Key_Return]="Return"; names[Qt.Key_Enter]="Enter"; names[Qt.Key_Escape]="Escape";
        const action = Model.keyAction(names[event.key] || "", editing,
            !!(event.modifiers & (Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier | Qt.ShiftModifier)));
        if (confirmation) {
            if (action === "escape") confirmation = null;
            else if (action === "activate") confirmPower();
            else return;
        } else if (action === "next" || action === "previous") {
            selected = Model.move(selected, action === "next" ? 1 : -1, rows.length);
            if (listItem) listItem.positionViewAtIndex(selected, ListView.Contain);
        } else if (action === "activate") activate(selected);
        else if (action === "forward") {
            if (selected >= 0 && (rows[selected].kind === "category" || rows[selected].kind === "emoji")) activate(selected);
        } else if (action === "back" || action === "escape") goBack();
        else return;
        event.accepted = true;
    }
    IpcHandler {
        target: "commandCenter"
        function prepareLock(token: string): string {
            if (!/^[a-f0-9]{32}$/.test(token) || !nativeObserver.running || !root.nativeState.known) return "WILSOF_LOCK_UNAVAILABLE";
            root.nativeState = NativeLock.prepare(root.nativeState, token); root.lockdown();
            nativeObserver.write(JSON.stringify({prepare:token}) + "\n"); return "WILSOF_LOCK_PENDING";
        }
        function lockStatus(token: string): string {
            const s = root.nativeState;
            const closed = root.modalClosed(center) && root.modalClosed(aboutLoader.item) && root.modalClosed(shortcutsLoader.item);
            return JSON.stringify({generation:s.pending, key:s.key || "", epoch:s.epoch,
                ready:s.known && !s.fault && !s.locked && s.ready && s.pending === token && closed,
                closed:closed, known:s.known, nativeLocked:s.locked});
        }
        function toggle(): string {
            if (!root.admission()) { root.lockdown(); return "WILSOF_COMMAND_CENTER_LOCKED"; }
            if (root.wantedOpen) root.lockdown(); else root.open();
            return "WILSOF_COMMAND_CENTER_OK";
        }
        function configure(): string {
            if (!root.admission()) return "WILSOF_COMMAND_CENTER_LOCKED";
            if (!root.wantedOpen) root.open();
            root.apply(Model.enter(root.snapshot(), "configure"));
            return "WILSOF_COMMAND_CENTER_OK";
        }
        function close(): string { root.lockdown(); return "closed"; }
        function search(text: string): string {
            if (!root.admission()) { root.lockdown(); return "WILSOF_COMMAND_CENTER_LOCKED"; }
            if (!root.wantedOpen) root.open();
            root.query = text; root.refresh(false); return "search requested";
        }
        function status(): string {
            return JSON.stringify({visible:center.shouldBeVisible, query:root.query, category:root.category,
                count:root.rows.length, selected:root.selected, selectedId:root.selected >= 0 ? root.rows[root.selected].id : "",
                rows:root.rows.map(r=>({id:r.id,name:r.name,kind:r.kind})), depth:root.history.length,
                focused:!!root.searchItem && root.searchItem.activeFocus, scrollY:root.listItem ? root.listItem.contentY : 0,
                dialog:root.pendingModal, confirmation:!!root.confirmation, usefulResultsMs:root.usefulResultsMs});
        }
    }
    Connections { target: SessionService; function onSessionLocked() { root.lockdown(); } }
    Loader { id: aboutLoader; active: false; source: Qt.resolvedUrl("About.qml") }
    Loader { id: shortcutsLoader; active: false; source: Qt.resolvedUrl("Shortcuts.qml") }
    Connections { target: aboutLoader.item; function onDialogClosed() { root.returnFromDialog(); } }
    Connections { target: shortcutsLoader.item; function onDialogClosed() { root.returnFromDialog(); } }
    DModal {
        id: center
        layerNamespace: "wilsof:command-center"
        modalWidth: Math.min(460, screenWidth - 24)
        modalHeight: Math.min(580, screenHeight - 48)
        backgroundColor: "#14181E"
        borderColor: "#3a424b"
        borderWidth: 1
        cornerRadius: 6
        enableShadow: false
        animationDuration: 0
        closeOnEscapeKey: false
        onDialogClosed: if (!root.pendingModal) root.wantedOpen = false
        content: Component {
            Item {
                anchors.fill: parent
                anchors.margins: 14
                Keys.onPressed: event => root.handleKey(event, false)
                Column {
                    id: heading
                    width: parent.width
                    spacing: 10
                    Row {
                        width: parent.width
                        spacing: 10
                        Image {
                            width: 36; height: 28; fillMode: Image.PreserveAspectFit; source: root.logo
                            Accessible.role: Accessible.Button; Accessible.name: "Wilsof Menu home"
                            activeFocusOnTab: true
                            Keys.onReturnPressed: root.goRoot()
                            MouseArea { anchors.fill: parent; onClicked: root.goRoot() }
                        }
                        Text { text: "Wilsof Menu"; color: "#E7EEF2"; font.pixelSize: 16; anchors.verticalCenter: parent.verticalCenter; width: parent.width - 112 }
                        Text {
                            text: "← Back"; color: "#86B9CE"; font.pixelSize: 13
                            visible: root.history.length > 0 || !!root.confirmation
                            activeFocusOnTab: visible
                            Accessible.role: Accessible.Button; Accessible.name: "Back"
                            Keys.onReturnPressed: root.goBack()
                            MouseArea { anchors.fill: parent; onClicked: root.goBack() }
                        }
                    }
                    Rectangle {
                        width: parent.width; height: 42; radius: 5; color: "#202830"
                        border.color: "#86B9CE"; border.width: search.activeFocus ? 1 : 0
                        TextInput {
                            id: search
                            objectName: "wilsofMenuSearch"
                            anchors.fill: parent; anchors.margins: 10
                            text: root.query; color: "#E7EEF2"; font.pixelSize: 15
                            clip: true; selectByMouse: true; activeFocusOnTab: true
                            Accessible.name: "Search applications, actions and settings"
                            onTextEdited: { root.query = text; root.confirmation = null; root.refresh(false); }
                            Component.onCompleted: { root.searchItem = search; forceActiveFocus(); }
                            Component.onDestruction: if (root.searchItem === search) root.searchItem = null
                            Connections { target: center; function onOpened() { search.forceActiveFocus(); } }
                            Keys.onPressed: event => root.handleKey(event, text.length > 0 || inputMethodComposing)
                            Text { visible: !search.text; text: "Search apps, actions and settings"; color: "#AAB6C0"; font: search.font }
                        }
                    }
                    Text { text: root.history.length ? root.category.charAt(0).toUpperCase() + root.category.slice(1) : "Everything you need. Nothing you don't."; color: "#AAB6C0"; font.pixelSize: 12 }
                }
                ListView {
                    id: results
                    objectName: "wilsofMenuResults"
                    anchors.top: heading.bottom; anchors.topMargin: 10
                    anchors.bottom: footer.top; anchors.bottomMargin: 8
                    width: parent.width; clip: true; spacing: 3
                    visible: !root.confirmation
                    model: root.rows; currentIndex: root.selected
                    boundsBehavior: Flickable.StopAtBounds
                    Component.onCompleted: root.listItem = results
                    Component.onDestruction: if (root.listItem === results) root.listItem = null
                    delegate: Rectangle {
                        required property int index
                        required property var modelData
                        width: results.width; height: 46; radius: 5
                        color: index === root.selected ? "#263B47" : "transparent"
                        border.width: index === root.selected ? 1 : 0; border.color: "#86B9CE"
                        Accessible.role: Accessible.MenuItem; Accessible.name: modelData.name
                        DIcon { x: 10; anchors.verticalCenter: parent.verticalCenter; name: modelData.icon; size: 19; color: "#86B9CE" }
                        Column {
                            x: 40; anchors.verticalCenter: parent.verticalCenter; width: parent.width - 58
                            Text { width: parent.width; text: modelData.name; color: "#E7EEF2"; font.pixelSize: 14; elide: Text.ElideRight }
                            Text { width: parent.width; text: modelData.comment; color: "#AAB6C0"; font.pixelSize: 11; elide: Text.ElideRight }
                        }
                        MouseArea { anchors.fill: parent; onClicked: root.activate(index) }
                    }
                    Text { anchors.centerIn: parent; visible: root.rows.length === 0; text: "No results. Try another name."; color: "#AAB6C0"; font.pixelSize: 14 }
                }
                Column {
                    anchors.centerIn: results; width: parent.width; spacing: 18; visible: !!root.confirmation
                    Text { width: parent.width; text: root.confirmation ? root.confirmation.name + "?" : ""; color: "#E7EEF2"; font.pixelSize: 22 }
                    Text { width: parent.width; text: "Save your work first. Enter confirms; Escape cancels."; wrapMode: Text.WordWrap; color: "#AAB6C0"; font.pixelSize: 14 }
                    Row {
                        spacing: 30
                        Text { text: "Confirm"; color: "#86B9CE"; activeFocusOnTab: true; Keys.onReturnPressed: root.confirmPower(); MouseArea { anchors.fill: parent; onClicked: root.confirmPower() } }
                        Text { text: "Cancel"; color: "#86B9CE"; activeFocusOnTab: true; Keys.onReturnPressed: root.confirmation = null; MouseArea { anchors.fill: parent; onClicked: root.confirmation = null } }
                    }
                }
                Text { id: footer; anchors.bottom: parent.bottom; width: parent.width; text: "↑↓ Select   Enter Open   ← Back   Esc Close"; color: "#AAB6C0"; font.pixelSize: 11; elide: Text.ElideRight }
            }
        }
    }
}
