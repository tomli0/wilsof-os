.pragma library

// Qt's public key/modifier enums, kept pure for deterministic regression tests.
function combination(key, modifiers) {
    if (key === 16777216) return "cancel";
    const names = {32:"space",16777217:"TAB",16777218:"TAB",16777220:"RETURN",16777221:"RETURN",16777225:"Print",16777234:"left",16777235:"up",16777236:"right",16777237:"down"};
    let name = names[key];
    if (!name && key >= 65 && key <= 90) name = String.fromCharCode(key);
    if (!name && key >= 48 && key <= 57) name = String.fromCharCode(key);
    if (!name && key >= 16777264 && key <= 16777275) name = "F" + (key - 16777263);
    if (!name) return null;
    const parts = [];
    if (modifiers & 0x10000000) parts.push("SUPER");
    if (modifiers & 0x04000000) parts.push("CTRL");
    if (modifiers & 0x08000000) parts.push("ALT");
    if (modifiers & 0x02000000) parts.push("SHIFT");
    return parts.concat([name]).join(" + ");
}
