.pragma library

// Original Wilsof menu model. Entries describe real upstream or Wilsof actions.
function row(id, name, comment, icon, kind, data, keywords) {
    return {id:id, name:name, comment:comment || "", icon:icon, kind:kind,
        data:data === undefined ? "" : data, keywords:keywords || ""};
}
function defaults() {
    return [
        row("apps", "Apps", "Installed applications", "apps", "category", "apps"),
        row("learn", "Learn", "Guides and keyboard shortcuts", "school", "category", "learn"),
        row("tools", "Tools", "Capture, emoji and clipboard", "build", "category", "tools"),
        row("appearance", "Appearance", "Wallpaper and visual preferences", "palette", "category", "appearance"),
        row("configure", "Configure", "Essential device controls", "settings", "category", "configure"),
        row("software", "Software", "Install, remove and update", "deployed_code", "category", "software"),
        row("about-category", "About", "Wilsof OS and open-source credits", "info", "category", "about"),
        row("power", "Power", "Lock, log out, restart and shut down", "power_settings_new", "category", "power")
    ];
}
function page(category) {
    const pages = {
        apps: [
            row("applications", "Browse all applications", "Search or browse installed apps", "apps", "category", "applications"),
            row("browser", "Browser", "Firefox", "language", "shortcut", "firefox", "web internet"),
            row("files", "Files", "Nautilus", "folder", "shortcut", "nautilus", "file manager"),
            row("terminal", "Terminal", "Ghostty", "terminal", "shortcut", "ghostty", "shell console")
        ],
        learn: [
            row("shortcuts", "Keyboard Shortcuts", "View, capture and edit active bindings", "keyboard", "shortcuts", "", "keys hotkeys"),
            row("guide", "Wilsof Guide", "Desktop help", "help", "action", "guide"),
            row("hyprland-docs", "Hyprland documentation", "Official upstream documentation", "menu_book", "url", "https://wiki.hypr.land/"),
            row("dux-docs", "Dux / DMS documentation", "Official upstream documentation", "menu_book", "url", "https://duxlabs.dev/docs/"),
            row("arch-wiki", "Arch Wiki", "Official Arch Linux knowledge base", "menu_book", "url", "https://wiki.archlinux.org/")
        ],
        tools: [
            row("screenshot", "Screenshot", "Select an area to capture", "screenshot", "action", "screenshot", "print screen capture"),
            row("recording", "Screen Recording", "Start or stop a selected-area recording", "videocam", "action", "recording", "video capture"),
            row("emoji", "Emoji Picker", "Search and copy an emoji", "mood", "emoji", "", "symbols smileys"),
            row("clipboard", "Clipboard History", "Recent clipboard entries", "content_paste", "clipboard", "", "copy paste")
        ],
        appearance: [
            row("wallpaper", "Wallpaper", "Choose a desktop background", "wallpaper", "settings", "wallpaper"),
            row("theme", "Theme and appearance", "Colors, fonts and motion", "palette", "settings", "personalization"),
            row("window-visuals", "Window visual preferences", "Gaps, rounding and borders", "window", "settings", "compositor_layout")
        ],
        configure: [
            row("display", "Display", "Resolution and scaling", "monitor", "settings", "displays", "screen monitor"),
            row("network", "Network and Bluetooth", "Wi-Fi, wired networks and Bluetooth", "wifi", "category", "network", "wifi wireless internet bluetooth"),
            row("sound", "Sound", "Volume, output and input", "volume_up", "control", "audioOutput", "audio microphone speaker"),
            row("input", "Keyboard and Mouse", "Shortcuts and input preferences", "keyboard", "category", "input", "keybinds touchpad"),
            row("power-management", "Power management", "Battery and performance profile", "battery_charging_full", "control", "battery", "battery energy")
        ],
        network: [
            row("wifi", "Network controls", "Wi-Fi and wired connections", "wifi", "control", "network", "wifi wireless internet"),
            row("bluetooth", "Bluetooth", "Pair and manage Bluetooth devices", "bluetooth", "control", "bluetooth")
        ],
        input: [
            row("shortcuts", "Keyboard Shortcuts", "View, capture and edit active bindings", "keyboard", "shortcuts", "", "keys hotkeys"),
            row("input-preferences", "Keyboard and mouse preferences", "Layout, pointer and touchpad", "mouse", "settings", "input")
        ],
        software: [
            row("install", "Install applications", "Find and install trusted repository packages", "download", "action", "install"),
            row("remove", "Remove applications", "Review a package removal", "delete", "action", "remove"),
            row("update", "Update system", "Review and apply a full system update", "system_update", "action", "update", "software upgrade")
        ],
        about: [
            row("about", "About Wilsof OS", "Made with purpose. Built with curiosity.", "info", "about", ""),
            row("system", "System information", "Real installed system information", "memory", "action", "system"),
            row("credits", "Open-source credits and licenses", "Component attribution and installed license notices", "copyright", "about", "credits")
        ],
        power: [
            row("lock", "Lock", "Secure the current session", "lock", "lock", ""),
            row("logout", "Log out", "End this desktop session", "logout", "power", "logout"),
            row("restart", "Restart", "Restart the computer", "restart_alt", "power", "reboot"),
            row("shutdown", "Shut down", "Power off the computer", "power_settings_new", "power", "poweroff")
        ]
    };
    return category ? (pages[category] || []) : defaults();
}
function commands(query) {
    const q = (query || "").trim().toLowerCase();
    const all = [], seen = {};
    for (const category of ["apps", "learn", "tools", "appearance", "configure", "network", "input", "software", "about", "power"]) {
        for (const item of page(category)) {
            if (!seen[item.id]) { seen[item.id] = true; all.push(item); }
        }
    }
    return all.filter(r => (r.name + " " + r.comment + " " + r.keywords + " " + r.data).toLowerCase().includes(q));
}
function emojis(query) {
    const items = [["😀","Grinning face"],["🙂","Slightly smiling face"],["😊","Smiling face"],["😂","Face with tears of joy"],["😍","Heart eyes"],["🥰","Smiling face with hearts"],["😎","Cool sunglasses"],["🤔","Thinking face"],["😴","Sleeping face"],["😢","Crying face"],["😭","Loudly crying face"],["😡","Angry face"],["👍","Thumbs up"],["👎","Thumbs down"],["👏","Clapping hands"],["🙌","Raised hands"],["🙏","Folded hands thanks"],["👋","Waving hand"],["❤️","Red heart"],["💙","Blue heart"],["💚","Green heart"],["💜","Purple heart"],["✨","Sparkles"],["⭐","Star"],["🔥","Fire"],["🎉","Party popper celebration"],["🎂","Birthday cake"],["🎁","Gift"],["☕","Coffee"],["🍕","Pizza"],["🌍","Earth globe"],["🌞","Sun"],["🌙","Moon"],["🌈","Rainbow"],["🌻","Sunflower"],["🐱","Cat"],["🐶","Dog"],["💻","Laptop computer"],["🚀","Rocket"],["✅","Check mark"],["❌","Cross mark"],["⚠️","Warning"]];
    const q = (query || "").trim().toLowerCase();
    return items.filter(e => (e[0]+" "+e[1]).toLowerCase().includes(q)).map(e => row("emoji:"+e[0],e[1],e[0]+" · copy to clipboard","mood","copy",e[0]));
}
function available(row, capabilities) {
    return !capabilities || capabilities[row.id] !== false;
}
function search(query, applications, capabilities) {
    const q = (query || "").trim().toLowerCase();
    const shortcuts = {firefox:"browser", "com.mitchellh.ghostty":"terminal", "org.gnome.Nautilus":"files"};
    const actions = commands(q).filter(r => available(r, capabilities));
    const ids = {};
    for (const item of actions) ids[item.id] = true;
    const apps = (applications || []).filter(r => !ids[shortcuts[r.data.id]]);
    function score(r) {
        const name = r.name.toLowerCase(), id = r.id.toLowerCase(), data = typeof r.data === "string" ? r.data.toLowerCase() : "";
        if (name === q) return 0;
        if (id === q || data === q) return 1;
        if (name.startsWith(q)) return 2;
        if (name.includes(q)) return 3;
        return 4;
    }
    return actions.concat(apps).filter(r => available(r, capabilities)).sort((a,b) => score(a) - score(b) || a.name.localeCompare(b.name));
}
function enter(state, category) {
    const saved = {category:state.category, query:state.query, selectedId:state.selectedId, scrollY:state.scrollY};
    return {category:category, query:"", selectedId:"", scrollY:0, stack:state.stack.concat([saved])};
}
function back(state) {
    if (!state.stack.length) return null;
    const saved = state.stack[state.stack.length - 1];
    return {category:saved.category, query:saved.query, selectedId:saved.selectedId,
        scrollY:saved.scrollY, stack:state.stack.slice(0, -1)};
}
function keyAction(key, editing, modified) {
    if (modified) return "edit";
    if (key === "Down") return "next";
    if (key === "Up") return "previous";
    if (key === "Return" || key === "Enter") return "activate";
    if (key === "Escape") return "escape";
    if (!editing && (key === "Backspace" || key === "Left")) return "back";
    if (!editing && key === "Right") return "forward";
    return "edit";
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
