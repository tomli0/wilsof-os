.pragma library

function row(id, name, comment, icon, kind, data) {
    return {id: id, name: name, comment: comment, icon: icon, kind: kind, data: data};
}

function defaults() {
    return [
        row("browser", "Browser", "Firefox", "language", "shortcut", "firefox"),
        row("terminal", "Terminal", "Ghostty", "terminal", "shortcut", "ghostty"),
        row("files", "Files", "Nautilus", "folder", "shortcut", "nautilus"),
        row("applications", "Applications", "Installed applications", "apps", "category", "applications"),
        row("folders", "Files & Folders", "Search names in your home directory", "folder_open", "category", "files"),
        row("settings", "Settings", "Display, sound, network and more", "settings", "settings", ""),
        row("appearance", "Appearance", "Wallpaper, colours, text and motion", "palette", "settings", "personalization"),
        row("help", "Help & Shortcuts", "Keyboard shortcuts and help", "keyboard", "settings", "keybinds"),
        row("about", "About Wilsof OS", "Everything you need. Nothing you don't.", "info", "about", ""),
        row("power", "Power", "Lock, suspend, log out, restart or shut down", "power_settings_new", "power", "")
    ];
}

function commands(query) {
    const q = (query || "").trim().toLowerCase();
    const rows = defaults().concat([row("lock", "Lock Screen", "Secure the current session", "lock", "lock", "")]);
    return rows.filter(r => (r.name + " " + r.comment + " " + r.data).toLowerCase().includes(q));
}

function selection(rows, id) {
    const index = rows.findIndex(r => r.id === id);
    return index >= 0 ? index : rows.length ? 0 : -1;
}

function accept(generation, activeGeneration, query, activeQuery, wantedOpen) {
    return wantedOpen && generation === activeGeneration && query === activeQuery;
}

function move(index, delta, length) {
    return length ? ((index + delta) % length + length) % length : -1;
}
