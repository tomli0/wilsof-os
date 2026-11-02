"""Conditional, in-memory specification. NO production/native/IPC adapter.

All calls are serialized. Tokens and acknowledgements are trusted typed inputs,
not authentication. A native implementation must establish their provenance.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    session: str
    authority: int
    generation: int


class Protocol:
    def __init__(self, session="boot/logind/compositor"):
        self.token = Token(session, 1, 0)
        self.ui_epoch = 1
        self.ui_online = True
        self.connected = True
        self.synced = False
        self.sequence = -1
        self.state = "UNKNOWN"
        self.pending = False
        self.ack = None
        self.physical = None
        self.physical_secured = False

    def _current(self, token):
        return token == self.token

    def baseline_idle(self, token, sequence):
        """ASSUMED causal idle fence, NOT DMS false or an arbitrary IPC reply."""
        if (not self._current(token) or not self.connected or self.pending
                or self.state != "UNKNOWN" or type(sequence) is not int
                or sequence < 0):
            return False
        self.sequence = sequence
        self.synced = True
        self.physical = None
        self.physical_secured = False
        self.state = "IDLE"
        return True

    def begin(self):
        """Every intent supersedes old permits/acks, including an immediate relock."""
        self.token = Token(self.token.session, self.token.authority,
                           self.token.generation + 1)
        self.ack = None
        self.pending = True
        self.state = "PREPARING"
        return self.token

    def ack_closed(self, token, ui_epoch, closed=True, disabled=True):
        """Trusted UI promises all grabs/input/lazy opens quiesced, not close()."""
        if (not self._current(token) or ui_epoch != self.ui_epoch
                or not self.ui_online or not self.connected
                or closed is not True or disabled is not True):
            return False
        self.ack = (token, ui_epoch)
        return True

    def start(self, token):
        """Only models permission to launch: never starts a real locker."""
        if (not self._current(token) or not self.connected or not self.synced
                or not self.ui_online or self.ack != (token, self.ui_epoch)
                or self.state != "PREPARING" or self.physical is not None):
            return False
        self.physical = token
        self.physical_secured = False
        self.state = "WAIT_LOCKED"
        return True

    def event(self, kind, token, sequence):
        """ASSUMED authority binds generation at origin, never at receipt.

        Sequence is contiguous within an authority incarnation. A delayed event
        can drain an old physical slot, but cannot release a newer intent.
        """
        if (not self.connected or not self.synced
                or token.session != self.token.session
                or token.authority != self.token.authority):
            return False
        if type(sequence) is not int or sequence != self.sequence + 1:
            self._quarantine()
            return False
        self.sequence = sequence
        if token.generation > self.token.generation or kind not in ("locked", "released"):
            self._quarantine()
            return False
        if token != self.physical:
            if token.generation < self.token.generation:
                return False
            self._quarantine()
            return False
        if kind == "locked":
            if self.physical_secured:
                self._quarantine()
                return False
            self.physical_secured = True
            if self._current(token):
                self.state = "LOCKED"
            return True
        if not self.physical_secured:
            self._quarantine()
            return False
        self.physical = None
        self.physical_secured = False
        if self._current(token):
            self.pending = False
            self.state = "IDLE"
        return True

    def _quarantine(self):
        self.state = "UNKNOWN"
        self.synced = False
        self.ack = None

    def locker_exit(self, code):
        """Every status, including zero, is deliberately non-authoritative."""
        return False

    def boolean_notification(self, locked):
        """Legacy DMS booleans never grant access or establish a baseline."""
        return False

    def ui_restart(self):
        self.ui_epoch += 1
        self.ack = None
        self.ui_online = True

    def disconnect(self):
        self.connected = False
        self.ui_online = False
        self._quarantine()

    def reconnect(self):
        """New observer incarnation invalidates all previous messages and acks."""
        self.token = Token(self.token.session, self.token.authority + 1,
                           self.token.generation + 1)
        self.ui_epoch += 1
        self.connected = True
        self.ui_online = True
        self.sequence = -1
        self._quarantine()

    def change_session(self, session):
        self.reconnect()
        self.token = Token(session, self.token.authority, self.token.generation)
        self.pending = False
        self.physical = None
        self.physical_secured = False

    def can_open(self):
        return (self.state == "IDLE" and self.synced and self.connected
                and self.ui_online and not self.pending and self.physical is None
                and self.ack == (self.token, self.ui_epoch))

    def open_request(self):
        return self.can_open()
