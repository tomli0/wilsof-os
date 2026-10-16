-- Optional VM-only fallback bindings for clients that intercept Super.
-- This file is loaded only when wilsof-vm-test-binds enable creates the enabled copy.

local wilsof_bin = os.getenv("HOME") .. "/.local/bin/"
local vm_test_keys = {
    "CTRL + ALT + space",
    "CTRL + ALT + L",
    "CTRL + ALT + I",
    "CTRL + ALT + F1",
}

for _, key in ipairs(vm_test_keys) do
    hl.unbind(key)
end

hl.bind("CTRL + ALT + space", hl.dsp.exec_cmd(wilsof_bin .. "wilsof-search toggle"))
hl.bind("CTRL + ALT + L", hl.dsp.exec_cmd(wilsof_bin .. "wilsof-lock"))
hl.bind("CTRL + ALT + I", hl.dsp.exec_cmd("dms ipc call settings open"))
hl.bind("CTRL + ALT + F1", hl.dsp.exec_cmd(wilsof_bin .. "wilsof-help"))
