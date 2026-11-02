# AS-02 Phase 1 transition diagram

Conditional model only. Native authority envelopes and UI quiescence are NOT implemented.

    process/session/observer start
                 |
                 v
             UNKNOWN [DENY] <--------------------------+
                 |                                    |
       trusted causal idle fence                      | gap / bad ordering /
       + current UI closed/disabled ACK               | disconnect / unknown origin
                 v                                    |
              IDLE [ALLOW only with current ACK]       |
                 | begin(g+1): invalidate ACK, DENY    |
                 v                                    |
          PREPARING [DENY] ----------------------------+
                 |
       current-session/generation/UI-incarnation ACK
       + synchronized live authority + no occupied slot
                 v
       WAIT_LOCKED [DENY; model start permission ONLY]
                 |
       origin-bound secured(g, next sequence)
                 v
             LOCKED [DENY]
                 |
       origin-bound released(g, next sequence)
                 v
              IDLE [ALLOW only with current ACK]

    begin B while physical A active:
      PREPARING B [DENY; cannot start a second locker]
      release A drains A only, remains PREPARING B [DENY]
      fresh B ACK + empty slot -> WAIT_LOCKED B -> LOCKED B
      release B -> IDLE

    wrong password / any exit code / DMS boolean false:
      no release transition

    UI restart:
      invalidate ACK; DENY until new UI ACK and authoritative IDLE

    IPC/observer disconnect during pending lock:
      UNKNOWN [DENY]; old messages invalid after incarnation change
      pending recovery unsupported -> remain denied, no guessed unlock

NATIVE GAP (not an edge implemented by this prototype):
  start permission -> UI restart -> real password activation
  Returned permission is not revocable here; no activation handshake is modeled.
  Likewise external lock activation can precede any observed notification.

No transition arrow asserts PAM success. Compositor release and PAM acceptance
are separate evidence. See ADR.md for trust boundaries and production NO-GO.
