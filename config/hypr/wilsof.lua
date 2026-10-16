-- Wilsof overrides for the DMS-generated Hyprland Lua configuration.
-- Load this after DMS modules so Wilsof owns its visual direction and entrypoints.

local wilsof_bin = os.getenv("HOME") .. "/.local/bin/"

hl.config({
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

-- This is deliberately registered after DMS's default binds.
hl.bind("SUPER + space", hl.dsp.exec_cmd(wilsof_bin .. "wilsof-search toggle"))
hl.bind("SUPER + L", hl.dsp.exec_cmd(wilsof_bin .. "wilsof-lock"))
