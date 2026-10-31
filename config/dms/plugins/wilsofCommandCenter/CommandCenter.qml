import QtQuick
import Quickshell
import Quickshell.Io
import qs.Common
import qs.Services
import qs.Modals.Common
import qs.DCommon.Widgets
import "Model.js" as Model

// A resident DMS plugin Item, not a separate shell, service or search daemon.
Item {
    id: root
    property var pluginService: null
    property string query: ""
    property bool wantedOpen: false
    property string category: ""
    property var rows: []
    property var localRows: []
    property var fileRows: []
    property int selected: -1
    property string searchNote: "Local search · names only"
    property double queryStarted: 0
    property int usefulResultsMs: 0
    property int fileGeneration: 0
    property var activeFileProcess: null
    readonly property string bin: Quickshell.env("HOME") + "/.local/bin/"

    function publish(items, preserve) {
        const id = preserve && selected >= 0 && selected < rows.length ? rows[selected].id : "";
        rows = items;
        selected = Model.selection(rows, id);
    }

    function refresh() {
        queryStarted = Date.now();
        fileGeneration++;
        if (activeFileProcess) {
            activeFileProcess.running = false;
            activeFileProcess = null;
        }
        fileTimer.stop();
        fileRows = [];
        searchNote = "Local search · names only";
        if (!query.trim() && !category) {
            localRows = Model.defaults();
        } else {
            let result = category ? [] : Model.commands(query);
            if (category !== "files") {
                const apps = AppSearchService.searchApplications(query);
                for (const app of apps.slice(0, 30)) {
                    result.push(Model.row("app:" + (app.id || app.name) + (app.isAction ? ":" + app.name : ""), app.name, app.comment || "Application", "apps", "app", app));
                }
                if (!category) {
                    const settings = AppSearchService.getBuiltInLauncherItems("dms_settings_search", query);
                    for (const setting of settings.slice(0, 8))
                        result.push(Model.row("setting:" + setting.action, setting.name, setting.comment, "settings", "setting", setting));
                }
            }
            localRows = result;
            if (category !== "applications")
                fileTimer.restart();
        }
        publish(localRows, false);
        usefulResultsMs = rows.length ? Date.now() - queryStarted : -1;
    }

    function open() {
        wantedOpen = true;
        query = "";
        category = "";
        refresh();
        center.targetScreen = CompositorService.getFocusedScreen();
        center.open();
    }

    function activate(index) {
        // Enter and mouse both snapshot the exact currently highlighted row.
        if (index < 0 || index >= rows.length)
            return;
        selected = index;
        const row = rows[index];
        if (row.kind === "category") {
            category = row.data;
            query = "";
            refresh();
            return;
        }
        root.wantedOpen = false;
        center.close();
        switch (row.kind) {
        case "shortcut": {
            const desktopIds = {firefox: "firefox", ghostty: "com.mitchellh.ghostty", nautilus: "org.gnome.Nautilus"};
            const entry = DesktopEntries.heuristicLookup(desktopIds[row.data]);
            if (entry)
                SessionService.launchDesktopEntry(entry);
            else
                ToastService.showError("Application unavailable", row.comment);
            break;
        }
        case "app":
            if (row.data.isAction)
                SessionService.launchDesktopAction(row.data.parentApp, row.data.actionData);
            else
                SessionService.launchDesktopEntry(row.data);
            break;
        case "file":
            Quickshell.execDetached(["systemd-run", "--user", "--collect", "--quiet", "--", "xdg-open", "file://" + row.data.split("/").map(encodeURIComponent).join("/")]);
            break;
        case "setting":
            AppSearchService.executeBuiltInLauncherItem(row.data);
            break;
        case "settings":
            if (row.data)
                PopoutService.openSettingsWithTab(row.data);
            else
                PopoutService.openSettings();
            break;
        case "about":
            PopoutService.openSettingsWithTab("about");
            break;
        case "power":
            // Never invoke destructive actions directly; retain DMS confirmation.
            PopoutService.openPowerMenu();
            break;
        case "lock":
            Quickshell.execDetached(["systemd-run", "--user", "--collect", "--quiet", "--", root.bin + "wilsof-lock"]);
            break;
        }
    }

    Timer {
        id: fileTimer
        interval: 35
        onTriggered: {
            const process = fileSearch.createObject(root, {pendingQuery: root.query, generation: root.fileGeneration});
            root.activeFileProcess = process;
            process.running = true;
        }
    }

    Component {
        id: fileSearch
        Process {
            id: worker
            property string pendingQuery
            property int generation
            command: [root.bin + "wilsof-file-search", "--query", pendingQuery]
            stdout: StdioCollector {
                onStreamFinished: {
                    if (!Model.accept(worker.generation, root.fileGeneration, worker.pendingQuery, root.query, root.wantedOpen))
                        return;
                    try {
                        const data = JSON.parse(text);
                        root.fileRows = data.items.map(f => Model.row("file:" + f.path, f.name, f.path.replace(Quickshell.env("HOME"), "~"), f.directory ? "folder" : "description", "file", f.path));
                        root.publish(root.localRows.concat(root.fileRows), true);
                        if (root.usefulResultsMs < 0 && root.rows.length)
                            root.usefulResultsMs = Date.now() - root.queryStarted;
                        root.searchNote = data.truncated ? "Bounded home search · refine your query" : "Home names only · no content index";
                        if (data.unreadable)
                            root.searchNote += " · some folders unavailable";
                    } catch (e) {
                        root.searchNote = "File search unavailable · applications and settings still work";
                    }
                }
            }
            onExited: code => {
                if (root.activeFileProcess === worker) {
                    root.activeFileProcess = null;
                    if (code !== 0 && generation === root.fileGeneration)
                        root.searchNote = "File search unavailable · applications and settings still work";
                }
                destroy();
            }
        }
    }

    IpcHandler {
        target: "commandCenter"
        function toggle(): string {
            if (root.wantedOpen) { root.wantedOpen = false; center.close(); } else root.open();
            return "WILSOF_COMMAND_CENTER_OK";
        }
        function close(): string { root.wantedOpen = false; center.close(); return "closed"; }
        function search(text: string): string {
            if (!root.wantedOpen) root.open();
            root.query = text;
            root.category = "";
            root.refresh();
            return "search requested";
        }
        function status(): string {
            return JSON.stringify({visible: center.shouldBeVisible, query: root.query, category: root.category, count: root.rows.length, selected: root.selected, selectedId: root.selected >= 0 ? root.rows[root.selected].id : "", usefulResultsMs: root.usefulResultsMs, filesRunning: root.activeFileProcess !== null, note: root.searchNote});
        }
    }

    DModal {
        id: center
        layerNamespace: "wilsof:command-center"
        modalWidth: Math.min(560, screenWidth - 32)
        modalHeight: Math.min(650, screenHeight * 0.8)
        backgroundColor: Theme.surface
        borderColor: Theme.outline
        borderWidth: 1
        cornerRadius: 6
        enableShadow: false
        animationDuration: SettingsData.reduceMotion ? 0 : 100
        onDialogClosed: {
            root.wantedOpen = false;
            root.fileGeneration++;
            fileTimer.stop();
            if (root.activeFileProcess)
                root.activeFileProcess.running = false;
        }
        content: Component {
            Item {
                anchors.fill: parent
                anchors.margins: 16
                Column {
                    id: heading
                    width: parent.width
                    spacing: 12
                    Row {
                        width: parent.width
                        Text { width: parent.width - 48; text: "WILSOF  /  COMMAND CENTER"; color: Theme.primary; font.pixelSize: 13; font.letterSpacing: 1 }
                        Text { text: "ESC"; color: Theme.surfaceVariantText; font.pixelSize: 12 }
                    }
                    Rectangle {
                        width: parent.width
                        height: 48
                        radius: 6
                        color: Theme.surfaceContainer
                        border.color: Theme.primary
                        border.width: search.activeFocus ? 1 : 0
                        TextInput {
                            id: search
                            anchors.fill: parent
                            anchors.margins: 12
                            text: root.query
                            color: Theme.surfaceText
                            font.pixelSize: 16
                            clip: true
                            selectByMouse: true
                            onTextEdited: { root.query = text; root.refresh(); }
                            Component.onCompleted: forceActiveFocus()
                            Connections { target: center; function onOpened() { search.forceActiveFocus(); } }
                            Keys.onPressed: event => {
                                if (event.key === Qt.Key_Down || event.key === Qt.Key_Up) {
                                    root.selected = Model.move(root.selected, event.key === Qt.Key_Down ? 1 : -1, root.rows.length);
                                    results.positionViewAtIndex(root.selected, ListView.Contain);
                                    event.accepted = true;
                                } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                                    root.activate(root.selected);
                                    event.accepted = true;
                                } else if (event.key === Qt.Key_Escape) {
                                    center.close(); event.accepted = true;
                                } else if (event.key === Qt.Key_Backspace && text === "" && root.category) {
                                    root.category = ""; root.refresh(); event.accepted = true;
                                }
                            }
                            Text { visible: !search.text; text: "Search apps, files and settings"; color: Theme.surfaceVariantText; font: search.font }
                        }
                    }
                    Text { text: root.category ? (root.category === "files" ? "FILES & FOLDERS  /  Backspace to go back" : "APPLICATIONS  /  Backspace to go back") : "Everything you need. Nothing you don't."; color: Theme.surfaceVariantText; font.pixelSize: 12 }
                }
                ListView {
                    id: results
                    anchors.top: heading.bottom
                    anchors.topMargin: 12
                    anchors.bottom: footer.top
                    anchors.bottomMargin: 8
                    width: parent.width
                    clip: true
                    spacing: 4
                    model: root.rows
                    currentIndex: root.selected
                    boundsBehavior: Flickable.StopAtBounds
                    delegate: Rectangle {
                        required property int index
                        required property var modelData
                        width: results.width
                        height: modelData.kind === "shortcut" ? 50 : 38
                        radius: 6
                        color: index === root.selected ? Theme.primaryContainer : (modelData.kind === "shortcut" ? Theme.surfaceContainer : "transparent")
                        border.width: index === root.selected ? 1 : 0
                        border.color: Theme.primary
                        DIcon { x: 12; anchors.verticalCenter: parent.verticalCenter; name: modelData.icon; size: 22; color: index === root.selected ? Theme.primary : Theme.surfaceVariantText }
                        Column {
                            x: 48; anchors.verticalCenter: parent.verticalCenter; width: parent.width - 64
                            Text { width: parent.width; text: modelData.name; color: Theme.surfaceText; font.pixelSize: 15; elide: Text.ElideRight }
                            Text { width: parent.width; text: modelData.comment; color: Theme.surfaceVariantText; font.pixelSize: 12; elide: Text.ElideMiddle }
                        }
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: { search.forceActiveFocus(); root.activate(index); }
                        }
                    }
                    Text { anchors.centerIn: parent; visible: root.rows.length === 0; text: root.activeFileProcess || fileTimer.running ? "Searching home names…" : "No results. Try another name."; color: Theme.surfaceVariantText; font.pixelSize: 14 }
                }
                Text { id: footer; anchors.bottom: parent.bottom; width: parent.width; text: root.searchNote + "    ↑↓  Select    ↵  Open"; color: Theme.surfaceVariantText; font.pixelSize: 11; elide: Text.ElideRight }
            }
        }
    }
}
