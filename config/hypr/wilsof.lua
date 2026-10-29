-- Wilsof overrides for the DMS-generated Hyprland Lua configuration.
-- Load this after DMS modules: generated DMS files remain untouched.

local wilsof_home = os.getenv("HOME")
local wilsof_bin = wilsof_home .. "/.local/bin/"
local vm_test_enabled = wilsof_home .. "/.config/hypr/wilsof-vm-test-enabled.lua"

hl.config({
    -- Wilsof owns onboarding/help; the optional upstream news window is not
    -- part of this desktop and crashes on the tested software-buffer path.
    ecosystem = { no_update_news = true },
    input = {
        kb_layout = "no",
        follow_mouse = 1,
    },
    general = {
        gaps_in = 8,
        gaps_out = 10,
        border_size = 1,
        col = {
            active_border = "rgb(86b9ce)",
            inactive_border = "rgb(3a424b)",
        },
    },
    decoration = {
        rounding = 6,
        active_opacity = 1.0,
        inactive_opacity = 0.96,
        shadow = { enabled = false },
    },
})

-- Start only the Wilsof target, after DMS's own graphical-session integration.
hl.on("hyprland.start", function()
    hl.exec_cmd("systemctl --user start wilsof-session.target")
end)

-- Remove only generated DMS binds that conflict with Wilsof's documented map.
-- `hl.unbind` is case-sensitive and removes all earlier registrations of each key.
local wilsof_keys = {
    "SUPER + space", "SUPER + L", "SUPER + I", "SUPER + Q", "SUPER + F", "SUPER + F1",
    "SUPER + left", "SUPER + right", "SUPER + up", "SUPER + down",
    "SUPER + SHIFT + left", "SUPER + SHIFT + right", "SUPER + SHIFT + up", "SUPER + SHIFT + down",
    "SUPER + CTRL + left", "SUPER + CTRL + right", "SUPER + CTRL + up", "SUPER + CTRL + down",
}
for workspace = 1, 9 do
    table.insert(wilsof_keys, "SUPER + " .. workspace)
    table.insert(wilsof_keys, "SUPER + SHIFT + " .. workspace)
end
for _, key in ipairs(wilsof_keys) do
    hl.unbind(key)
end

hl.bind("SUPER + space", hl.dsp.exec_cmd(wilsof_bin .. "wilsof-search toggle"))
hl.bind("SUPER + L", hl.dsp.exec_cmd(wilsof_bin .. "wilsof-lock"))
hl.bind("SUPER + I", hl.dsp.exec_cmd("dms ipc call settings open"))
hl.bind("SUPER + F1", hl.dsp.exec_cmd(wilsof_bin .. "wilsof-help"))
hl.bind("SUPER + left", hl.dsp.focus({ direction = "left" }))
hl.bind("SUPER + right", hl.dsp.focus({ direction = "right" }))
hl.bind("SUPER + up", hl.dsp.focus({ direction = "up" }))
hl.bind("SUPER + down", hl.dsp.focus({ direction = "down" }))
hl.bind("SUPER + SHIFT + left", hl.dsp.exec_cmd("hyprctl dispatch movewindow l"))
hl.bind("SUPER + SHIFT + right", hl.dsp.exec_cmd("hyprctl dispatch movewindow r"))
hl.bind("SUPER + SHIFT + up", hl.dsp.exec_cmd("hyprctl dispatch movewindow u"))
hl.bind("SUPER + SHIFT + down", hl.dsp.exec_cmd("hyprctl dispatch movewindow d"))
hl.bind("SUPER + CTRL + left", hl.dsp.exec_cmd("hyprctl dispatch resizeactive -40 0"))
hl.bind("SUPER + CTRL + right", hl.dsp.exec_cmd("hyprctl dispatch resizeactive 40 0"))
hl.bind("SUPER + CTRL + up", hl.dsp.exec_cmd("hyprctl dispatch resizeactive 0 -40"))
hl.bind("SUPER + CTRL + down", hl.dsp.exec_cmd("hyprctl dispatch resizeactive 0 40"))
hl.bind("SUPER + Q", hl.dsp.window.close())
hl.bind("SUPER + F", hl.dsp.exec_cmd("hyprctl dispatch fullscreen"))
hl.bind("SUPER + SHIFT + space", hl.dsp.window.float({ action = "toggle" }))

for workspace = 1, 9 do
    hl.bind("SUPER + " .. workspace, hl.dsp.focus({ workspace = workspace }))
    hl.bind("SUPER + SHIFT + " .. workspace, hl.dsp.window.move({ workspace = workspace }))
end

-- Deliberately opt-in: useful only when a VM client intercepts Super.
local vm_test_file = io.open(vm_test_enabled, "r")
if vm_test_file then
    vm_test_file:close()
    require("wilsof-vm-test-enabled")
end
