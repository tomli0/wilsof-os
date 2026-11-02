"""Run with Python; output is a MODEL TRACE, never native lock evidence."""
import json
from protocol import Protocol


def main():
    p = Protocol()
    p.baseline_idle(p.token, 0)
    p.ack_closed(p.token, p.ui_epoch)
    rows = [{"event": "trusted hypothetical idle baseline", "open": p.can_open()}]
    a = p.begin()
    rows.append({"event": "begin A before UI ack", "start": p.start(a), "open": p.can_open()})
    p.ack_closed(a, p.ui_epoch)
    p.start(a)
    p.event("locked", a, 1)
    b = p.begin()
    p.ack_closed(b, p.ui_epoch)
    rows.append({"event": "begin B while A still owns native slot", "start": p.start(b), "open": p.can_open()})
    p.event("released", a, 2)
    rows.append({"event": "delayed release A", "open": p.can_open()})
    p.start(b)
    p.event("locked", b, 3)
    p.event("released", b, 4)
    rows.append({"event": "hypothetical origin-bound release B", "open": p.can_open()})
    print(json.dumps({"scope": "conditional in-memory model, production blocked", "trace": rows}, indent=2))


if __name__ == "__main__":
    main()
