"""Deliberately unsafe negative control, NOT production code or a native adapter."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Token:
    session: str
    authority: int
    generation: int

class LegacyBoolean:
    def __init__(self, session="boot/logind/compositor"):
        self.token = Token(session, 1, 0)
        self.ui_epoch = 1
        self.allowed = False

    def baseline_idle(self, token, sequence):
        self.allowed = True
        return True

    def begin(self):
        self.token = Token(self.token.session, self.token.authority, self.token.generation + 1)
        self.allowed = False
        return self.token

    def ack_closed(self, token, ui_epoch, closed=True, disabled=True):
        return True

    def start(self, token):
        return True

    def event(self, kind, token, sequence):
        if kind in ("locked", "released"):
            self.allowed = kind == "released"
        return True

    def can_open(self):
        return self.allowed
