// Native compositor observations only. No public IPC can supply an unlock.
function fresh() {
    return {epoch:"", seq:-1, known:false, locked:true, pending:"", armed:false, ready:false, secured:false, fault:false};
}
function bad(s) { return Object.assign({}, s, {known:false, ready:false, fault:true}); }
function allowed(s) { return s.known && !s.fault && !s.locked && !s.pending; }
function prepare(s, token) {
    if (!/^[a-f0-9]{32}$/.test(token)) return bad(s);
    return Object.assign({}, s, {pending:token, armed:false, ready:false, secured:false});
}
function receive(s, m, expected) {
    if (!m || m.epoch !== expected) return s; // An old process cannot release a new engine.
    if (s.fault || !Number.isInteger(m.seq) || m.seq < 0) return bad(s);
    if (m.kind === "snapshot") {
        if (s.known || s.epoch || typeof m.locked !== "boolean" || typeof m.guardBusy !== "boolean" || !/^[a-f0-9]{64}$/.test(m.key)) return bad(s);
        return Object.assign({}, s, {epoch:expected, seq:m.seq, known:true, locked:m.locked,
            key:m.key, pending:m.guardBusy ? "recovery" : s.pending, secured:m.locked});
    }
    if (!s.known || s.epoch !== expected) return bad(s);
    if (m.kind === "barrier") {
        if (m.token !== s.pending) return s;
        if (m.seq !== s.seq || m.locked !== s.locked) return bad(s);
        return Object.assign({}, s, {armed:true, ready:!s.locked, secured:s.locked});
    }
    if (m.kind === "quiescent") {
        if (m.seq !== s.seq || s.locked) return bad(s);
        return s.pending === "recovery" ? Object.assign({}, s, {pending:"", secured:false}) : s;
    }
    if (m.kind === "pulse") return m.seq === s.seq ? s : bad(s);
    if (m.seq !== s.seq + 1) return bad(s);
    if (m.kind === "locked" && !s.locked)
        return Object.assign({}, s, {seq:m.seq, locked:true, ready:false,
            secured:s.armed || s.pending === "recovery"});
    if (m.kind === "unlocked" && s.locked)
        return Object.assign({}, s, {seq:m.seq, locked:false,
            pending:s.secured ? "" : s.pending, armed:false, ready:false, secured:false});
    return bad(s);
}
