-- Seeded once. Personal edits here survive wilsof-config-update.
-- DMS already supplies the terminal shortcut; add only the missing app keys.
hl.unbind("SUPER + B")
hl.bind("SUPER + B", hl.dsp.exec_cmd("firefox"))
hl.unbind("SUPER + E")
hl.bind("SUPER + E", hl.dsp.exec_cmd("nautilus"))
